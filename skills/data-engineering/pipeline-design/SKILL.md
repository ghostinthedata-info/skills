---
name: pipeline-design
description: Default design principles for robust data pipelines — idempotency, reproducibility, backfills, defensive engineering, and safe deployment. Use when designing a new pipeline or DAG, reviewing one, or hardening a fragile pipeline that breaks on retries/backfills.
---

# Pipeline Design

Build pipelines that you can re-run, backfill, and reason about. These are
the non-negotiable defaults.

## Idempotency — the foundation

A task must produce the same result whether it runs once or ten times.
Without it you cannot safely retry, backfill, or debug. Use **merge/upsert
with a unique key**, not blind insert (a mid-run failure + rerun =
duplicates). Guard merges so newer data isn't overwritten by older on replay
(`WHEN MATCHED AND source.updated_at > target.updated_at`).

## Reproducibility

Prefer **path-independent** designs: the output depends on the input data
and the code, not on the history of runs (the Healing Tables principle —
see `slowly-changing-dimensions` if installed). You should be able to drop
and rebuild a layer from source. Pin time, seed any randomness, and version
the transformation logic.

## Backfills

Design for backfill from day one rather than looping the daily job N times
(that compounds errors and degrades non-linearly). Process whole ranges in
one pass; make the range a parameter; validate temporal integrity before
publish.

## Defensive engineering

* Validate inputs at boundaries (schema, types, freshness) and fail fast
  with a clear message — don't let a malformed row propagate silently.
* Handle late-arriving and out-of-order data explicitly; decide soft vs hard
  deletes up front.
* Quarantine bad records (error mart) rather than dropping them invisibly.

## Safe deployment

Use **Write-Audit-Publish**: stage the new data, audit it with the full test
battery, then swap into production with a backup — never publish on red (see
`test-data` if installed for the audit battery). Keep core spine models lean
so the DAG stays wide and parallel, not a serial chain. Make every task emit
the metrics (duration, queue wait, row counts) that tuning needs later.

## Visibility

Ship a thin visible slice early and keep stakeholders updated on a cadence.
A pipeline nobody can see the progress of is a pipeline nobody trusts
(Ghost in the Data, "Don't Go Dark").

## Template

For a pre-build/review checklist plus tool-agnostic skeletons (idempotent
guarded merge, boundary validation, quarantine, the WAP swap), see
[DESIGN-CHECKLIST.md](./DESIGN-CHECKLIST.md). Substitute your engine's
syntax (consult `docs/agents/platform.md` and `docs/agents/tooling.md` if
present).
