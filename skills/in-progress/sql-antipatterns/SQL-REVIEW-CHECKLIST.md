# SQL review checklist

A copy-paste pass for reviewing a schema, migration, or query. Tick what
applies; for each unticked box, either fix it or write down why the exception
holds. Antipattern names are from Karwin's *SQL Antipatterns*.

## Schema / DDL

- [ ] **No comma-separated value columns** — multi-valued attributes live in an
      intersection table, one row per value. *(Jaywalking / Multicolumn)*
- [ ] **Hierarchies use the right model** — closure table, nested sets, or path
      enumeration for subtree queries; adjacency list only if level-at-a-time +
      recursive CTEs are enough. *(Naive Trees)*
- [ ] **Every table has a real key** — natural/compound key is declared
      `UNIQUE` even when a surrogate `id` exists. *(ID Required)*
- [ ] **Foreign keys are declared** (or, where the platform can't, a test
      enforces the relationship). *(Keyless Entry)*
- [ ] **No generic EAV table** for attributes that could be real columns.
- [ ] **No polymorphic `parent_id` + `parent_type`** in place of declarable FKs.
- [ ] **Money is `NUMERIC`/`DECIMAL`**, never `FLOAT`/`REAL`. *(Rounding Errors)*
- [ ] **`NOT NULL`, `CHECK`, `DEFAULT`** declared wherever the rule is known.
- [ ] **Volatile value lists live in lookup tables**, not in DDL. *(Magic Beans)*
- [ ] **External-file references** have a documented reconciliation/cleanup
      story (or the bytes are stored in-DB). *(Phantom Files)*

## Indexes

- [ ] Indexes match the real `WHERE` / `JOIN` / `ORDER BY` workload.
- [ ] Each index was **measured** (EXPLAIN) — none added "just in case",
      none missing on hot paths. *(Index Shotgun → MENTOR)*

## Queries

- [ ] **No `SELECT *`** and no column-less `INSERT` — columns are named.
      *(Implicit Columns)*
- [ ] **NULL handled correctly** — `IS NULL`/`IS NOT NULL`, `COALESCE`, no
      `= NULL`, no sentinel literals; `NOT IN` over NULL-able sets checked.
      *(Fear of the Unknown)*
- [ ] **`GROUP BY` lists every non-aggregate column**, or a window function is
      used instead. *(Ambiguous Groups)*
- [ ] **No `ORDER BY RAND()`** for sampling; no `LIKE '%x%'` for real search.
- [ ] **Big queries are decomposed** (CTEs / steps); no accidental Cartesian
      products inflating totals. *(Spaghetti Query)*

## Application boundary

- [ ] **User input is parameterised / bound**; identifiers allow-listed.
      *(SQL Injection)*
- [ ] **Passwords are salted one-way hashes**, never reversible. *(Readable
      Passwords)*
- [ ] **Surrogate-key gaps left alone** — no renumbering. *(Pseudokey
      Neat-Freak)*
- [ ] **SQL and migrations are in version control, reviewed, and tested.**
      *(Diplomatic Immunity / See No Evil)*
