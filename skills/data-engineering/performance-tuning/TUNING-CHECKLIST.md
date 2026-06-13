# Performance Tuning Checklist

A working checklist for the measure → critical-path → fix loop in the skill,
plus what to look for when reading a query plan and the high-leverage SQL
patterns. Tool-agnostic: the *principles* hold on every engine; the exact
function/feature names differ (consult `docs/agents/platform.md` if present).

---

## 0. Before you touch anything — measure

- [ ] Capture a **baseline**: total runtime, per-stage duration, AND queue/wait time.
- [ ] Pull run artifacts from the orchestrator/transform tool (dbt `run_results.json`,
      Airflow task durations, query history). Don't eyeball — record numbers.
- [ ] Rank stages by runtime. Expect **3–5 models to dominate 60–80%** — those
      are the only ones worth touching first.
- [ ] Identify the **critical path** (longest chain of *dependent* tasks). A
      20-min model running parallel to a 45-min model is not the bottleneck;
      optimising off the critical path changes nothing.

## 1. Read the query plan — what to look for

Run `EXPLAIN` / `EXPLAIN ANALYZE` (or your engine's profile view) and scan for:

- [ ] **Full table scan** where a filter should have pruned — missing partition
      filter, function wrapped around the filter column (`WHERE DATE(ts) = …`
      defeats the index/pruning), or implicit type cast.
- [ ] **Rows scanned ≫ rows returned** — you're reading far more than you keep.
- [ ] **Spill to disk** — a join or sort exceeded memory; reduce the working
      set or repartition.
- [ ] **Skew** — one partition/reducer does most of the work (a hot key, often
      NULL or a default value). Look at per-partition row counts.
- [ ] **Exploding join** — output rows ≫ input rows = a non-unique join key
      fanning out. Re-check key uniqueness (see `profile-data`).
- [ ] **Nested-loop join on big inputs** where a hash join was expected — stale
      stats or a non-equi join.
- [ ] **Stale statistics** — estimated vs actual row counts diverge wildly;
      re-gather stats / analyze the table.

## 2. High-leverage fixes (in rough priority order)

- [ ] **Filter early, project only needed columns.** Push `WHERE` down; avoid
      `SELECT *`. On columnar engines, fewer columns = less I/O.
- [ ] **Partition pruning / clustering.** Organise by the columns you *filter*
      on, not how you load. Limit to 2–3 keys. Don't wrap the partition column
      in a function in the `WHERE`.
- [ ] **Incremental processing.** Switch growing fact tables from full rebuild
      to incremental + merge so volume growth stops mattering.
- [ ] **Materialise repeated work.** Nested views re-execute their whole chain
      on every query; persist expensive intermediate layers as tables.
- [ ] **Fix the join.** Join on unique keys; ensure both sides are the same
      type; pre-aggregate before joining when possible; broadcast the small side.
- [ ] **Pre-aggregate.** Push `GROUP BY` upstream so downstream models scan
      fewer rows. Build aggregate tables only for proven-slow, frequently-hit
      rollups.
- [ ] **Kill phantom & monster dependencies.** Remove refs that no longer
      reflect real reads. Keep core spine models lean — push expensive
      enrichment downstream (`dim_customers` lean vs `dim_customers_extended`).
      Rule of thumb: if <half of consumers use an attribute, it doesn't belong
      on the core model.
- [ ] **Right-size "real-time."** Most "real-time" is "faster batch" — micro-batch
      every 15–60 min beats new streaming infra. Reserve true streaming for
      fraud/safety/RTB.
- [ ] **Event-driven triggers.** Replace "schedule at 4am and hope" with
      trigger-on-arrival to remove safety-margin slack.

## 3. Discipline

- [ ] Form **one hypothesis**, change **one thing**, **re-measure** against the
      baseline. Never "optimise everything at once."
- [ ] Bisect: if a change didn't move the baseline, revert it.
- [ ] Re-confirm the critical path after each win — the bottleneck moves.

## 4. Guardrail (stop the slow creep)

- [ ] Track completion-time **drift over weeks**, not pass/fail per run. A green
      DAG that runs 5% slower every month is a ticking clock to a missed SLA.
- [ ] Audit dependencies **quarterly**; delete dead edges.
- [ ] Alert on a runtime budget (e.g. "warn if this DAG exceeds 90 min"), not
      just on failure. Fix the 3-min/week creep before a stakeholder asks.

---

## Anti-patterns to call out

- Optimising a model that isn't on the critical path.
- Adding an index/cluster key without checking how the table is *queried*.
- Wrapping the filter/partition column in a function (kills pruning).
- `SELECT *` through a chain of views.
- Defaulting to streaming because someone said "real-time."
- Tuning by guesswork with no before/after numbers.
