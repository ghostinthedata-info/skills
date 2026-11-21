---
name: sql-style
description: Write portable, readable SQL in the house style — layer-prefixed model names (stg_, dim_, fct_), lowercase snake_case columns with role suffixes (_id, _at, _date) and is_/has_ booleans, one name and one type per attribute everywhere, standard syntax, constraints in the schema, and comments that carry the context the code can't. Use when establishing SQL conventions for a repo, reviewing query craft, or naming tables and columns.
metadata:
  internal: "true"
---

# SQL Style

Code is read far more often than it is written, and SQL outlives the
application that issued it. The discipline is simple: **name things by what
they are and the same way everywhere, write portable standard SQL, format for
a reader who thinks in sets, and write down the why.** This is the *how it reads* companion to `sql-antipatterns` (what to
avoid) and `set-based-sql` (how to think) if installed. Adopt one convention
per repo and record it in `CONTEXT.md` so names mean one thing everywhere.

## Naming — the house conventions

Record the convention once per repo (in `CONTEXT.md` or the style guide the
linter reads) so names mean one thing everywhere. The pack's default:

* **Models are named by layer, then entity**, lowercase snake_case, entity
  singular: `stg_<source>__<entity>` for a typed, renamed copy of one source
  table (`stg_billing__invoice`), `int_<entity>_<verb>` for intermediate steps
  if you use that layer, `dim_<entity>` for dimensions (`dim_customer`), and
  `fct_<process>` for facts (`fct_order_line`).
* **Columns are lowercase snake_case and singular.** Never camelCase, never
  quoted identifiers.
* **The suffix or prefix says the role:**
  * `_id` — an identifier: the table's own key, and every foreign key, which
    repeats the referenced column's name exactly (`customer_id` in every
    table that points at a customer). Not `_key`, not a bare `id`.
  * `_at` — a timestamp (`created_at`); `_date` — a date (`order_date`).
  * `is_` / `has_` — a boolean (`is_active`, `has_refund`).
  * Measures name what they hold, with the unit where it matters
    (`net_amount`, `line_count`, `discount_pct`).
* **One name, one type, one meaning — everywhere.** `customer_id` has the same
  data type in every model, and two different attributes never share a name.
  Keep a small naming dictionary (column → type → meaning) and check new models
  against it in review; a script can do the comparison.
* **Letters, digits and `_` only, starting with a letter.** No reserved words,
  no `__` except the `stg_` source separator, no trailing `_`. Keep names
  short enough to say aloud, without stripping vowels into codes.

## Portability

* **Write ISO-standard SQL; avoid proprietary syntax** unless you have a
  measured reason. Prefer `CASE`, `COALESCE`, standard `JOIN ... ON`, and ANSI
  date/string functions over vendor-specific equivalents.
* **Use explicit ANSI joins** (`INNER JOIN ... ON`), never comma-joins with
  join predicates buried in `WHERE`.
* **Compare types honestly** — don't rely on implicit casts; convert
  explicitly so behaviour is the same across engines.

## Schema discipline

* **Put integrity in the DDL, not the application:** `NOT NULL`, `CHECK`,
  `DEFAULT`, `UNIQUE`, `PRIMARY KEY`, `FOREIGN KEY`. The schema is the single
  enforcement point.
* **Declare `DEFAULT` and `NOT NULL`** for every column whose absence is
  meaningless; reserve `NULL` strictly for genuinely missing/inapplicable data.
* **Use `CHECK` constraints** to encode the rules you'd otherwise hope the app
  remembers; use **lookup tables** for value sets that change.
* **Name your constraints** so error messages and migrations are legible.

## Formatting

* **Reserved words UPPERCASE; identifiers lowercase.** Be consistent — case is
  the reader's syntax highlighter.
* **Pick one indentation width and one comma style for the repo, and let a
  formatter or linter enforce them** (sqlfluff, or your tool's equivalent). A
  style guide that says both "4 spaces" and "2 spaces" enforces neither.
* **One clause to a line:** `SELECT` / `FROM` / `WHERE` / `GROUP BY` /
  `HAVING` / `ORDER BY` each start a line; align and indent their contents.
* **One column per line** in long `SELECT` lists; put the comma where your repo
  agrees (leading or trailing) and never mix.
* **Indent subqueries and joined tables** to show structure; line up `ON` and
  `AND`/`OR` predicates.
* **Comments explain *why*, not *what*** — see below.

## Comments that carry context

SQL says what the query does; it can't say why it was written that way. A
comment earns its place when it carries what the code can't, and is
load-bearing for whoever inherits the model:

* **The rule and its source** — the business reason, and the agreement or
  document behind it.
* **The owner and the date** — who confirmed it, and when.
* **The upstream cause** of a workaround, with the ticket or incident.
* **What breaks if it's removed.**

```sql
-- Exclude status codes 1, 2 and 9: they're artefacts of the CRM sync firing
-- before an order is confirmed. Upstream fix deprioritised (DATA-3841).
-- Confirmed with Finance, 2024-12. Removing this filter double-counts orders.
WHERE status_code NOT IN (1, 2, 9)
```

When two models deliberately disagree — two churn thresholds for two
teams — say so in both, or someone will "fix" one to match the other.
Don't narrate obvious SQL; and when a rule can be a test, make it a test as
well as a comment.

## The principle

The reader of your SQL is thinking in sets and may be on a different database
engine years from now. Name for the data, lean on the standard, push integrity
into the schema, and lay the statement out so its set logic is visible at a
glance. See `set-based-sql` if installed for the matching way of *thinking*.
