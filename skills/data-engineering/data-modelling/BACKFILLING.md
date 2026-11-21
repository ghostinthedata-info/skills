# Backfilling and Healing SCD2 History

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

## The six steps

1. **Effectivity table** — extract every actual change point from source;
   filter out non-changes with null-safe comparison
   (`prev IS DISTINCT FROM curr`).
2. **Time slices** — `LEAD()` over the change points to derive
   `valid_from`/`valid_to` (left-closed/right-open).
3. **Join sources** — union every source's change points into one timeline,
   then as-of join each source back onto it, and **document attribute
   ownership** (which source wins per column). See *Several sources* below.
4. **Hash** — a key-hash for identity and a row-hash for change detection;
   `COALESCE` NULLs to a sentinel so `NULL` ≠ `''`.
5. **Compress** — collapse consecutive identical states (islands-and-gaps),
   only where temporally contiguous **and** row-hash-equal.
6. **Validate** — the temporal-integrity tests from
   [SCD2.md](./SCD2.md) before publish.

[HEALING-TABLE-TEMPLATE.md](./HEALING-TABLE-TEMPLATE.md) has tool-agnostic
pseudo-SQL for all six steps. The building block below shows steps 1–2 for a
single source with change timestamps.

### Building block — change points to time slices

```sql
WITH ordered AS (
  SELECT customer_bk, region, customer_name, effective_ts, source_seq,
         ROW_NUMBER()          OVER w AS version_no,
         LAG(region)           OVER w AS prev_region,
         LAG(customer_name)    OVER w AS prev_name
  FROM src_customer_history
  WINDOW w AS (PARTITION BY customer_bk ORDER BY effective_ts, source_seq)
  -- source_seq (log position, ingest offset) breaks timestamp ties;
  -- without it the order — and so the result — isn't deterministic
),
changes AS (
  SELECT * FROM ordered
  WHERE version_no = 1                              -- first appearance
     OR prev_region IS DISTINCT FROM region
     OR prev_name   IS DISTINCT FROM customer_name
)
SELECT customer_bk, region, customer_name,
       effective_ts AS valid_from,
       COALESCE(
         LEAD(effective_ts) OVER (PARTITION BY customer_bk ORDER BY effective_ts, source_seq),
         TIMESTAMP '9999-12-31 00:00:00'
       ) AS valid_to
FROM changes;
```

`ROW_NUMBER() = 1` finds the first version; testing `prev_region IS NULL`
instead also fires whenever the previous value was a real NULL. If your
engine has no named `WINDOW` clause, repeat the `OVER (…)` in each column.

## Several sources

Never load several sources straight into one SCD2. Each load closes the
others' versions, and the same instant ends up with different attribute
combinations depending on which source ran first — the history becomes a
record of load order. Instead, build one timeline: union the change points
from every source, slice it once (step 2), and as-of join each source back to
take the columns it owns. Step 3 of
[HEALING-TABLE-TEMPLATE.md](./HEALING-TABLE-TEMPLATE.md) shows the shape.

## Snapshot sources

When a source only gives full snapshots (no change timestamps), derive the
change points by diffing consecutive snapshots per key: a row whose tracked
values differ from the previous snapshot's is a change at that snapshot date,
and a key that was in the previous snapshot but is missing from this one has
gone — close its interval at this snapshot's date (the *contiguous presence*
precondition). Step 1b of the template has both queries.

## Test harness — rebuild into a copy, never in place

Never rebuild a production history table in place on the first attempt.
Rebuild into an isolated copy: a zero-copy clone or snapshot if your engine
has one (Snowflake `CLONE`, BigQuery table clones, Delta `SHALLOW CLONE`),
otherwise a full copy in a scratch schema:

```sql
CREATE TABLE hst_backfill_test.dim_customer_hst AS
SELECT * FROM hst.dim_customer_hst;      -- or your engine's clone/snapshot
```

Rebuild into the copy, run the validation suite, diff against the live table,
then publish with an atomic swap, rename, or view re-point. Drop the copy when
done.

## Two-step staging — raw backfill table, then the published table

Stage the rebuilt timeline in a raw landing table first, validate it there,
then promote it to the published history table. This keeps a broken rebuild
out of the published table and gives you an inspectable artifact:

1. `raw.dim_customer_backfill` — output of steps 1–5 run over the landed
   history (below), untrusted.
2. Run validation (step 6) against the raw table.
3. On pass, replace `hst.dim_customer_hst` atomically (swap, rename, or view
   re-point).

## Land large history by partition

For large historical source in object storage, land the raw history in
**month-level partitions** rather than one monolithic load — it bounds memory,
makes failures re-runnable per partition, and parallelises. Use your engine's
bulk loader (a `COPY`/`LOAD` command, an external table, or a Spark read),
fail the partition on any rejected row, and make each partition's load
replace that partition:

```sql
-- one month at a time; re-running a month replaces it
DELETE FROM raw.customer_history_landing WHERE fetch_month = '2024-03';
INSERT INTO raw.customer_history_landing
SELECT f.*, '2024-03' AS fetch_month
FROM <files under customer/history/year=2024/month=03/> f;   -- your bulk loader
```

Loop the months and check each landed partition's row counts against the
profiling baseline.

**Partition the landing, not the logic.** Steps 1–5 read the landing table and
run over each key's *whole* history in one pass. Windowing them by month cuts
`LAG`/`LEAD` at every boundary: each month gets a fake first version and an
open last one, so you get overlaps and several current rows. If the work must
be split, split by business key, never by time. And if you dedupe the output,
dedupe on (key-hash, `valid_from`) — the key-hash alone is one row per entity,
so deduping on it deletes the history.

## Checklist

* Rebuilt into a **copy** (clone, snapshot, or scratch table), never live, on
  the first pass.
* Staged through a **raw** table, validated, then promoted to the published
  table atomically.
* Raw history **landed** by partition (e.g. month) with per-partition
  row-count checks; steps 1–5 run over each key's full history, never per month.
* Preconditions checked: complete history, deletes captured, gaps in presence
  closed.
* All six Healing-Table steps applied; result is path-independent.
* Full [SCD2.md](./SCD2.md) temporal-integrity suite passes before publish.
* Load is idempotent — a re-run produces an identical table.
