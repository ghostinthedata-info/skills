---
name: fact-table-design
description: Choose the right fact-table grain and type — transaction, periodic snapshot, accumulating snapshot — and classify each measure as additive, semi-additive, or non-additive. Covers factless facts, degenerate dimensions, and null/measure discipline. Use when modeling a business process into facts or when a fact table is hard to aggregate correctly.
---

# Fact Table Design

Facts hold the measurements; everything else is context. Get the **grain** and
the **type** right and aggregation becomes trivial; get them wrong and every
query downstream is a workaround. This is the deep dive behind the four-step
process in `dimensional-modeling` (see it if installed for the modeling flow).

## Declare the grain first (non-negotiable)

State what **one fact row** means in business terms — "one row per order
line", "one row per daily account balance", "one row per claim lifecycle".
Choose the **most atomic** grain the source supports: atomic facts answer
questions you haven't thought of yet and can always roll up; pre-aggregated
facts can't drill down. Never mix grains in one table. A fuzzy grain is the #1
fact-design failure — don't pick a type or a column until the grain is one
unambiguous sentence.

## The three fact-table types

* **Transaction** — one row per measurement event, at the moment it happens.
  Most common, most atomic, most flexible. Rows are inserted, never updated.
  Default to this unless the question demands otherwise.
* **Periodic snapshot** — one row per entity per regular period (daily balance,
  monthly subscription state). Answers "what was the state on day X?" cheaply
  when reconstructing it from transactions would be expensive. Predictable,
  dense — a row exists every period whether or not anything changed.
* **Accumulating snapshot** — one row per workflow instance, **updated in
  place** as it passes pipeline milestones (ordered → picked → shipped →
  delivered). Multiple date FKs, one per milestone, plus lag measures between
  them. Use for processes with a well-defined start, end, and finite steps.

Most processes warrant a transaction grain *and* a complementary snapshot —
they answer different questions. They are not alternatives to choose between.

## Measure additivity (mark every measure)

* **Additive** — sums correctly across **all** dimensions (quantity, amount).
  The most useful kind; aim for these.
* **Semi-additive** — sums across some dimensions but **not time** (account
  balances, inventory levels, headcount). Aggregate across time with an
  average or period-end value, never `SUM`.
* **Non-additive** — must never be summed (ratios, percentages, unit prices,
  temperatures). Store the **fully additive components** (numerator and
  denominator) and compute the ratio at query time, not the ratio itself.

Document additivity next to each measure; it's the contract that stops someone
`SUM`-ing a balance and shipping a wrong number.

## Factless fact tables

A fact table with no numeric measure — the **event itself** is the fact.

* **Event tracking** — student attended class, promotion was applied. Count
  rows; a `COUNT(*)` is the measure.
* **Coverage** — records what *could* have happened so you can find what
  *didn't* (products on promotion that recorded no sales). Without coverage,
  absence is invisible.

## Degenerate dimensions

A dimension key with no dimension table — typically a transaction identifier
(order number, ticket number) kept **on the fact row** because it has no
attributes of its own but is needed for grouping and operational lineage.
Don't manufacture a single-column dimension table for it.

## Rules & anti-patterns

* Foreign keys to dimensions are **surrogate keys** (see `keys` if installed);
  never join facts on natural keys.
* Every dimension FK points at a real row — route unknowns to the dimension's
  ghost/"unknown" row (key `-1`) so a fact is never dropped on join.
* Don't put descriptive text on the fact (it belongs on a dimension) and don't
  put measures on a dimension.
* NULL is fine for a missing **measure**; NULL is never allowed in a
  **foreign key** — use the ghost row instead.
* Pick the SCD policy per dimension attribute, not on the fact (see
  `slowly-changing-dimensions` if installed).
* For point-in-time reporting, carry the **durable key** on the fact alongside
  the surrogate so you can report all history by current attributes.

## Template

If `dimensional-modeling` is installed, its `STAR-SCHEMA-TEMPLATE.md` has grain
statements and tool-agnostic DDL skeletons for each fact type. Otherwise write
the grain as one sentence, then a `CREATE TABLE` with the FK columns to each
dimension plus the measures, and a separate degenerate-dimension column for the
transaction id. Substitute your engine's syntax (consult `docs/agents/platform.md`
if present) and use the naming from `CONTEXT.md`.

