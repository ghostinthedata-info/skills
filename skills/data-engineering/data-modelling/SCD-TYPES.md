# SCD Types 0–7 — Choosing a History Policy

When a dimension attribute changes, what do you do with the old value? Pick
**per attribute, not per table** — defaulting everything to Type 2 creates
huge tables with no analytical value. (Folded in from the former
*slowly-changing-dimensions* skill.)

## The types (Kimball)

* **Type 0** — never changes (original credit score, most date attributes).
* **Type 1** — overwrite. Simple; destroys history. Use when no one needs
  the old value. Kimball's caveat: an overwrite silently invalidates
  pre-built aggregates/OLAP cubes and makes the *same* historical report
  return different totals before vs. after the change — fine for a genuine
  correction, dangerous if anyone relies on point-in-time consistency.
  Implementation: [SCD1.md](./SCD1.md).
* **Type 2** — add a new row with a new surrogate key,
  `valid_from`/`valid_to`, and `is_current`. The workhorse for point-in-time
  truth ("what was their region when they ordered?"). Costs row growth.
  Implementation: [SCD2.md](./SCD2.md); rebuilding history:
  [BACKFILLING.md](./BACKFILLING.md).
* **Type 3** — add a "previous value" column. For one-off alternate-reality
  comparisons (a single re-org), not general history.
* **Type 4** — split fast-changing attributes into a **mini-dimension** so
  the base dimension stays stable (see [DIMENSIONS.md](./DIMENSIONS.md)).
* **Type 5 / 6 / 7** — hybrids (4+1, 1+2, dual current/historical). Powerful
  but rarely needed; don't reach for them before confirming Type 1/2 can't
  do the job — that's premature optimisation.

## Deciding, attribute by attribute

Ask of each changing attribute: *does anyone need to know its value as of a
past date?*

* Yes → **Type 2**.
* Only the latest value matters → **Type 1**.
* It never changes → **Type 0**.
* Only "before vs after one known change" → **Type 3**.
* It changes so often that Type 2 would explode the dimension → **Type 4**.

Record the chosen type beside each attribute (column docs or the model's
metadata) so the next engineer doesn't have to rediscover it.

## Alternative to Type 2: periodic full snapshots

When storage is cheap and the dimension is small to medium, a dated full copy
per day or week (partitioned by snapshot date) can replace Type 2. History
queries join on the snapshot date, there's no merge logic to get wrong, and a
bad day is fixed by re-taking that snapshot ("compute is cheap, storage is
cheap, engineering time is expensive"). The costs: storage grows with
entities × periods, changes between snapshots are invisible, and an "as of"
question resolves to the nearest snapshot, not the exact instant. Prefer
Type 2 when you need exact change times or the dimension is large and changes
slowly. Snapshots are also a good *source* for a Type 2 — diff consecutive
ones ([BACKFILLING.md](./BACKFILLING.md)).
