# SQL Tuning — Cloud / MPP Warehouses (Snowflake, BigQuery, Redshift, Databricks SQL)

For columnar, massively-parallel, decoupled-storage warehouses. The mental
model is different from an OLTP RDBMS: there are **no traditional indexes**,
you don't tune locks, and compute is elastic and **billed by time or bytes**.
The levers are **pruning** (scan less data), **clustering/partitioning**,
**right-sizing compute**, and **not re-computing** what you can materialise or
cache. "Faster" and "cheaper" are usually the same fix here — less data
scanned.

## Contents
1. Get the profile / plan
2. The universal goal: prune more, scan less
3. Snowflake specifics
4. BigQuery specifics
5. Redshift specifics
6. Databricks SQL / Photon specifics
7. Cross-warehouse fixes
8. Cost = performance

---

## 1. Get the profile / plan

- **Snowflake**: Query Profile in Snowsight (the graphical operator tree) —
  look at *Partitions scanned vs total*, *Bytes spilled to local/remote
  storage*, and the % time in each operator. `QUERY_HISTORY` /
  `SNOWFLAKE.ACCOUNT_USAGE` for trends; `SYSTEM$EXPLAIN_PLAN_JSON` /
  `EXPLAIN USING TABULAR`.
- **BigQuery**: the Execution Details / query plan tabs (per-stage
  records in/out, wait/read/compute/write ms, *shuffle bytes*, *slot ms*).
  `INFORMATION_SCHEMA.JOBS` for bytes billed and slot consumption.
- **Redshift**: `EXPLAIN`; then `SVL_QUERY_REPORT`, `SVL_QUERY_SUMMARY`,
  `STL_ALERT_EVENT_LOG` (flags missing stats, nested loops, large
  distributions), `SYS_QUERY_HISTORY` (RA3/serverless).
- **Databricks SQL**: the Spark UI / Query Profile; look for file pruning,
  shuffle, and spill (see also the Spark reference).

Read the profile for the same red flags as any engine: **scanned ≫ returned**,
**spill**, **skew**, **exploding joins**, **stale stats**.

## 2. The universal goal: prune more, scan less

Columnar warehouses bill and slow down by **data scanned**. Everything below
is in service of scanning fewer micro-partitions/blocks and fewer columns.

- **Filter on the partition/cluster key, unwrapped.** `WHERE event_date >= …`
  prunes; `WHERE CAST(event_ts AS DATE) = …` or `WHERE func(col)=…` often
  doesn't. Keep the column bare on the left side of the predicate.
- **Project narrow.** Never `SELECT *` from a wide columnar table — each column
  is separate I/O. Select only what you need.
- **Filter before join/aggregate**, and push predicates into subqueries/CTEs so
  they prune at the scan, not after a full materialisation.
- **Materialise expensive intermediate layers** instead of chaining views; a
  view re-runs its whole definition every time it's referenced.

## 3. Snowflake specifics

- **Micro-partitions** are automatic; you influence pruning via a **clustering
  key** on large tables (>~1TB or with poor natural ordering). Check
  `SYSTEM$CLUSTERING_INFORMATION('table','(col)')` for overlap/depth before and
  after. Cluster on the column(s) you filter/join on most, low-to-moderate
  cardinality, 1–2 columns ideally.
- **Spilling**: "Bytes spilled to local storage" (and worse, remote) in the
  profile means the warehouse is too small for the working set — size up the
  warehouse *for that query* or reduce the working set. Spill to **remote** is
  a strong size-up signal.
