---
name: slowly-changing-dimensions
description: Decide how to track attribute change over time — SCD types 0,1,2,3,4,5,6,7 with trade-offs, plus the Healing Tables approach to deterministic, rebuildable SCD2. Use when a dimension attribute changes and you must decide whether/how to keep history, or when an SCD2 backfill has gone wrong.
---

# Slowly Changing Dimensions

When a dimension attribute changes, what do you do with the old value? Pick
per attribute, not per table — defaulting everything to Type 2 creates huge
tables with no analytical value.

## The types (Kimball)

* **Type 0** — never changes (original credit score, most date attributes).
* **Type 1** — overwrite. Simple; destroys history. Use when no one needs
  the old value. Kimball's caveat: an overwrite silently invalidates
  pre-built aggregates/OLAP cubes and makes the *same* historical report
  return different totals before vs. after the change — fine for a genuine
  correction, dangerous if anyone relies on point-in-time consistency.
* **Type 2** — add a new row with a new surrogate key,
  `valid_from`/`valid_to`, and `is_current`. The workhorse for point-in-time
  truth ("what was their region when they ordered?"). Costs row growth.
* **Type 3** — add a "previous value" column. For one-off alternate-reality
  comparisons (a single re-org), not general history.
* **Type 4** — split fast-changing attributes into a **mini-dimension** so
  the base dimension stays stable.
* **Type 5 / 6 / 7** — hybrids (4+1, 1+2, dual current/historical). Powerful
  but rarely needed; don't reach for them before confirming Type 1/2 can't
  do the job — that's premature optimisation.

## SCD2 done right

* Use left-closed/right-open intervals (`valid_from <= t < valid_to`) so
  every instant maps to exactly one version. Use a high date (`9999-12-31`)
  **and** an explicit `is_current` flag.
* Use null-safe comparison (`IS DISTINCT FROM` or equivalent) for change
  detection so NULLs compare correctly.
* Validate after every load (and block on failure): exactly one current row
  per durable key, no overlapping ranges, no gaps (if continuity required),
  `valid_from < valid_to`, no consecutive duplicate versions.

## Healing Tables (Ghost in the Data) — for backfills & deterministic SCD2

Day-by-day SCD2 backfills compound errors: a miss on Jan 3 becomes the
baseline for Jan 4, and you can't fix one day without redoing all the days
built on it. A **Healing Table** is **path-independent** — it separates
*change detection* from *period construction* and rebuilds the whole timeline
from source, so the result depends only on source data, not on load history.
Six steps:

1. **Effectivity table** — extract every actual change point from source
   (filter out non-changes; null-safe comparison).
2. **Time slices** — `LEAD()` to derive `valid_from`/`valid_to`.
3. **Join sources** — build a unified timeline, as-of join each source;
   document attribute ownership (which source wins per column).
4. **Hash** — a key-hash for identity and a row-hash for change detection
   (COALESCE NULLs to a sentinel so NULL ≠ '').
5. **Compress** — collapse consecutive identical states (islands-and-gaps),
   only when both temporally contiguous and row-hash-equal.
6. **Validate** — the temporal-integrity tests above, before publish.

The payoff: fix the logic, reprocess the range, and you get exactly what a
full rebuild would — the dimension "heals" accumulated drift. Use it when you
have full source history and rebuild time is acceptable; keep plain
incremental for very high volume or real-time.

## Template

For pseudo-SQL scaffolds of all six steps (effectivity → time slices → join
→ hash → compress → validate), see
[HEALING-TABLE-TEMPLATE.md](./HEALING-TABLE-TEMPLATE.md). Keep them
tool-agnostic — swap the windowing/hashing functions for your engine's
(consult `docs/agents/platform.md` if present).
