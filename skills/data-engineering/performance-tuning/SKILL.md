---
name: performance-tuning
description: A methodology for tuning slow pipelines and queries — measure first, find the critical path, then fix with partition pruning, incremental processing, idempotent merges, and dependency cleanup. Tool-agnostic spine plus engine-specific reference files for traditional RDBMS (Oracle/SQL Server), cloud warehouses (Snowflake/BigQuery/Redshift), and Spark. Use this skill whenever a pipeline is slow or "shifting right" (finishing later each month), a query is expensive or timing out, a warehouse bill is climbing, a Spark job is stalling or spilling, or anyone asks to optimise, speed up, profile, or baseline a query, transform, or data job — even if they don't say the word "tuning."
---

# Performance Tuning

Pipeline health is **trajectory**, not pass/fail. A green DAG that runs 5%
slower every month is a ticking clock toward a missed SLA — "slow is harder
to see than broken" (Ghost in the Data, "Why Your Pipeline Finishes Later
Every Month"). Tune with discipline; don't guess.

Consult `docs/agents/platform.md` (if present) for which optimisation
features your engine actually has.

## The method (in order)

1. **Measure first — establish a baseline.** Instrument each stage (duration
   AND queue/wait time). Read your orchestrator/transform tool's run
   artifacts; typically 3–5 models dominate 60–80% of runtime — those are the
   only ones worth touching. Record real numbers; never eyeball.
2. **Find the critical path.** The longest chain of dependent tasks sets the
   minimum runtime. **Optimising a task not on the critical path changes
   nothing.** A 20-min model running parallel to a 45-min model is not the
   bottleneck.
3. **Diagnose with the plan.** Pull the query/execution plan or job profile
   for the dominant stages and read it for full scans, skew, spills,
   exploding joins, and stale stats. (Engine-specific: see references below.)
4. **Form a hypothesis, change one thing, re-measure.** Bisect against the
   baseline. If a change didn't move the number, revert it. Re-confirm the
   critical path after each win — the bottleneck moves.
5. **Guardrail.** Track completion-time drift over weeks; audit dependencies
   quarterly; alert on a runtime budget, not just on failure.

## Common high-leverage fixes (tool-agnostic)

* **Partition pruning / clustering.** Organise data by the columns you
  filter on so queries scan a fraction of the table. Choose keys by how the
  table is *queried*, not how it's loaded; limit to 2–3. Don't wrap the
  partition column in a function in the `WHERE` — it kills pruning.
* **Incremental processing.** Switch growing fact tables from full rebuild to
  incremental + idempotent merge so volume growth stops mattering.
* **Avoid full scans & view-on-view.** Nested views re-execute their whole
  chain on every query; materialise expensive intermediate layers as tables.
* **Filter early, project narrow.** Push `WHERE` down; avoid `SELECT *`. On
  columnar engines fewer columns = less I/O.
* **Fix the join.** Join on unique keys; match types on both sides;
  pre-aggregate before joining; broadcast the small side.
* **Kill phantom & monster dependencies.** Remove refs that no longer reflect
  real reads. Keep core spine models lean — push expensive enrichment into a
  separate downstream model (`dim_customers` lean vs `dim_customers_extended`)
  so 40 downstream models don't wait on a propensity score. Rule of thumb: if
  fewer than half of consumers use an attribute, it doesn't belong on the
  core model.
* **Right-size "real-time."** Most "we need real-time" is "we need faster
  batch" — micro-batch every 15–60 min beats new streaming infra. Reserve
  true streaming for fraud/safety/RTB.
* **Event-driven triggers.** Replace "schedule at 4am and hope" with
  trigger-on-arrival to remove safety-margin slack.

## Choose the right engine reference

The spine above is tool-agnostic. For diagnosis and fixes that depend on the
engine, read the matching reference file — map the generic feature names to
your platform's actual features:

* **Traditional transactional RDBMS — Oracle, SQL Server** (B-tree indexes,
  optimiser stats, lock/latch contention, plan baselines): read
  [references/rdbms-oracle-mssql.md](./references/rdbms-oracle-mssql.md).
* **Cloud / MPP warehouses — Snowflake, BigQuery, Redshift, Databricks SQL**
  (micro-partitions, pruning, clustering, warehouse sizing, slot/credit
  cost): read [references/cloud-warehouse.md](./references/cloud-warehouse.md).
* **Spark — Spark SQL, PySpark, Databricks, Glue, EMR** (shuffle, partition
  counts, skew/stragglers, AQE, broadcast joins, caching, spill): read
  [references/spark.md](./references/spark.md).

If a workload spans engines (e.g. Spark writing to Snowflake), read both and
tune the dominant stage first.

## Template

For a working checklist of the whole loop — measure, what to look for in a
query plan, the high-leverage fixes in priority order, and the anti-patterns
— see [TUNING-CHECKLIST.md](./TUNING-CHECKLIST.md). The principles are
tool-agnostic; map feature names to your engine.