- **Warehouse sizing**: each size up roughly doubles credits/hour *and* compute.
  Size up only if the query is compute-bound or spilling, not if it's pruning-
  bound (a bigger warehouse won't fix a full scan). Use multi-cluster for
  concurrency, not for single-query speed.
- **Result cache** (24h, exact-match) and **warehouse/local disk cache**: avoid
  defeating them with `CURRENT_TIMESTAMP`/nondeterministic functions in the
  query, and keep the warehouse warm for repeated workloads.
- **Search Optimization Service** for selective point-lookups on big tables;
  **materialized views** for frequently-hit aggregates (note maintenance cost).
- **Query acceleration service** for scan-heavy outliers.
- Avoid exploding joins: Snowflake won't save you from a non-unique key.

## 4. BigQuery specifics

- **Partitioning** (by date/ingestion-time or integer range) + **clustering**
  (up to 4 columns) is the core pruning lever. Always filter on the partition
  column to hit *partition pruning*; check "bytes processed" in the dry-run
  before running.
- **Avoid `SELECT *`** — BigQuery bills by columns scanned (on-demand). Select
  named columns; the column count directly moves the bill.
- **Dry run** (`--dry_run` / `jobs.query` `dryRun`) to see bytes billed before
  committing spend.
- **Slots**: on-demand vs reservations. A stage stuck on "wait" = slot
  contention; "shuffle bytes" high = repartition/skew. Address skew by
  filtering nulls/hot keys or pre-aggregating.
- **Broadcast vs hash join**: keep the small side small so BigQuery broadcasts
  it; avoid cross joins and unintended fan-out.
- Materialized views and `BI Engine` for repeated dashboard queries; partition
  expiration to keep tables lean.
- Beware `JOIN` on `STRING` keys vs clustered `INT64` — clustering only prunes
  if you filter/join on the clustered columns in order.

## 5. Redshift specifics

- **Distribution style** is the big lever: `DISTKEY` on the common join key so
  matching rows colocate (avoids redistribution); `DISTSTYLE ALL` for small
  dimensions; `EVEN` when there's no good key. A wrong DISTKEY = broadcast/
  redistribute on every join (`DS_BCAST_INNER` / `DS_DIST_BOTH` in the plan —
  red flags).
- **SORTKEY** (compound or interleaved) acts like the pruning/zone-map key —
  sort on the column you range-filter on. Check `SVV_TABLE_INFO` for
  `unsorted` %.
- **`VACUUM`** to reclaim/re-sort after big deletes/loads, and **`ANALYZE`** to
  refresh stats — stale stats cause nested-loop disasters (watch
  `STL_ALERT_EVENT_LOG`).
- **WLM / concurrency scaling / queues**: queue wait time shows as queue delay,
  not execution — separate the two when baselining.
- RA3 / serverless changes some of this (managed storage, auto), but
  DIST/SORT/ANALYZE discipline still pays.

## 6. Databricks SQL / Photon specifics

- **File/data skipping** via Delta stats + **`OPTIMIZE`** (compaction) and
  **`ZORDER BY`** the columns you filter on; `OPTIMIZE … ZORDER` is the
  clustering analogue. Liquid clustering where available.
- Small-file problem: many tiny files = slow scans; compact with `OPTIMIZE`.
- Photon acceleration for scan/aggregate-heavy SQL; check the query profile for
  Photon coverage.
- Underlying engine is Spark — for shuffle/skew/spill, also read the Spark
  reference.

## 7. Cross-warehouse fixes

- **Incremental, not full-refresh.** Process only new/changed partitions
  (dbt incremental + merge). Volume growth then stops inflating runtime.
- **Pre-aggregate** frequently-hit rollups into summary tables / materialized
  views rather than re-scanning raw every time.
- **Right-size the model graph**: keep core models lean, push heavy enrichment
  downstream so dozens of consumers don't wait on it.
- **Don't fix a scan problem with bigger compute.** A full scan or skew costs
  the same proportion of a bigger warehouse — fix pruning/skew first, *then*
  size for the genuinely compute-bound remainder.
- **Cache-friendliness**: deterministic queries reuse result caches; warm pools
  for repeated batch.

## 8. Cost = performance

In these engines the bill is the cleanest performance metric you have.

- Baseline in **bytes scanned / slot-ms / credits**, not just wall-clock.
- Snowflake: `ACCOUNT_USAGE.QUERY_HISTORY` (credits, spill, partitions scanned)
  → find the top-cost queries; they're usually the top-slow ones.
- BigQuery: `INFORMATION_SCHEMA.JOBS` by `total_bytes_billed` / `total_slot_ms`.
- Redshift: `SYS_QUERY_HISTORY` / `SVL_QUERY_SUMMARY` by scan and exec time.
- Set a **budget alert** on the dominant workload and a runtime budget on the
  DAG, the same way you'd alert on failure. Catch the slow/expensive creep
  early.

**Always**: read the profile → confirm it's a pruning problem vs a compute
problem → fix the data layout/predicate → re-measure bytes *and* time against
the baseline before sizing up.
