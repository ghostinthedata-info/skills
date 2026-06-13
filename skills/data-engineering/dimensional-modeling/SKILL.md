---
name: dimensional-modeling
description: Model tables into facts, dimensions, and aggregates using Kimball's method — grain declaration first, then fact-table type selection, dimension design, conformed dimensions, and the bus matrix. Use when the user is designing analytics/reporting tables, a star schema, or a gold/presentation layer.
---

# Dimensional Modeling

Kimball's brilliance: **separate measurements (facts) from context
(dimensions).** It powers the overwhelming majority of enterprise data
warehouses and is more widely used today than ever (Ghost in the Data, "Why
Dimensional Modeling Isn't Dead"). Follow the four steps in order.

## The four-step design process (do not reorder)

1. **Select the business process.** A low-level activity that produces
   measurable events: taking an order, shipping, a payment, a support call.
   Listen for the verb.
2. **Declare the grain.** State exactly what one fact row is, in business
   terms — "one row per order line." Choose the **most atomic** grain you
   can; it's the most flexible. A fuzzy grain is the #1 dimensional-design
   failure.
3. **Identify the dimensions.** The who/what/where/when/why/how that gives
   the measurement context.
4. **Identify the facts.** The numeric measurements true to the grain.

## Fact table types

* **Transaction** — one row per event. Most common, most atomic.
* **Periodic snapshot** — one row per entity per regular period (daily
  balance, monthly subscription state). For "what was the state on day X."
* **Accumulating snapshot** — one row per workflow instance, updated as it
  passes milestones (order placed → shipped → delivered), with multiple date
  columns and lag measures.

Mark each fact as **additive / semi-additive / non-additive** (ratios and
balances are not freely summable). For the full treatment — declaring grain,
choosing the type, factless facts, and degenerate dimensions — see
`fact-table-design` if installed.

## Dimension design

* Wide, denormalised, descriptive. Don't snowflake into 3NF — it kills
  star-join performance and adds user-perceived complexity (Kimball).
* Every dimension gets a **surrogate key**; keep the natural/business key as
  a column for lineage (see `keys` if installed for the full decision rules).
* Handle change with the right SCD type per attribute (see
  `slowly-changing-dimensions` if installed; default: Type 1 overwrite unless
  consumers need point-in-time truth, then Type 2).
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
  dimension so the base dimension stays stable (this is SCD Type 4 — see
  `slowly-changing-dimensions` if installed).
* **Outrigger** — a dimension referenced by another dimension (a date
  attribute inside `dim_customer`). Use sparingly; it's a controlled,
  permissible bit of snowflaking, not a licence to normalise.
* **Bridge table** — resolve a **multivalued** relationship (a patient with
  several diagnoses, an account with multiple holders) with a group/bridge
  table carrying allocation/weighting factors so measures don't double-count.
* **Degenerate dimension** — a dimension key with no attributes (order number)
  kept on the fact row; don't build a table for it.

## Conformed dimensions & the bus matrix

* A **conformed dimension** (date, customer, product) shares identical keys
  and meaning across fact tables, enabling "drill across." Define it **once,
  with the business**, and reuse it — this is the integration backbone.
* Build the **bus matrix**: rows = business processes, columns = dimensions,
  shaded cell = "this dimension applies." It's your roadmap and your
  prioritisation tool — implement one row (process) at a time.
* For the enterprise treatment — conformed rollups, conformed facts,
  drill-across, and avoiding stovepipe marts — see `conformed-dimensions` if
  installed.

## Aggregates

Build aggregate fact tables only for proven-slow, frequently-hit rollups;
keep them at a declared grain conformed to the atomic fact. They're a
performance tactic, not a modeling layer.

## Template

For scaffolds of the four-step output — grain statement, bus matrix,
tool-agnostic dimension/fact/aggregate DDL skeletons, and a **dbt
`schema.yml` column-documentation** pattern (documenting each column's key
role, SCD type/effectivity, denormalisation, and measure additivity) — see
[STAR-SCHEMA-TEMPLATE.md](./STAR-SCHEMA-TEMPLATE.md). Substitute your
engine's syntax (consult `docs/agents/platform.md` if present) and use the
naming from `CONTEXT.md`.
