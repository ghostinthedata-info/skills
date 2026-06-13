---
name: performance-tuning
description: A methodology for tuning slow pipelines and queries — measure first, find the critical path, then fix with partition pruning, incremental processing, idempotent merges, and dependency cleanup. Tool-agnostic. Use when a pipeline is slow or "shifting right" (finishing later each month), or a query is expensive.
---

# Performance Tuning

Pipeline health is **trajectory**, not pass/fail. A green DAG that runs 5%
slower every month is a ticking clock toward a missed SLA — "slow is harder
to see than broken" (Ghost in the Data, "Why Your Pipeline Finishes Later
Every Month"). Tune with discipline; don't guess.

Consult `docs/agents/platform.md` (if present) for which optimisation
features your engine actually has.

## The method (in order)

1. **Measure first.** Instrument each stage (duration AND queue/wait time).
   Read your orchestrator/transform tool's run artifacts; typically 3–5
   models dominate 60–80% of runtime — those are the only ones worth
   touching.
2. **Find the critical path.** The longest chain of dependent tasks sets the
   minimum runtime. **Optimising a task not on the critical path changes
   nothing.** A 20-min model running parallel to a 45-min model is not the
   bottleneck.
3. **Form a hypothesis, change one thing, re-measure.** Establish a
   baseline, then bisect. Never "optimise everything at once."

## Common high-leverage fixes

* **Partition pruning / clustering.** Organise data by the columns you
  filter on so queries scan a fraction of the table, not all of it. Choose
  keys by how the table is *queried*, not how it's loaded; limit to 2–3.
* **Incremental processing.** Switch growing tables from full rebuild to
  incremental + merge so volume growth stops mattering. Most fact tables.
* **Avoid full scans & view-on-view.** Nested views re-execute their whole
  chain on every query; materialise expensive intermediate layers as tables.
* **Kill phantom & monster dependencies.** Remove references that no longer
  reflect real reads. Keep core spine models lean — push expensive
  enrichment into a separate downstream model (e.g. `dim_customers` lean vs
  `dim_customers_extended`) so 40 downstream models don't wait on a
  propensity score. Rule of thumb: if fewer than half of consumers use an
  attribute, it doesn't belong on the core model.
* **Right-size "real-time."** Most "we need real-time" is "we need faster
  batch" — micro-batch every 15–60 min beats new streaming infra. Reserve
  true streaming for fraud/safety/RTB.
* **Event-driven triggers.** Replace "schedule at 4am and hope" with
  trigger-on-arrival to remove safety-margin slack.

## Guardrail

Track completion-time drift over weeks and audit dependencies quarterly. Fix
the 3-min/week creep before a stakeholder asks.
