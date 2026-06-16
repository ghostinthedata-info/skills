# Spark Tuning — Spark SQL / PySpark (Databricks, Glue, EMR, OSS)

For distributed in-memory compute. The SQL-shaped fixes (prune, filter early,
fix joins) still apply, but the dominant bottleneck is almost always the
**shuffle**: moving data across the network between stages. Most Spark tuning
is about *avoiding, shrinking, or balancing the shuffle*, then giving each task
the right amount of data and memory. Don't reach for `repartition()` or more
executors before you've read the DAG.

## Contents
1. Read the Spark UI first
2. The shuffle is usually the problem
3. Partitioning (the #1 lever)
4. Skew & stragglers
5. Joins
6. Caching & persistence
7. File layout & I/O
8. Memory, spill & serialization
9. Adaptive Query Execution (turn it on)
10. PySpark-specific traps
11. Config cheat-sheet

---

## 1. Read the Spark UI first

Don't guess — open the **Spark UI** (or Databricks Spark UI / Glue Spark UI /
EMR history server):

- **Stages tab**: find the stage eating the wall-clock. Look at its **task
  duration distribution** — a long *max* vs *median* = skew/stragglers.
- **Shuffle Read/Write** columns: large shuffle = expensive stage; that's your
  target.
- **Spill (memory/disk)** columns: non-zero spill = tasks exceeding memory;
  repartition or raise memory.
- **SQL tab**: the query plan with per-operator row counts and *Exchange*
  (shuffle) nodes; *BroadcastHashJoin* vs *SortMergeJoin*; whole-stage codegen.
- **Tasks**: a few tasks running 10× longer than the rest = data skew.
- `df.explain("formatted")` / `EXPLAIN FORMATTED` to see the physical plan and
  count Exchanges before you run.

## 2. The shuffle is usually the problem

A shuffle happens on `join`, `groupBy`/aggregation, `repartition`, `distinct`,
and window functions. It writes to disk, sends over the network, and re-reads —
orders of magnitude slower than a narrow transformation.

- **Minimise shuffles**: filter and project **before** the shuffle so less data
  crosses the network. Push `WHERE`/`select` up; drop columns you don't need.
- **Avoid needless re-shuffles**: don't `repartition()` then immediately
  `groupBy` on a different key. Co-locate operations that share a key.
- **Pre-aggregate** before a join when you only need a rollup.
- Prefer `reduceByKey`-style combiners over `groupByKey` (RDD land); in
  DataFrame land the Catalyst optimiser does map-side combine for you.

## 3. Partitioning (the #1 lever)

Two different things both called "partitions":

**(a) Shuffle partitions** — `spark.sql.shuffle.partitions` (default 200).
- Too few → huge tasks, spill, OOM. Too many → scheduling overhead, tiny tasks.
- Aim for tasks of ~**100–200MB** each. Rough target: total shuffle data ÷
  ~128MB. With **AQE on** (§9), let `coalescePartitions` size this dynamically
  rather than hard-coding 200.

**(b) Input/DataFrame partitions** — how the data is split across the cluster.
- `repartition(n)` = full shuffle to `n` even partitions (use to *increase*
  parallelism or fix skew).
- `coalesce(n)` = merge without full shuffle (use to *decrease*, e.g. before
  writing fewer output files).
- `repartition(col)` to co-locate by join/group key and avoid a later shuffle.

Rule of thumb: target **2–4 tasks per CPU core** across the cluster so cores
stay busy without excessive overhead.

## 4. Skew & stragglers

One key with far more rows than the rest = one task that runs forever while the
cluster idles. Classic signature: stage max-task-time ≫ median.

- **Find it**: `df.groupBy(key).count().orderBy(desc("count"))` — look for a hot
  key, often `NULL`, `0`, `''`, or a default/unknown value.
- **Filter or split nulls/sentinels** before the join, handle them separately.
- **Salting**: append a random suffix to the hot key on both sides to spread it
  across tasks, then strip it after the join.
- **AQE skew join handling** (`spark.sql.adaptive.skewJoin.enabled=true`) splits
  skewed partitions automatically — often the easiest fix; turn it on first.

## 5. Joins

- **Broadcast the small side**: if one side fits in memory
  (`spark.sql.autoBroadcastJoinThreshold`, default 10MB), Spark broadcasts it
  and skips the shuffle entirely — a *BroadcastHashJoin* in the plan. Hint it
  with `broadcast(df)` / `/*+ BROADCAST(t) */` when the optimiser underestimates.
- **SortMergeJoin** on two large shuffled sides is the default for big-big; make
  sure both sides are partitioned on the join key to avoid double shuffles.
- **Check key uniqueness** — a non-unique key explodes output rows (output ≫
  input in the plan). Dedup or aggregate first.
