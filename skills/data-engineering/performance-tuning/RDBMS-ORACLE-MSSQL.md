# SQL Tuning — Traditional Transactional RDBMS (Oracle, SQL Server)

For row-store, OLTP-oriented engines with a cost-based optimiser, B-tree
indexes, and per-row locking. The optimiser is the thing you're really
tuning: it picks the plan, and it picks well only when its **statistics** are
fresh and its **access paths** (indexes) exist. Most "slow query" problems
here are a bad plan caused by stale stats, a non-sargable predicate, or a
missing/unusable index — not raw hardware.

## Contents
1. Get the real execution plan
2. Read the plan — red flags
3. Statistics & cardinality
4. Indexing
5. Sargability (let the index work)
6. Joins
7. Locking, blocking & contention
8. Plan stability
9. Engine cheat-sheet (Oracle ↔ SQL Server)

---

## 1. Get the real execution plan

Estimated plans lie; get the **actual** plan with real row counts wherever
possible.

**Oracle**
- `EXPLAIN PLAN FOR <sql>;` then `SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);` — estimate only.
- Real execution stats: run with `/*+ GATHER_PLAN_STATISTICS */`, then
  `SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(format=>'ALLSTATS LAST'));`
  — compare **E-Rows vs A-Rows**. Big divergence = bad cardinality estimate.
- `DBMS_XPLAN.DISPLAY_AWR(sql_id)` for historical plans; AWR/ASH reports for
  system-wide waits; SQL Monitor (`DBMS_SQLTUNE.REPORT_SQL_MONITOR`) for
  long-running statements.

**SQL Server**
- `SET STATISTICS IO, TIME ON;` — logical reads + CPU/elapsed per statement.
- Actual execution plan (SSMS "Include Actual Execution Plan", or
  `SET STATISTICS XML ON`). Hover for **Estimated vs Actual Rows**.
- Query Store (SQL 2016+) for historical plans and regressions; `sys.dm_exec_query_stats`,
  `sys.dm_exec_requests`, `sys.dm_os_wait_stats` for live diagnosis.

## 2. Read the plan — red flags

- **Full/segment table scan** on a large table where a seek was expected →
  missing index, non-sargable predicate, or stats say "most rows match."
- **Index scan vs index seek** (SQL Server) — a scan reads the whole index; a
  seek navigates to rows. Scans on big tables under selective filters are suspect.
- **Estimated rows ≫/≪ actual** → stale or missing stats; the optimiser is
  flying blind and will pick wrong join orders/methods.
- **Nested loops over a large outer input** → fine for small/indexed inner,
  disastrous when the optimiser underestimated the outer set.
- **Hash match spilling to tempdb/temp** (warnings on the operator) →
  underestimated memory grant; fix the estimate, not just `work_area` size.
- **Implicit conversion** warning (SQL Server) / predicate with a cast →
  defeats the index (see §5).
- **Key lookup / table access by ROWID** repeated millions of times → covering
  index opportunity.
- **Parallelism you didn't want** (high `CXPACKET`/`CXCONSUMER` waits) → a
  serial-friendly query forced parallel, or skewed work distribution.

## 3. Statistics & cardinality

Stale stats are the single most common root cause. Refresh before you do
anything clever.

**Oracle**
- `EXEC DBMS_STATS.GATHER_TABLE_STATS('SCHEMA','TABLE', cascade=>TRUE);`
- Use `AUTO_SAMPLE_SIZE`; gather histograms on skewed columns
  (`METHOD_OPT => 'FOR COLUMNS SIZE AUTO ...'`).
- Watch for stale stats after big loads: `DBMS_STATS.GATHER_TABLE_STATS`
  post-load in your pipeline, or rely on the auto stats job only if loads are small.
- Extended stats / column groups for correlated predicates the optimiser
  otherwise treats as independent.

**SQL Server**
- `UPDATE STATISTICS schema.table WITH FULLSCAN;` (or sampled for huge tables).
- Auto-update kicks in at a row-modification threshold; large tables can go
  stale between thresholds — schedule manual updates after big loads, or use
  trace flag 2371 / the 2016+ recompute behaviour.
- Watch for the **parameter sniffing** trap: a plan cached for one parameter
  value performs terribly for another. Mitigate with `OPTION (RECOMPILE)`,
  `OPTIMIZE FOR`, or query-store forced plans.

## 4. Indexing

- Index the columns you **filter, join, and order** on — driven by the
  workload, not guesswork. Check actual predicates in the plan / query store /
  AWR.
- **Composite index column order matters**: equality predicates first, then
  range, then sort columns (the "left-prefix" rule). An index on `(a,b)` helps
  `WHERE a=… AND b=…` and `WHERE a=…`, but not `WHERE b=…` alone.
- **Covering indexes**: include the projected columns (`INCLUDE` in SQL Server;
  add to the index key or use an index-organised/covering design in Oracle) so
  the engine never touches the base table. Kills key-lookups.
