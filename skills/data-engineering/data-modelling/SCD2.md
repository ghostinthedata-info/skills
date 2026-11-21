# SCD Type 2 — History Rows (Snowflake)

Type 2 adds a new row each time a tracked attribute changes, so every
point-in-time question ("what was their region when they ordered?") has an
exact answer. It costs row growth — apply it per attribute, only where
point-in-time truth is genuinely needed. For overwrite-only attributes use
[SCD1.md](./SCD1.md).

## Shape

```sql
CREATE TABLE IF NOT EXISTS DIM_CUSTOMER_HST (
    CUSTOMER_SK     NUMBER       IDENTITY,           -- surrogate, unique per version
    CUSTOMER_BK     VARCHAR      NOT NULL,           -- durable business key
    CUSTOMER_NAME   VARCHAR,
    REGION          VARCHAR,
    VALID_FROM      TIMESTAMP_NTZ NOT NULL,
    VALID_TO        TIMESTAMP_NTZ NOT NULL DEFAULT '9999-12-31'::TIMESTAMP_NTZ,
    IS_CURRENT      BOOLEAN      NOT NULL DEFAULT TRUE,
    ROW_HASH        VARCHAR,                         -- change-detection hash
    LOAD_TS         TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()  -- audit only, never validity
);
```

### Interval convention

Use **left-closed / right-open** intervals — `VALID_FROM <= t < VALID_TO` —
so every instant maps to exactly one version with no overlap and no gap. Use
a high sentinel (`9999-12-31`) for the open end **and** an explicit
`IS_CURRENT` flag (don't rely on one alone).

## Change detection — hash, null-safe

Build a `ROW_HASH` over the tracked columns, coalescing NULLs to a sentinel
so `NULL` and `''` don't collide:

```sql
SHA2(
  ARRAY_TO_STRING(ARRAY_CONSTRUCT(
     COALESCE(CUSTOMER_NAME, '∅'),
     COALESCE(REGION,        '∅')
  ), '||'), 256
) AS ROW_HASH
```

Compare incoming `ROW_HASH` to the current row's; differ → close the old, open
the new.

## Load — close-and-insert MERGE

Take validity from the **source, never the load clock**: `VALID_FROM` is when
the change happened (the source's change timestamp, or the snapshot date for a
snapshot source). Validity stamped with `CURRENT_TIMESTAMP()` depends on when
the job ran, so it can never be reproduced — the same flaw that rules out dbt
snapshots below. The load's own time goes only in `LOAD_TS`.

Before loading, reduce the batch to **one row per key** — the latest change,
with timestamp ties broken by a deterministic source sequence (log position,
ingest offset) — or apply the batch's changes in order. Otherwise the `MERGE`
fails or opens two current rows. A **back-dated** change (older than the
current row's `VALID_FROM`) can't be placed by close-and-insert: route that
key to a heal ([BACKFILLING.md](./BACKFILLING.md)).

A single `MERGE` can't both update the expiring row and insert the new one for
the same key, so the standard Snowflake pattern is two steps: (1) `MERGE` to
**close** changed current rows, (2) `INSERT` the new versions. Wrap in a
transaction.

```sql
-- STG_CUSTOMER: one row per CUSTOMER_BK, with CHANGED_AT taken from the source
-- Step 1: expire current rows whose hash changed
MERGE INTO DIM_CUSTOMER_HST tgt
USING ( SELECT s.*, <hash expr> AS ROW_HASH FROM STG_CUSTOMER s ) src
   ON  tgt.CUSTOMER_BK = src.CUSTOMER_BK
   AND tgt.IS_CURRENT  = TRUE
WHEN MATCHED AND tgt.ROW_HASH IS DISTINCT FROM src.ROW_HASH THEN
   UPDATE SET tgt.VALID_TO   = src.CHANGED_AT,   -- closes exactly where the new version opens
              tgt.IS_CURRENT = FALSE;

-- Step 2: insert new versions (new keys + changed keys)
INSERT INTO DIM_CUSTOMER_HST
   (CUSTOMER_BK, CUSTOMER_NAME, REGION, VALID_FROM, VALID_TO, IS_CURRENT, ROW_HASH)
SELECT src.CUSTOMER_BK, src.CUSTOMER_NAME, src.REGION,
       src.CHANGED_AT, '9999-12-31'::TIMESTAMP_NTZ, TRUE, src.ROW_HASH
FROM ( SELECT s.*, <hash expr> AS ROW_HASH FROM STG_CUSTOMER s ) src
LEFT JOIN DIM_CUSTOMER_HST cur
       ON cur.CUSTOMER_BK = src.CUSTOMER_BK AND cur.IS_CURRENT = TRUE
WHERE cur.CUSTOMER_BK IS NULL                       -- brand-new key
   OR cur.ROW_HASH IS DISTINCT FROM src.ROW_HASH;   -- changed key
```

## dbt snapshots

Never use dbt **snapshots** for an SCD2 you need to trust: a snapshot records
only the state it happens to observe on each run, so its history is
path-dependent — a missed or late run is a permanent gap, and a logic fix
can't be replayed over the past. For a clean rebuild from full history, use
the Healing-Table approach in [BACKFILLING.md](./BACKFILLING.md) instead.

## Validate after every load (block on failure)

* Exactly **one current row** per durable key — count over *all* rows, so a key
  with no current row is caught too
  (`GROUP BY CUSTOMER_BK HAVING SUM(IFF(IS_CURRENT, 1, 0)) <> 1` → empty).
* The current flag agrees with the high date
  (`IS_CURRENT` exactly when `VALID_TO = '9999-12-31'`).
* `(CUSTOMER_BK, VALID_FROM)` is unique.
* **No overlapping** intervals per key (`LEAD(VALID_FROM)` ≥ `VALID_TO`).
* **No gaps** if continuity is required.
* `VALID_FROM < VALID_TO` on every row.
* No **consecutive duplicate** versions — same hash **and** contiguous
  (`VALID_FROM` = the previous `VALID_TO`). Same-hash rows with a gap between
  them are separate states, not duplicates.

## Querying point-in-time

```sql
SELECT * FROM DIM_CUSTOMER_HST
WHERE CUSTOMER_BK = :bk
  AND :as_of_ts >= VALID_FROM
  AND :as_of_ts <  VALID_TO;
```

Carry the **durable key** on facts alongside the surrogate so you can also
report all history by *current* attributes. An SCD2 dimension holds all three
key types at once — the surrogate (one per version, the FK target), the
natural/business key (lineage), and the durable "super-natural" key (joins all
versions of one entity). See [KEYS.md](./KEYS.md) for the full rules.
