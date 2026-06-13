---
name: set-based-sql
description: Think in sets, not loops — replace cursors and row-by-row procedural code with declarative constraints, window functions, GROUPING SETS/CUBE/ROLLUP, CASE, set operations, and auxiliary tables. Use when SQL is being written procedurally, a transform loops over rows, or a query could be expressed declaratively.
---

# Set-Based SQL

SQL's unit of work is the **set**, not the row. You *describe* the result you
want with a rule and let the engine produce it "all at once"; you do not walk
the data one element at a time. Celko's core test: **"ask how you'd specify it
in terms of sets, and you'll usually get the right answer."** This is the *how
to think* companion to `sql-style` (how to write) and `sql-antipatterns` (what
to avoid) if installed.

## Unlearn the file system

Four habits to drop — they're why procedural SQL is slow and wrong:

* **Schemas are not file sets; tables are not files.** The whole schema is the
  unit of work.
* **Rows are not records** — there is no physical order. `ORDER BY` is a
  property of a *cursor/result*, never of a table. Don't depend on insertion
  order.
* **Columns are not fields** — they have types, constraints, and a single
  meaning, not just a position.

## Decision rules

* **No cursors / row-by-row loops for set operations.** A cursor processes one
  row at a time and blocks the optimiser from parallelising; an `UPDATE` /
  `INSERT ... SELECT` / `MERGE` against a set is faster and clearer. Reach for
  a cursor only for genuinely sequential, non-relational work.
* **No app-side loops to do what a join does.** Looping in Python/Java to fetch
  related rows one query at a time is a cursor in disguise — express it as a
  single set query.
* **Push validation into declarative constraints.** `CHECK`, `FOREIGN KEY`,
  `UNIQUE`, `DEFAULT`, `NOT NULL` enforce rules once, for every writer — not
  re-implemented (and forgotten) in each application.
* **Replace procedural branching with `CASE`.** A `CASE` expression is a
  value-returning, set-based conditional; use it instead of looping with
  if/then to compute a column.
* **Aggregate with the right tool:** plain `GROUP BY` for one grouping;
  **`GROUPING SETS` / `ROLLUP` / `CUBE`** for subtotals and crosstabs in one
  pass instead of `UNION`-ing many queries.
* **Use window (OLAP) functions** for running totals, rankings, moving
  averages, and per-partition calculations — they avoid self-joins and
  correlated subqueries, and keep detail rows.
* **Use set operators** — `UNION`/`UNION ALL`, `INTERSECT`, `EXCEPT` — to
  combine result sets, rather than procedurally merging them. Prefer
  `UNION ALL` when you know rows are already distinct.
* **Keep an auxiliary Calendar table and a Numbers/Sequence table.** They turn
  "generate a row per day" or "explode a range" from a loop into a join. Build
  them once; join to them forever.
* **Normalise first.** Most "I need a loop" problems are unnormalised designs:
  a fact represented more than once, or a repeating group that should be rows.
  Fix the model and the set query falls out (see `dimensional-modeling` /
  `keys` if installed).

## NULLs and three-valued logic

* SQL logic is **true / false / unknown**. Any comparison with `NULL` yields
  *unknown*, and `WHERE` keeps only *true* rows — so `x = NULL` never matches;
  use `IS NULL` / `IS NOT NULL`.
* `NOT IN (subquery)` returns no rows if the subquery yields any `NULL` — a
  classic silent bug. Prefer `NOT EXISTS`, which is unaffected.
* Aggregates skip `NULL`s (except `COUNT(*)`); know whether that's what you
  want before reporting the number.

## Temporal / interval modelling

* Model durations as **half-open intervals** `[start, end)` so adjacent periods
  meet without overlapping or leaving gaps.
* Test overlap with the standard rule — two intervals overlap when
  `a.start < b.end AND b.start < a.end` — rather than enumerating cases or
  looping over dates. (Allen's interval relations name the full set of
  before/meets/overlaps/during cases if you need them.)

## The principle

If you're writing a loop, a cursor, or "fetch then loop in the app," stop and
ask what *set* you're really describing and what *rule* defines it. Express
that rule once — as a constraint, a join, an aggregate, or a window — and let
the engine do the iteration.
