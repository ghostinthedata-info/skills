# Dimension Design

Dimensions carry the context — the who/what/where/when/why/how — that gives a
measurement meaning. (Folded in from the former *dimensional-modeling*
skill.)

## Dimension design rules

* Wide, denormalised, descriptive. Don't snowflake into 3NF — it kills
  star-join performance and adds user-perceived complexity (Kimball).
* Every dimension gets a **surrogate key**; keep the natural/business key as
  a column for lineage (see [KEYS.md](./KEYS.md) for the full decision rules).
* Handle change with the right SCD type per attribute (see
  [SCD-TYPES.md](./SCD-TYPES.md); default: Type 1 overwrite unless consumers
  need point-in-time truth, then Type 2).
* Give every dimension an "unknown"/ghost row so facts never lose rows on
  join.

## Dimension techniques (reach for these by name)

* **Role-playing** — one physical dimension referenced multiple times in one
  fact under different roles (order date, ship date, delivery date all point
  at `dim_date`). Expose a view/alias per role so column names read clearly.
* **Junk dimension** — collapse a handful of low-cardinality flags and
  indicators (status, yes/no options) into one small dimension of the observed
  combinations, instead of scattering cryptic flags on the fact.
* **Mini-dimension** — split fast-changing attributes (e.g. customer
  age-band, credit score) out of a large dimension into their own small
  dimension so the base dimension stays stable (this is SCD Type 4).
* **Outrigger** — a dimension referenced by another dimension (a date
  attribute inside `dim_customer`). Use sparingly; it's a controlled,
  permissible bit of snowflaking, not a licence to normalise.
* **Bridge table** — resolve a **multivalued** relationship (a patient with
  several diagnoses, an account with multiple holders) with a group/bridge
  table carrying allocation/weighting factors so measures don't double-count.
* **Degenerate dimension** — a dimension key with no attributes (order number)
  kept on the fact row; don't build a table for it.

## The date dimension — generate it

Every fact table needs a date dimension, and it's the one dimension you build
rather than source. Generate it: one row per day across the full range your
facts can touch (with headroom), carrying the calendar and fiscal attributes
people slice by — day of week, week, month, quarter, fiscal period,
`is_weekend`, holidays from a maintained calendar — plus a ghost row for
unknown dates. It's a reference dimension: built once and re-run only to
extend the range or add attributes (a new holiday calendar). Audit it before
publish like any other table: one row per day in the range, no gaps, a unique
date key.

## Conformed dimensions & the bus matrix

* A **conformed dimension** (date, customer, product) shares identical keys
  and meaning across fact tables, enabling "drill across." Define it **once,
  with the business**, and reuse it — this is the integration backbone.
* Build the **bus matrix**: rows = business processes, columns = dimensions,
  shaded cell = "this dimension applies." It's your roadmap and your
  prioritisation tool — implement one row (process) at a time.

## Aggregates

Build aggregate fact tables only for proven-slow, frequently-hit rollups;
keep them at a declared grain conformed to the atomic fact. They're a
performance tactic, not a modeling layer.
