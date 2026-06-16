# Performance Tuning Checklist

A copy-paste checklist for the full tuning loop. Work the sections in order;
don't jump to fixes before the baseline and critical path are confirmed.
Map feature names to your engine using the reference files in this directory.

---

## 1. Measure — establish a baseline

- [ ] Instrument every pipeline stage: **duration** AND **queue/wait time** separately.
- [ ] Pull run history for the last 2–4 weeks; note any trend (growing? flat? spiking?).
- [ ] Record real numbers — never eyeball or estimate from memory.
- [ ] Identify the **3–5 models/stages that dominate 60–80% of total runtime** — these are the only candidates worth touching.

---

## 2. Find the critical path

- [ ] Map all task dependencies (DAG view if available).
- [ ] Identify the **longest chain** — that chain sets the floor for total runtime.
- [ ] Confirm each candidate optimisation target is **on the critical path**.
  - A model running in parallel to a longer task is not a bottleneck; optimising it changes nothing.
- [ ] Re-confirm the critical path **after each win** — the bottleneck moves.

---

## 3. Diagnose with the plan / job profile

Pull the query plan or job profile for the dominant critical-path stages. Read for:

- [ ] **Full table scans** on large tables — no partition/cluster pruning firing.
- [ ] **Partition column wrapped in a function** — kills pruning (e.g. `DATE(loaded_at)` instead of `loaded_at`).
- [ ] **Exploding joins** — Cartesian products, missing join predicates, type mismatches causing implicit casts.
- [ ] **Skew / stragglers** — one task/partition taking 10× longer than peers (Spark: check stage task distribution).
- [ ] **Spills to disk** — memory insufficient; data overflows to storage (Spark/Snowflake).
- [ ] **Stale statistics** — optimizer making bad plan choices because row counts are wrong (RDBMS).
- [ ] **View-on-view chains** — nested views re-executing the whole chain on every query; should be materialised.
- [ ] **`SELECT *`** / wide projections — unnecessary columns pulled in columnar engines.

Engine-specific: see [RDBMS-ORACLE-MSSQL.md](./RDBMS-ORACLE-MSSQL.md), [CLOUD-WAREHOUSE.md](./CLOUD-WAREHOUSE.md), [SPARK.md](./SPARK.md).

---

## 4. Fix — one change at a time

Apply each fix against the baseline, re-measure, then decide keep/revert.

### Partition & clustering
- [ ] Partition/cluster by the columns the table is **filtered on**, not loaded by.
- [ ] Limit to 2–3 clustering/partition keys.
- [ ] No function wrapping the partition column in `WHERE` predicates.

### Incremental processing
- [ ] Growing fact tables switched from full rebuild to **incremental + idempotent merge**.
- [ ] Watermark column identified and tested for completeness (late-arriving rows?).

### Join quality
- [ ] Joining on **unique keys** — confirm uniqueness (see `profile-data`/`test-data` if installed).
- [ ] Types match on both sides — no implicit casts.
- [ ] Pre-aggregate large tables **before** joining where possible.
- [ ] Small side broadcast in distributed engines (Spark/BigQuery/Redshift).

### Projection & filtering
- [ ] `WHERE` pushed down as early as possible.
- [ ] Only columns actually needed in `SELECT`.
- [ ] Intermediate layers materialised as tables rather than chained views.

### Dependency diet
- [ ] Review upstream deps: remove any that no longer reflect real reads (phantom dependencies).
- [ ] Attributes used by <50% of downstream models moved off the core model into an extended/enriched model.
- [ ] Any expensive enrichment step (ML scores, complex aggregates) isolated so core spine stays lean.

### Scheduling
- [ ] Replaced "schedule at fixed time and hope" with **event/trigger-on-arrival** where feasible.
- [ ] Removed safety-margin slack added to compensate for upstream lateness.

### Real-time reality check
- [ ] Confirmed "we need real-time" is not actually "we need faster batch".
- [ ] Micro-batch (15–60 min) considered before streaming infra investment.
- [ ] True streaming reserved for fraud / safety / RTB use cases.

---

## 5. Guardrail — keep the win

- [ ] Alert on **runtime budget**, not just on job failure (`if duration > N min, alert`).
- [ ] Track completion-time trend over weeks — plot it; a 5% per-month drift is a ticking clock.
- [ ] Dependency audit scheduled quarterly.
- [ ] Baseline updated after any material change so the next comparison is valid.

---

## Anti-patterns (raise if spotted)

- Optimising a task not on the critical path.
- Adding a partition/index "just in case" without measuring.
- Applying multiple fixes simultaneously — can't attribute which one worked.
- Reverting a fix without recording why it didn't help.
- No baseline recorded before tuning started.
