# ADR format

An ADR records one decision that's expensive to undo, so the next engineer
knows it was deliberate and doesn't "fix" it. ADRs live in `docs/adr/`,
numbered in order — `0001-<slug>.md`, `0002-<slug>.md` (take the highest
number there and add one). Create the folder with the first ADR.

## When a decision earns one

Write an ADR only when all three hold:

1. **Undoing it would cost real work** — a rebuild, a migration, re-agreeing
   things with consumers.
2. **A reader would otherwise wonder why**, or assume the opposite.
3. **There was a real alternative**, and you chose against it for a reason.

Easy to reverse, obvious, or forced? Skip it.

Decisions that usually qualify in data work:

* Event time or load time — for partitions, for validity intervals.
* The grain of a core fact table, or splitting two grains apart.
* Which system is the source of truth for an attribute.
* Full rebuild or incremental, and how often a heal runs.
* Keeping history for an attribute (Type 2) — or deciding not to.
* A deliberate departure from the pack's defaults ("this fact appends without
  replacing partitions, because …").
* A constraint the code can't show: a retention law, a contractual SLA, a
  vendor's rate limit.

## The shape

Short is the point. Most ADRs are a title and one paragraph:

```md
# Partition order facts by event date, not load date

Orders from the marketplace feed arrive up to ten days late, and month-end
totals must not move when the feed catches up, so late orders land in the
period they happened. Load-date partitions would be simpler to backfill but
would put late orders in the wrong month. Agreed 2026-03-02 with the finance
data owner.
```

Add a section only when it earns its place:

* **Status** — `accepted`, `superseded by 0007`, … once decisions start being
  revisited.
* **Options considered** — when the rejected option is likely to be suggested
  again.
* **Consequences** — when the knock-on effects aren't obvious (a backfill, a
  consumer change, a new test).

Don't edit a superseded decision. Write a new ADR that supersedes it, and set
the old one's status to point at the new one.
