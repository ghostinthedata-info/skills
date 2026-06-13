# Spark Performance — Reference

Deep catalogue behind the [`spark-performance` skill](./SKILL.md). The SKILL.md
holds the method and highest-leverage rules; this file holds the detail you
reach for once you know which lever to pull.

## Prefer the structured APIs

- **DataFrames/Datasets/Spark SQL over raw RDDs** for relational work. Catalyst
  rewrites the plan (predicate pushdown, column pruning, join selection);
  Tungsten stores data compactly off-heap — optimisations RDD code can't get.
  Drop to RDDs only for genuinely non-relational logic.
- **Push filters and column selection early.** Filter before join, `select`
  only needed columns. With columnar formats the engine reads less off disk via
  predicate/projection pushdown.
- **Prefer columnar, splittable, compressed storage** (Parquet/ORC) over
  CSV/JSON. Partition on disk by the columns you filter on so whole files are
  skipped — the storage-layer equivalent of partition pruning.

## Shuffle catalogue

- **Never `groupByKey` to aggregate.** It shuffles every value, then reduces.
  Use `reduceByKey` / `aggregateByKey` / `combineByKey` (or DataFrame
  `groupBy().agg()`) so values combine **map-side first** and only partials
  cross the wire. Same answer, fraction of the shuffle — and `groupByKey` can
  OOM one reducer on a hot key.
- **Shuffle once, then reuse the partitioning.** Ops needing a known partitioner
  (`reduceByKey`, `join`, `lookup`) run shuffle-free against an
  already-partitioned RDD. `partitionBy(partitioner)` + `persist` once if you'll
  join/aggregate on the same key repeatedly.
- **Use partition-preserving ops.** `mapValues` / `flatMapValues` keep the
  partitioner; a plain `map` discards it (Spark can't know the key is unchanged)
  and forces the next key-op to reshuffle.
- **Co-partition before joining.** Two RDDs with the **same partitioner** join
  without a full shuffle.

## Partitioning detail

- **Partition count = parallelism.** Too few starve cores and bloat per-task
  memory (OOM/spill); too many drown the scheduler in tiny tasks. Aim for
  partitions that fit comfortably in executor memory, totalling a small multiple
  of total cores.
- **`coalesce` to shrink, `repartition` to grow or rebalance.** `coalesce(n)`
  reduces partitions **without a full shuffle** (merges adjacent) — use after a
  heavy `filter`. `repartition(n)` does a full shuffle for even sizes — use to
  increase parallelism or fix skew.
- **Don't write a thousand tiny files.** `coalesce` before writing so downstream
  reads aren't dominated by file-open overhead.

## Broadcast joins

- **When one side fits in memory, broadcast it.** A broadcast (map-side) hash
  join ships the small table to every executor and joins locally — **no shuffle
  of the big table.** Highest-leverage join optimisation.
- In Spark SQL this is the **broadcast hash join**, chosen automatically below
  `spark.sql.autoBroadcastJoinThreshold`; raise the threshold or use an explicit
  `broadcast()` hint when you know a table is small but the estimate doesn't.
  Confirm in the plan (`BroadcastHashJoin`).
- **Use broadcast variables for read-only lookup data** referenced in
  transformations, instead of capturing a large object in a closure (re-shipped
  per task).
- The alternative — a shuffle/sort-merge join — moves **both** sides across the
  network, so reach for broadcast whenever the small side qualifies.

## Skew (the straggler problem)

- A stage finishes only when its **slowest task** finishes. One overloaded
  partition (hot key, nulls, default value) runs 10× longer while other cores
  idle. Spot it in the UI: max task duration / shuffle-read far above median.
- **Filter junk keys** (nulls, sentinels, empty strings) before the wide op.
- **Salt the hot key:** append a random suffix (`key#0..N`) to spread it across
  partitions, aggregate per-salt, then aggregate the partials. Or split and
  broadcast-join the skewed keys separately.
- **`repartition` to rebalance** when skew is from uneven partition sizes rather
  than one dominant key.

## Cache deliberately — not by default

- **Caching isn't free:** it consumes executor memory (evicting other data,
  causing recompute or spill) and adds overhead. Cache **only** an RDD/DataFrame
  **reused multiple times** (iterative algorithm, or a base table feeding
  several outputs). A dataset used once should never be cached.
- **Choose the storage level on purpose.** `MEMORY_ONLY` is fastest but drops
  blocks under pressure (forcing recompute); `MEMORY_AND_DISK` spills instead —
  prefer when recompute is expensive. `*_SER` levels trade CPU for a much
  smaller footprint.
- **`unpersist()` when done** so blocks don't squat in memory.
- Caching also **pins nondeterministic results** (random splits,
  current-timestamp columns) so they don't change between actions.

## Serialization & engine config

- **Register Kryo serialization** (`spark.serializer` = `KryoSerializer`,
  register your classes) for RDD-heavy jobs — far more compact and faster than
  Java serialization, shrinking every shuffle and cached block.
- Right-size executor memory/cores rather than over-allocating; an OOM is
  usually too few partitions or a skewed key, not too little RAM.

---
Source: *High Performance Spark*, Karau & Warren (O'Reilly).