- **Don't over-index**: every index taxes every insert/update/delete and bloats
  storage. Find unused indexes (`sys.dm_db_index_usage_stats`;
  `V$OBJECT_USAGE` / `DBA_INDEX_USAGE` in Oracle) and drop dead ones.
- **Rebuild/reorganise** fragmented indexes only when fragmentation actually
  hurts range scans; for OLTP, fill-factor tuning matters more than chasing 0%.
- Filtered indexes (SQL Server) / function-based indexes (Oracle) for narrow
  hot predicates.

## 5. Sargability (let the index work)

A predicate is **sargable** if the engine can use an index seek. Common killers:

- **Function on the column**: `WHERE TRUNC(order_date) = …` /
  `WHERE YEAR(order_date) = 2024` → rewrite as a range:
  `WHERE order_date >= DATE '2024-01-01' AND order_date < DATE '2025-01-01'`.
- **Implicit type conversion**: comparing `VARCHAR` column to `N'…'` /`NVARCHAR`,
  or string column to a number → cast the literal, not the column, and fix the
  schema type.
- **Leading wildcard** `LIKE '%foo'` → can't seek; consider full-text or a
  reversed/computed column.
- **`OR` across different columns** → sometimes better as `UNION ALL` of two
  seekable queries.
- **Arithmetic on the column** (`WHERE qty * price > 100`) → precompute or move
  the maths to the literal side.

## 6. Joins

- Confirm the join key is **unique on at least one side**; a non-unique key
  fans rows out (exploding join). Verify with a `GROUP BY … HAVING COUNT(*)>1`.
- Match **data types** on both sides of the join — a type mismatch forces a
  cast and a scan.
- Let the optimiser choose the method, but if it's wrong it's usually a
  **cardinality** problem (§3) — fix stats before adding hints.
- Pre-aggregate the large side before joining when you only need a rollup.
- For star schemas, ensure FK columns are indexed and stats/histograms exist on
  the dimension keys (Oracle star-transformation; SQL Server can use bitmap-ish
  hash plans).

## 7. Locking, blocking & contention

OLTP slowness is often not the plan at all — it's waiting on a lock.

**Oracle**
- `V$SESSION` (blocking_session), `V$LOCK`, ASH for `enq:` and `buffer busy`
  waits. `gc` waits = RAC interconnect. Long `log file sync` = commit/IO.
- Watch for row-lock contention on hot rows, and `ITL`/`enq: TX` waits.

**SQL Server**
- `sys.dm_tran_locks`, `sys.dm_os_waiting_tasks`, blocked-process report.
- `LCK_M_*` waits = blocking; `PAGELATCH` on tempdb = allocation contention
  (add tempdb files); `WRITELOG` = log IO.
- Reduce lock footprint: shorter transactions, correct isolation level,
  consider `READ COMMITTED SNAPSHOT` to cut reader/writer blocking.

General: keep transactions short, commit in reasonable batches (not row-by-row,
not one giant transaction), and access tables in a consistent order to avoid
deadlocks.

## 8. Plan stability

When a good query suddenly regresses:

- **Oracle**: SQL Plan Baselines (`DBMS_SPM`) to lock a known-good plan; SQL
  Profiles / SQL Tuning Advisor for corrections; check for plan flips after a
  stats gather or upgrade. Adaptive plans/cardinality feedback can both help
  and surprise you.
- **SQL Server**: Query Store → "force plan" on the last good plan; investigate
  parameter sniffing (§3). Beware cardinality-estimator version changes across
  compatibility levels after an upgrade.

## 9. Engine cheat-sheet (Oracle ↔ SQL Server)

| Concept | Oracle | SQL Server |
|---|---|---|
| Estimated plan | `EXPLAIN PLAN` + `DBMS_XPLAN.DISPLAY` | Estimated Execution Plan / `SET SHOWPLAN_XML` |
| Actual plan w/ row counts | `GATHER_PLAN_STATISTICS` + `DISPLAY_CURSOR(ALLSTATS LAST)` | Actual Execution Plan / `SET STATISTICS XML ON` |
| Per-statement IO/CPU | SQL Monitor / AWR | `SET STATISTICS IO, TIME ON` |
| Historical plans | AWR / `DISPLAY_AWR` | Query Store |
| Gather stats | `DBMS_STATS.GATHER_TABLE_STATS` | `UPDATE STATISTICS … WITH FULLSCAN` |
| Covering columns | function-based / IOT / add to key | `INCLUDE` columns |
| Lock a plan | SQL Plan Baseline (`DBMS_SPM`) | Query Store "force plan" |
| Live waits | ASH / `V$SESSION` / `V$LOCK` | `sys.dm_os_wait_stats` / `dm_tran_locks` |
| Skew handling | histograms (`METHOD_OPT`) | filtered stats / `OPTION(RECOMPILE)` |

**Always**: refresh stats → get the actual plan → fix sargability/index →
re-measure against the baseline before reaching for hints or hardware.
