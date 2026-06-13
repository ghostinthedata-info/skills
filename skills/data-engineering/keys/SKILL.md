---
name: keys
description: Choose and design keys correctly — business/natural, surrogate, composite, and durable ("super-natural") keys. Use when designing any table's primary key, fact-to-dimension joins, SCD2 dimensions, or when diagnosing fan-out/duplicate-row problems caused by bad keys.
---

# Keys

Most "the numbers are wrong" bugs are key bugs. Get these right up front.

## The key types

* **Natural / business key** — the identifier the business uses (employee
  number, order code, VIN). Meaningful, but **outside your control** and
  prone to change, reuse, and collision.
* **Surrogate key** — a meaningless system-generated integer (or hash) that
  is the table's primary key. Stable, compact, fast to join. Use it as the
  fact→dimension foreign key.
* **Composite key** — multiple columns that together identify a row
  (order_id + line_no). Common in source data; profile to confirm it's
  actually unique before trusting it.
* **Durable / "super-natural" key** — a persistent identifier that ties all
  versions of an entity together even when the natural key changes or the
  entity is re-created. In an SCD2 dimension you have all three: the
  surrogate (per version, the FK), the natural key (lineage), and the durable
  key (joins all versions of one entity).

## Decision rules

* **Always** surrogate-key dimensions in a Kimball model, especially for SCD2
  (each version needs its own key) and conformed dimensions across sources.
* Keep the natural/business key as a column for lineage and debugging — never
  throw it away, but don't join facts on it.
* Add the **durable key to the fact table too**, alongside the surrogate, so
  you can report all history by current attributes with one join.
* In Data Vault, identify the **true business key** for the hub (not the
  source PK) and hash it; reused business keys get resolved in the business
  vault.

## Naming

* Name a key after **what it identifies**, not the table it sits in:
  `customer_id`, not `id` or `cust_tbl_pk`. One `_id` per table for its
  identifier; foreign keys repeat the referenced column's name so joins are
  self-documenting (see `sql-style` if installed).
* Don't encode meaning, type tags, or position into the name — a surrogate is
  deliberately meaningless.

## Anti-patterns (call these out)

* **"ID Required"** — adding a surrogate `id` to *every* table by reflex, even
  when a sound natural or compound key exists, and then leaving that natural
  key un-enforced. The surrogate is a convenience, not a substitute: **still
  declare the natural key `UNIQUE`**, or you'll get duplicate rows that differ
  only by `id` (see `sql-antipatterns` if installed).
* **Exposed physical locators** — using a row's physical address, `ROWID`, or a
  bare auto-increment/`IDENTITY` as the *only* key and exposing it outside the
  database. Physical locators change on reload/migration; a logical key must
  back them.
* **Pseudokey neat-freak** — renumbering surrogate keys to "close the gaps."
  Gaps are harmless; renumbering breaks every reference. Leave them alone.
* Treating a nullable or non-unique column as a key → silent join fan-out.
  Always confirm `COUNT(*) = COUNT(DISTINCT key)` and zero nulls (see
  `profile-data` if installed).
* Joining facts on the natural key → breaks the moment the source renumbers.
* Embedding business meaning in a surrogate (then someone parses it).
* Reusing a source PK as the warehouse key when the source can recycle it.
* Most warehouses don't enforce PK uniqueness — so **test** every key for
  unique + not-null in the pipeline; don't assume (see `test-data` if
  installed).

