---
name: spark-performance
description: Tune distributed Spark jobs — choose partition counts, minimise shuffles, broadcast small tables, handle skew, cache deliberately, and prefer narrow over wide transformations. Tool-agnostic across Spark APIs. Use when a Spark or distributed dataframe/RDD job is slow, expensive, OOMs, or has long-tail stragglers.
---

# Spark Performance

In a distributed engine the dominant cost is **moving data across the network**
(the *shuffle*), not local computation. High Performance Spark (Karau & Warren):
a partition can't split across executors, one task runs per partition, and
*"the number of tasks in a stage equals the number of partitions in that
stage's output RDD."* So tuning is mostly controlling partitions, avoiding
shuffles, and not letting one straggler hold up the stage. Measure with the
Spark UI first — find the stage with the longest tasks and heaviest shuffle
read/write before changing anything. Distributed-engine companion to
`performance-tuning` if installed.

## The five highest-leverage levers

1. **Narrow vs wide transformations** — the master distinction.
   - **Narrow** (`map`, `filter`, `mapPartitions`, `union`): each output
     partition depends on **one** input partition. No network; Spark pipelines
     them in one stage.
   - **Wide** (`groupByKey`, `join`, `distinct`, `repartition`, `sortBy`):
     output depends on **many** inputs → a **shuffle** and a stage boundary.
   - **Rule:** chain narrow ops freely; treat every wide one as a cost to
     justify. A stage boundary in the DAG = a shuffle = the expensive part.
2. **Aggregate map-side, never `groupByKey`.** Use `reduceByKey` /
   `aggregateByKey` (or DataFrame `groupBy().agg()`) so values combine before
   they cross the wire. Same answer, fraction of the shuffle.
3. **Broadcast the small side of a join.** If one table fits in memory, ship it
   to every executor and join locally — **no shuffle of the big table**. The
   highest-leverage join fix.
4. **Right-size partitions.** Partition count = parallelism. Too few starve
   cores / OOM; too many drown the scheduler. `coalesce` to shrink without a
   shuffle, `repartition` to grow or rebalance.
5. **Handle skew.** A stage finishes only when its **slowest task** finishes.
   Spot a max task far above the median in the UI; filter junk keys or salt the
   hot key.

## Prefer the structured APIs

Use DataFrames/Datasets/Spark SQL over raw RDDs for relational work — Catalyst
and Tungsten optimise the plan for free. Push filters and column selection
early, and store data columnar (Parquet/ORC), partitioned on the columns you
filter on. Drop to RDDs only for genuinely non-relational logic.

## Cache deliberately — not by default

Caching consumes executor memory and adds overhead. Cache **only** a dataset
**reused multiple times** (iterative algorithm, or a base table feeding several
outputs); `unpersist()` when done. A dataset used once should never be cached.

## The method

1. Open the Spark UI; find the longest stage and its heaviest shuffle.
2. Ask the data: *How is it distributed? Is it skewed? What's the range and
   grouping of the join/group key?*
3. Apply the highest-leverage fix that fits (broadcast a small side; replace
   `groupByKey`; salt a hot key; right-size partitions; cache a reused result).
4. Change one thing, re-run, re-read the UI. Never tune blind.

## Reference

For the full catalogue — structured-API detail, the shuffle/partitioning/
broadcast/skew/cache deep-dives, and serialization config — see
[REFERENCE.md](./REFERENCE.md). See `performance-tuning` for the engine-agnostic
loop (measure → critical path → one change at a time) and `pipeline-design` for
where a heavy Spark job fits in a wider DAG, if installed.
