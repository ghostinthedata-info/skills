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
   artifacts; typically 3–5 models dominate 60–80% of runtime — those are
   your candidates, but step 2 decides what's worth touching. Also measure
   **time-to-consumer** (source event → landed → processed → served): it's
   the number stakeholders feel, and DAG runtime is only part of it. Keep
   these timings in a table you own — managed orchestrators may hide their
   metadata store. Record real numbers; never eyeball.
2. **Find the critical path.** The longest chain of dependent tasks sets the
   minimum runtime. **Optimising a task not on the critical path changes
   nothing.** A 20-min model running parallel to a 45-min model is not the
   bottleneck — but a 30-second task that gates five parallel branches can
   be. Shorten the path three ways: make its tasks faster, take tasks off it
   (drop dependencies that don't reflect real reads), or split a monolithic
   step so its parts run in parallel.
3. **Diagnose with the plan.** Pull the query/execution plan or job profile
   for the dominant stages and read it for full scans, skew, spills,
   exploding joins, and stale stats. (Engine-specific: see references below.)
4. **Form a hypothesis, change one thing, re-measure.** Bisect against the
   baseline. If a change didn't move the number, revert it. Re-confirm the
   critical path after each win — the bottleneck moves.
5. **Guardrail.** Track completion-time drift over weeks; audit dependencies
   quarterly; alert on a runtime budget and on freshness / time-to-consumer
   breaches, not just on failure.

### If the symptom is drift ("shifting right")

Plot completion time per run over the last 30–60 days. If it trends later,
check the four usual causes, most common first:

1. **Volume growth** — inputs outgrew a full-rebuild step. Fix: incremental
   processing.
2. **Resource contention** — more jobs share one compute window; it shows up
   as queue/wait time, not task time. Fix: separate compute per workload
   (transform / BI / ad-hoc), stagger start times, or scale for that window.
3. **Critical-path lengthening** — small steps added to the path accumulate.
   Fix: re-derive the critical path after every significant change and move
   non-essential steps off it.
4. **Upstream source delay** — check source freshness separately, so a late
   source isn't misread as a slow pipeline. Fix: trigger on arrival, with a
   wait that holds no compute and times out loudly.

### If the problem is cost

Cost has its own levers; speed fixes don't always lower the bill.

* **Attribute before you cut.** Tag every query and job with model, pipeline,
  team, and environment, then rank compute by spend — two or three
  warehouses/clusters usually drive most of it.
* **Find spend that never shows up as a slow query:** idle compute (match the
  suspend policy to the workload — batch compute suspends between runs,
  interactive BI stays warm a little longer between bursts), background
  services (auto-clustering, materialised-view upkeep, continuous ingestion),
  cross-region transfer, and storage of outputs nobody reads.
* **Retire zombies.** An output with no reads in ~90 days costs its refresh and
  its storage — review it with its owner, deprecate it, keep a way back (and
  check retention and legal-hold rules before deleting classified data).
* **Watch for spikes as well as creep:** tiered budget alerts, and a daily
  spend check against a rolling baseline.

## Common high-leverage fixes (tool-agnostic)

* **Partition pruning / clustering.** Organise data by the columns you
  filter on so queries scan a fraction of the table. Choose keys by how the
  table is *queried*, not how it's loaded; limit to 2–3. Don't wrap the
  partition column in a function in the `WHERE` — it kills pruning.
* **Incremental processing.** Switch growing fact tables from full rebuild to
  incremental + idempotent merge so volume growth stops mattering. Re-read a
  lookback window sized to how late the source can be, merge on a unique key,
  and schedule a periodic full refresh to correct drift.
* **Materialise on purpose.** Nested views re-execute their whole chain on
  every query, but materialising everything costs too. Inline (CTE or
  ephemeral) any step with a single downstream consumer; keep light, rarely
  read logic as a view; make a model a table when it takes more than ~30s to
  build and is read more than once between builds; go incremental for large
  tables where a small share changes per run.
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
  [RDBMS-ORACLE-MSSQL.md](./RDBMS-ORACLE-MSSQL.md).
* **Cloud / MPP warehouses — Snowflake, BigQuery, Redshift, Databricks SQL**
  (micro-partitions, pruning, clustering, warehouse sizing, slot/credit
  cost): read [CLOUD-WAREHOUSE.md](./CLOUD-WAREHOUSE.md).
* **Spark — Spark SQL, PySpark, Databricks, Glue, EMR** (shuffle, partition
  counts, skew/stragglers, AQE, broadcast joins, caching, spill): read
  [SPARK.md](./SPARK.md).

If a workload spans engines (e.g. Spark writing to Snowflake), read both and
tune the dominant stage first.

## Template

For a working checklist of the whole loop — measure, what to look for in a
query plan, the high-leverage fixes in priority order, and the anti-patterns
— see [TUNING-CHECKLIST.md](./TUNING-CHECKLIST.md). The principles are
tool-agnostic; map feature names to your engine.