- **Match key types** on both sides; a type mismatch silently disables broadcast
  and can force a cartesian-ish plan.
- Avoid **cross joins** unless intended (`spark.sql.crossJoin` guard).

## 6. Caching & persistence

- `cache()`/`persist()` **only** a DataFrame reused multiple times (e.g. an
  iterative algorithm or a base reused by several branches). Caching a
  single-use DataFrame wastes memory and can *cause* spill.
- Pick the storage level deliberately: `MEMORY_AND_DISK` is the safe default;
  `MEMORY_ONLY` risks recompute under pressure.
- **`unpersist()`** when done to free memory.
- Remember caching is lazy — it materialises on the next action.

## 7. File layout & I/O

- **Small-file problem**: thousands of tiny files = huge task-scheduling
  overhead and slow listing. Compact (`OPTIMIZE` on Delta, or `coalesce`/
  `repartition` before write) to ~**128MB–1GB** files.
- **Partition the output** by a low-cardinality column you filter on
  (`partitionBy("date")`) so downstream reads prune — but **don't
  over-partition** (a column with millions of values creates millions of tiny
  dirs).
- **Columnar formats** (Parquet/ORC/Delta) with predicate pushdown + column
  pruning; avoid CSV/JSON for big intermediate data.
- **Partition pruning & pushdown**: confirm filters reach the scan
  (`PushedFilters` in `explain`). A function around the partition column defeats
  pruning, same as any engine.
- Watch the **GC** and read time in the UI — heavy GC means too much data per
  executor.

## 8. Memory, spill & serialization

- **Spill (memory→disk)** in the UI = working set exceeds executor memory.
  Options: more shuffle partitions (smaller tasks), more executor memory, or
  less data via earlier filtering.
- **Executor sizing**: a handful of *fat* executors (e.g. 4–5 cores, several GB
  each) usually beats many tiny ones; leave headroom for overhead
  (`spark.executor.memoryOverhead`). Avoid one giant executor (GC pauses) and
  avoid 1-core executors (no in-executor parallelism).
- **Kryo serialization** (`spark.serializer=org.apache.spark.serializer.KryoSerializer`)
  for faster/smaller shuffle on RDD/dataset-heavy jobs.
- Avoid collecting large results to the driver (`collect()`); it OOMs the
  driver. Use `take`, `write`, or aggregate first.

## 9. Adaptive Query Execution (turn it on)

On Spark 3+, AQE re-optimises at runtime using actual stage statistics. It's
the single biggest "free win":

```
spark.sql.adaptive.enabled = true
spark.sql.adaptive.coalescePartitions.enabled = true   # right-sizes shuffle partitions
spark.sql.adaptive.skewJoin.enabled = true             # splits skewed partitions
```

With AQE on, stop hard-coding `shuffle.partitions` to 200 and let it coalesce.
It can also switch SortMergeJoin → BroadcastJoin at runtime when a side turns
out small. (Databricks: on by default; Glue/EMR: verify the version and enable.)

## 10. PySpark-specific traps

- **Avoid Python UDFs** where a built-in/`pyspark.sql.functions` expression
  exists — Python UDFs serialise row-by-row to a Python worker (slow, no
  codegen). If you must, use **pandas/vectorized UDFs** (Arrow) and enable
  `spark.sql.execution.arrow.pyspark.enabled=true`.
- Don't loop in Python over a DataFrame's rows; express it as a transformation.
- Beware accidental wide ops in pandas-on-Spark / `.toPandas()` pulling
  everything to the driver.

## 11. Config cheat-sheet

| Lever | Config / API | When |
|---|---|---|
| Shuffle partition count | `spark.sql.shuffle.partitions` (+ AQE coalesce) | spill / tiny tasks / 200-default mismatch |
| Adaptive execution | `spark.sql.adaptive.enabled=true` | always, Spark 3+ |
| Skew join | `spark.sql.adaptive.skewJoin.enabled=true` + salting | straggler tasks |
| Broadcast join | `spark.sql.autoBroadcastJoinThreshold`, `broadcast(df)` | one side small |
| Repartition/coalesce | `repartition(n[,col])` / `coalesce(n)` | parallelism up / files down |
| Cache reused data | `persist(MEMORY_AND_DISK)` / `unpersist()` | DataFrame reused ≥2× |
| Output file size | `OPTIMIZE` / coalesce before write | small-file problem |
| Serialization | Kryo serializer | RDD/dataset-heavy shuffle |
| Arrow for UDFs | `spark.sql.execution.arrow.pyspark.enabled=true` | pandas UDFs / toPandas |

**Always**: read the Spark UI → identify the dominant stage and whether it's
shuffle / skew / spill → apply one fix (AQE + broadcast + skew handling cover
most cases) → re-measure the stage against the baseline. Don't add executors to
hide a skew or full-scan bug.
