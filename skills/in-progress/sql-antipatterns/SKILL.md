---
name: sql-antipatterns
description: Recognise and avoid the common SQL schema and query design traps — comma-separated lists, adjacency-only trees, missing foreign keys, EAV, polymorphic associations, FLOAT money, SELECT *, unplanned indexes, and broken NULL logic. Use when designing a schema, reviewing a migration, or diagnosing a query that's slow, wrong, or impossible to constrain.
---

# SQL Antipatterns

Most schema pain is self-inflicted: a design that felt convenient on day one
makes integrity, joins, and aggregation impossible on day one hundred. This is
Karwin's catalogue of the recurring traps. Each has a name, a tell, and a
founded fix — and a few *legitimate* exceptions, so the rule is "know when,"
not "never." Pairs with `sql-style` (how to write it) and `set-based-sql` (how
to think it) if installed.

## How to use this

When reviewing a schema or query, scan for the tells below. The presence of a
tell isn't proof — check the legitimate-use note before raising it. For a
copy-paste review pass see [SQL-REVIEW-CHECKLIST.md](SQL-REVIEW-CHECKLIST.md).

## Logical design traps

* **Jaywalking** — multiple values stuffed into one comma-separated column.
  *Tell:* `LIKE '%,3,%'`, "how long can the list get?", can't FK or count it.
  *Fix:* an intersection (junction) table, one row per value.
  *OK when:* the list is genuinely opaque text you never query into.
* **Naive Trees** — storing a hierarchy with only `parent_id` (adjacency
  list). *Tell:* recursive app-side loops to fetch a subtree; can't get all
  descendants in one query. *Fix:* pick by access pattern — **closure table**
  (most flexible, supports multi-parent), **nested sets** (fast subtree reads,
  slow writes), or **path enumeration** (`/1/4/6/`). Adjacency list is fine if
  your engine has recursive CTEs and you only walk a level at a time.
* **ID Required** — bolting a surrogate `id` onto every table by reflex.
  *Tell:* an `id` column sitting next to a perfectly good natural/compound key
  that is left un-enforced; duplicate rows that differ only by `id`. *Fix:*
  name the key after what it identifies, and **still declare the natural key
  UNIQUE**. Use a surrogate deliberately, not automatically (see `keys` if
  installed).
* **Keyless Entry** — no foreign-key constraints, "for flexibility/speed."
  *Tell:* orphaned rows, cleanup scripts, "the app guarantees it." *Fix:*
  declare FK constraints; let the database enforce referential integrity.
  *OK when:* the platform genuinely can't enforce them (some MPP warehouses) —
  then you **must** test the relationship instead (see `test-data`).
* **EAV (Entity-Attribute-Value)** — one generic `(entity, attribute, value)`
  table to store "any" attribute. *Tell:* everything is a string, no NOT NULL
  or type checks possible, monstrous self-join pivots. *Fix:* model real
  columns; for true variability use single-table/class-table inheritance, a
  semi-structured (JSON) column, or a serialized blob — chosen deliberately.
* **Polymorphic Associations** — one `parent_id` + `parent_type` pointing at
  many possible tables. *Tell:* a FK you can't declare because it could
  reference several tables. *Fix:* reverse it — an intersection table per
  parent, or a common supertable the children reference.
* **Multicolumn Attributes** — `tag1, tag2, tag3` repeated columns for one
  multi-valued attribute. *Tell:* "we need a fourth tag column." *Fix:* a
  dependent/intersection table, same as Jaywalking.

## Physical design traps

* **Rounding Errors** — `FLOAT`/`REAL` for money. *Tell:* totals off by a
  cent, `WHERE amount = 19.99` returns nothing. *Fix:* `NUMERIC`/`DECIMAL`
  with explicit precision and scale.
* **31 Flavors / Magic Beans** — hard-coding a fixed value list in a column
  definition (e.g. `CHECK status IN (...)`) when it changes often, or treating
  a model as nothing but an `id`. *Fix:* a lookup table you can extend with
  data, not DDL.
* **Index Shotgun** — guessing at indexes: indexing everything, nothing, or
  the wrong columns. *Tell:* indexes nobody uses, full scans on hot queries,
  no measurement. *Fix:* index for your actual `WHERE`/`JOIN`/`ORDER BY`
  workload — **M**easure, **E**xplain, **N**ominate, **T**est ("MENTOR").
  See `performance-tuning` if installed.
* **Phantom Files** — storing only a filesystem path to data the database
  should own. *Tell:* `DELETE` leaves orphan files, no transactional rollback,
  no backup consistency. *Fix:* weigh storing the bytes (BLOB) vs. accepting
  the path with a documented reconciliation/cleanup process.

## Query traps

* **Fear of the Unknown** — using a literal (`-1`, `'N/A'`, `''`) instead of
  `NULL`, or comparing to NULL with `=`. *Tell:* `WHERE x = NULL` (always
  false), aggregates that silently skip rows, `NOT IN` over a NULL-able set
  returning nothing. *Fix:* use `NULL` for missing, `IS NULL`/`IS NOT NULL`,
  and `COALESCE`; remember `NULL` is unknown under three-valued logic, not a
  value. See `set-based-sql` if installed.
* **Ambiguous Groups** — selecting non-aggregated columns not in `GROUP BY`.
  *Tell:* a query that returns an arbitrary row per group. *Fix:* group by
  every non-aggregate column, or use a window function / a join to the
  per-group aggregate.
* **Random Selection** — `ORDER BY RAND()` to pick a random row. *Tell:* full
  sort of the whole table for one row. *Fix:* pick a random key in a range, or
  offset by a random count.
* **Poor Man's Search Engine** — `LIKE '%term%'` / full-table pattern scans for
  text search. *Fix:* a real full-text index, or a dedicated search engine.
* **Spaghetti Query** — solving a whole problem in one giant statement.
  *Tell:* cartesian blow-ups, unintended row multiplication, nobody can read
  it. *Fix:* split into steps (CTEs / temp tables), or run separate queries
  and combine — Cartesian products are the usual cause of wrong totals.
* **Implicit Columns** — `SELECT *` and column-less `INSERT`. *Tell:* breakage
  when a column is added/reordered, wasted I/O, broken views. *Fix:* name the
  columns you actually need, always.

## Application-layer traps (flag, don't fix here)

* **Readable Passwords** — storing plaintext or reversible passwords. *Fix:*
  salted one-way hash; never email a password, offer reset.
* **SQL Injection** — concatenating user input into SQL. *Fix:* parameterised
  queries / bound variables, always; allow-list anything that can't be a
  parameter (identifiers, sort direction).
* **Pseudokey Neat-Freak** — renumbering surrogate keys to "fill the gaps."
  *Fix:* leave gaps; surrogate keys are meaningless by design.
* **See No Evil / Diplomatic Immunity** — ignoring return codes and error
  messages, or exempting SQL from version control, testing, and review.
  *Fix:* read errors; treat SQL and migrations as code (review + tests + VCS).

## The discipline

Most of these collapse into three habits: **declare integrity in the database**
(keys, FKs, NOT NULL, CHECK, correct types), **model multi-valued and
hierarchical data as rows, not strings or repeated columns**, and **be explicit**
(named columns, measured indexes, parameterised input). When a platform can't
enforce a constraint, replace it with a test — don't drop the guarantee.
