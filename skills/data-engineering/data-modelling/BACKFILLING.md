# Backfilling and Healing SCD2 History (Snowflake)

Use this to build an SCD2 dimension's history deterministically from full
source. It isn't only for disaster recovery — three uses:

* **A one-off backfill** or reconstruction of a dimension's history.
* **The main build** for batch dimensions, when the preconditions below hold.
* **A scheduled heal** alongside daily incremental loads
  ([SCD2.md](./SCD2.md)): weekly or monthly, rebuild from source and diff
  against the incremental table — any difference is drift to investigate
  before you publish the healed version. A heal also picks up retroactive
  source corrections, backfills a new attribute across every version, and
  places back-dated changes that close-and-insert can't.

## Why not just replay day by day

Day-by-day SCD2 backfills **compound errors**: a miss on Jan 3 becomes the
baseline for Jan 4, and you can't fix one day without redoing every day built
on it. The fix is a **path-independent** rebuild — a *Healing Table* — that
separates *change detection* from *period construction* and rebuilds the whole
timeline from source. The result depends only on source data, not on load
history; fix the logic, reprocess the range, and the dimension "heals."

**Preconditions** — check each before relying on it:

* **Complete source history.** If the source doesn't keep it, start a
  persistent staging area now that keeps every extract, partitioned by fetch
  date.
* **No hard deletes.** The method assumes deletions are flagged. If the source
  physically removes rows, capture the deletes first (CDC tombstones or
  snapshot diffs), or that history is lost.
* **Contiguous presence.** If an entity can disappear and reappear, close its
  interval when it's absent from a full snapshot — otherwise `LEAD()` silently
  stretches the last version across the gap.
* **Acceptable rebuild time.** Otherwise stay incremental — also the right call
  for real-time, or when no history exists.

## The six steps (Snowflake)

1. **Effectivity table** — extract every actual change point from source;
   filter out non-changes with null-safe comparison
   (`prev IS DISTINCT FROM curr`).
2. **Time slices** — `LEAD()` over the change points to derive
   `VALID_FROM`/`VALID_TO` (left-closed/right-open).
3. **Join sources** — build a unified timeline; as-of join each source and
   **document attribute ownership** (which source wins per column).
4. **Hash** — a key-hash for identity and a row-hash for change detection;
   `COALESCE` NULLs to a sentinel so `NULL` ≠ `''`.
5. **Compress** — collapse consecutive identical states (islands-and-gaps),
   only where temporally contiguous **and** row-hash-equal.
6. **Validate** — the temporal-integrity tests from
   [SCD2.md](./SCD2.md) before publish.

[HEALING-TABLE-TEMPLATE.md](./HEALING-TABLE-TEMPLATE.md) has tool-agnostic
pseudo-SQL for all six steps — swap in the Snowflake functions below.

### Snowflake building blocks

```sql
-- Step 1+2: change points → time slices
WITH ranked AS (
  SELECT CUSTOMER_BK, REGION, NAME, EFFECTIVE_TS,
         LAG(REGION) OVER (PARTITION BY CUSTOMER_BK ORDER BY EFFECTIVE_TS) AS prev_region,
         LAG(NAME)   OVER (PARTITION BY CUSTOMER_BK ORDER BY EFFECTIVE_TS) AS prev_name
  FROM SRC_CUSTOMER_HISTORY
),
changes AS (
  SELECT * FROM ranked
  WHERE prev_region IS DISTINCT FROM REGION
     OR prev_name   IS DISTINCT FROM NAME
     OR prev_region IS NULL                 -- first row per key
)
SELECT CUSTOMER_BK, REGION, NAME,
       EFFECTIVE_TS AS VALID_FROM,
       COALESCE(
         LEAD(EFFECTIVE_TS) OVER (PARTITION BY CUSTOMER_BK ORDER BY EFFECTIVE_TS),
         '9999-12-31'::TIMESTAMP_NTZ
       ) AS VALID_TO
FROM changes;
```

## Test harness — zero-copy clone

Never rebuild a production HST table in place on the first attempt. Snowflake
**zero-copy cloning** gives you a full-size, isolated copy in seconds at no
storage cost until you diverge:

```sql
CREATE TABLE PROD_DB.HST.DIM_CUSTOMER_HST_BACKFILL_TEST
  CLONE PROD_DB.HST.DIM_CUSTOMER_HST;
-- or clone the whole schema for a wider rehearsal:
CREATE SCHEMA PROD_DB.HST_BACKFILL_TEST CLONE PROD_DB.HST;
```

Rebuild into the clone, run the validation suite, diff against the live table,
then swap (`ALTER TABLE ... SWAP WITH`) or re-point. Drop the clone when done.

## Two-step RAW → HST staging

Stage the rebuilt timeline in a RAW landing table first, validate it there,
then promote to HST. This keeps a broken rebuild out of the published table
and gives you an inspectable artifact:

1. `RAW.DIM_CUSTOMER_BACKFILL` — output of steps 1–5 run over the landed
   history (below), untrusted.
2. Run validation (step 6) against RAW.
3. On pass, `INSERT`/`SWAP` into `HST.DIM_CUSTOMER_HST`.

## Partition-level loads with COPY INTO

For large historical source in object storage, land the raw history in
**month-level partitions** rather than one monolithic file — it bounds memory,
makes failures re-runnable per partition, and parallelises:

```sql
COPY INTO RAW.CUSTOMER_HISTORY_LANDING
FROM @HISTORY_STAGE/customer/history/year=2024/month=03/
FILE_FORMAT = (TYPE = PARQUET)
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
ON_ERROR = ABORT_STATEMENT;
```

Loop the months, check each landed partition's row counts against the
profiling baseline, and keep the landing idempotent (truncate-and-reload the
partition) so a re-run is safe.

**Partition the landing, not the logic.** Steps 1–5 read the landing table and
run over each key's *whole* history in one pass. Windowing them by month cuts
`LAG`/`LEAD` at every boundary: each month gets a fake first version and an
open last one, so you get overlaps and several current rows. If the work must
be split, split by business key, never by time. And if you dedupe the output,
dedupe on (key-hash, `VALID_FROM`) — the key-hash alone is one row per entity,
so deduping on it deletes the history.

## Checklist

* Rebuilt into a **zero-copy clone**, never live, on the first pass.
* Staged through **RAW**, validated, then promoted to HST.
* Raw history **landed** by partition (e.g. month) with per-partition
  row-count checks; steps 1–5 run over each key's full history, never per month.
* Preconditions checked: complete history, deletes captured, gaps in presence
  closed.
* All six Healing-Table steps applied; result is path-independent.
* Full [SCD2.md](./SCD2.md) temporal-integrity suite passes before publish.
* Load is idempotent — a re-run produces an identical table.
