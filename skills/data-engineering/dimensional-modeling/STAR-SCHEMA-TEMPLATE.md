# Star Schema Template

Scaffolds for Kimball's four-step output: the grain statement, the bus
matrix, and tool-agnostic dimension/fact DDL skeletons. Substitute your
engine's syntax (consult `docs/agents/platform.md` if present). Use the
naming defined in `CONTEXT.md` for every business concept.

---

## 1. Grain statement (write this first, in one sentence)

> **One row per `<business process event at its most atomic level>`.**
>
> e.g. "One row per order line." / "One row per daily account balance." /
> "One row per support-ticket lifecycle."

Everything below hangs off this. A fuzzy grain is the #1 dimensional-design
failure — don't proceed until it's a single, unambiguous sentence.

---

## 2. Bus matrix (the roadmap)

Rows = business processes. Columns = conformed dimensions. Mark `X` where a
dimension applies. Build **one row (process) at a time**.

| Business process    | Date | Customer | Product | Store | Employee | Promotion |
|---------------------|:----:|:--------:|:-------:|:-----:|:--------:|:---------:|
| Orders              |  X   |    X     |    X    |   X   |    X     |     X     |
| Shipments           |  X   |    X     |    X    |   X   |          |           |
| Returns             |  X   |    X     |    X    |   X   |          |     X     |
| Payments            |  X   |    X     |         |       |          |           |

A dimension shared across rows (same key, same meaning) is **conformed** —
define it once with the business; it's the integration backbone that enables
drill-across.

---

## 3. Dimension DDL (skeleton)

```sql
CREATE TABLE dim_customer (
  customer_key        BIGINT       NOT NULL,   -- surrogate key (PK)
  customer_id         VARCHAR      NOT NULL,   -- natural/business key (lineage)
  customer_name       VARCHAR,
  segment             VARCHAR,                 -- wide, denormalised, descriptive
  region              VARCHAR,
  -- SCD2 columns (only if consumers need point-in-time truth) --
  valid_from          TIMESTAMP    NOT NULL,
  valid_to            TIMESTAMP    NOT NULL,   -- high date 9999-12-31 for current
  is_current          BOOLEAN      NOT NULL
);

-- Every dimension gets an "unknown"/ghost row so facts never lose rows on join:
INSERT INTO dim_customer (customer_key, customer_id, customer_name, is_current,
                          valid_from, valid_to)
VALUES (-1, 'UNKNOWN', 'Unknown', TRUE, '1900-01-01', '9999-12-31');
```

- Surrogate key on every dimension; keep the natural key as a column (see
  `keys` if installed).
- Don't snowflake into 3NF — wide and denormalised wins for star-join speed.
- Pick the SCD type **per attribute**, not per table (see
  `slowly-changing-dimensions` if installed; default Type 1 unless
  point-in-time truth is needed, then Type 2).

---

## 4. Fact DDL (skeleton) — pick the type

```sql
-- TRANSACTION fact: one row per event (most common, most atomic)
CREATE TABLE fct_order_line (
  -- dimension foreign keys (surrogate keys) --
  date_key            INT          NOT NULL,
  customer_key        BIGINT       NOT NULL,
  product_key         BIGINT       NOT NULL,
  store_key           BIGINT       NOT NULL,
  -- degenerate dimension (lives on the fact) --
  order_id            VARCHAR      NOT NULL,
  order_line_no       INT          NOT NULL,
  -- measures (true to the grain) --
  quantity            INT,                     -- additive
  gross_amount        NUMERIC(18,2),           -- additive
  discount_amount     NUMERIC(18,2),           -- additive
  unit_price          NUMERIC(18,2)            -- non-additive (don't SUM)
);
```

Mark each measure **additive / semi-additive / non-additive**. Balances and
ratios are not freely summable.

Other fact types:
- **Periodic snapshot** — one row per entity per regular period (daily
  balance, monthly subscription state). For "what was the state on day X."
- **Accumulating snapshot** — one row per workflow instance, updated as it
  passes milestones; multiple date FKs (order_date_key, ship_date_key,
  deliver_date_key) and lag measures between them.

---

## 5. Aggregates (only when proven slow)

Build an aggregate fact only for a frequently-hit, measured-slow rollup. Keep
it at a declared grain conformed to the atomic fact. It's a performance
tactic, not a modeling layer.

```sql
-- e.g. daily product sales, conformed to fct_order_line
CREATE TABLE agg_product_daily_sales (
  date_key            INT          NOT NULL,
  product_key         BIGINT       NOT NULL,
  total_quantity      BIGINT,                  -- additive rollup only
  total_gross_amount  NUMERIC(18,2)
);
```

---

## 6. dbt column documentation (`schema.yml`)

If you use dbt, the DDL skeletons above carry no documentation — the model
`.yml` is where a reader learns each column's **role** in the star. Document
the role explicitly, because it's invisible from the type alone: a `BIGINT`
could be a surrogate key, a degenerate dimension, or an additive measure.
State, per column: its key role (surrogate / natural / degenerate / FK), its
historisation (SCD type, high-date/effectivity), whether it's a
wide/denormalised descriptor, the measure additivity, and any business rule.

```yaml
version: 2

models:
  - name: dim_customer
    description: >
      Customer dimension. Wide, denormalised, descriptive. SCD2 — one row per
      customer per change period; join facts on customer_key, not customer_id.
    columns:
      - name: customer_key
        description: "Surrogate key (PK). Meaningless integer; fact FKs point here."
        # tests: unique + not_null (see test-data if installed)

      - name: customer_id
        description: "Natural/business key from the source. Kept for lineage; NOT the join key."

      - name: segment
        description: "Wide denormalised descriptor. Do not snowflake into its own table."

      - name: valid_from
        description: "SCD2 effectivity start (left-closed). Row is valid for valid_from <= t < valid_to."

      - name: valid_to
        description: "SCD2 effectivity end (right-open). High date 9999-12-31 = current row."

      - name: is_current
        description: "SCD2 current-row flag. Exactly one TRUE per durable key."

  - name: fct_order_line
    description: "Transaction fact. Grain: one row per order line."
    columns:
      - name: customer_key
        description: "FK to dim_customer (surrogate). NULL maps to the -1 ghost row."

      - name: order_id
        description: "Degenerate dimension — order number kept on the fact, no dim table."

      - name: gross_amount
        description: "Measure — ADDITIVE. Safe to SUM across all dimensions."

      - name: unit_price
        description: "Measure — NON-ADDITIVE. Do not SUM; average or recompute instead."

      - name: account_balance
        description: "Measure — SEMI-ADDITIVE. Additive across all dims except date (snapshot)."
```

Keep these descriptions next to the SCD and additivity decisions they encode —
when the SCD type or grain changes, update the description in the same commit.
Pair `unique`/`not_null` tests on the surrogate key (see `test-data` if
installed); the description says *what* a column is, the test enforces it.
