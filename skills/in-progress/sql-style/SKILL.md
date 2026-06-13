---
name: sql-style
description: Write portable, readable SQL — ISO-standard syntax, consistent ISO-11179 naming, set-oriented formatting, and constraints in the schema. Use when establishing SQL conventions for a repo, reviewing query craft, or naming tables and columns.
---

# SQL Style

Code is read far more often than it is written, and SQL outlives the
application that issued it. Celko's discipline is simple: **name things by what
they are, write portable standard SQL, and format for a reader who thinks in
sets.** This is the *how it reads* companion to `sql-antipatterns` (what to
avoid) and `set-based-sql` (how to think) if installed. Adopt one convention
per repo and record it in `CONTEXT.md` so names mean one thing everywhere.

## Naming (ISO-11179 data elements)

* **Name the data element, not the program variable.** A column name is a
  global, shared fact: `<class>_<attribute>_<role>` — e.g. `order_nbr`,
  `birth_date`. No `my_`, no table-name prefixes, no Hungarian type tags.
* **Tables and views are sets — name them with a collective or plural noun**
  (`Personnel`, `OrderLines`), never a singular ("one row") or a vague
  "…Table"/"…File" suffix that betrays file-system thinking.
* **Columns are scalars — name them singular.** Reserve a small set of agreed
  **postfixes** that signal the attribute's role, and use them consistently:
  `_id` (identifier, one per table), `_nbr`/`_no` (a tag number, not a
  quantity), `_date`/`_dt`, `_cat` (category), `_seq` (sequence), `_qty`,
  `_amt`, `_pct`, `_name`, `_code`. Don't invent ad-hoc postfixes.
* **Use letters, digits, and `_` only; start with a letter.** Never end in `_`
  or use `__`. Avoid `$ # @` even where the engine allows them.
* **Never use reserved words or quoted/delimited identifiers.** Quoted names
  ("col with spaces") destroy portability and hide bad names.
* **Keep names reasonably short and pronounceable** (~18 chars is the classic
  ceiling); don't strip vowels into unreadable codes either.
* **One name, one meaning, everywhere.** The same attribute is spelled the same
  in every table; different attributes never share a name.

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

* **Reserved words UPPERCASE; identifiers lowercase** (or your repo's agreed
  case). Be consistent — case is the reader's syntax highlighter.
* **One clause to a line:** `SELECT` / `FROM` / `WHERE` / `GROUP BY` /
  `HAVING` / `ORDER BY` each start a line; align and indent their contents.
* **One column per line** in long `SELECT` lists; put the comma where your repo
  agrees (leading or trailing) and never mix.
* **Indent subqueries and joined tables** to show structure; line up `ON` and
  `AND`/`OR` predicates.
* **Comments explain *why*, not *what*** — use them for business rules and
  surprising constraints, not to narrate obvious SQL.

## The principle

The reader of your SQL is thinking in sets and may be on a different database
engine years from now. Name for the data, lean on the standard, push integrity
into the schema, and lay the statement out so its set logic is visible at a
glance. See `set-based-sql` if installed for the matching way of *thinking*.
