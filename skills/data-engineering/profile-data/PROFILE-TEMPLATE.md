# Profiling Query Template

Pseudo-SQL scaffolds for each profiling section in the skill, plus the
baseline report shape. 

These are **tool-agnostic skeletons**, not runnable code. Substitute your
engine's functions (consult `docs/agents/platform.md` if present) and replace
`{{table}}` / `{{col}}` / `{{key}}` placeholders. Run each section in order.

---

## 1. Shape

```sql
-- row count (+ per partition if partitioned)
SELECT COUNT(*) AS row_count FROM {{table}};
SELECT {{partition_col}}, COUNT(*) FROM {{table}} GROUP BY {{partition_col}} ORDER BY 1;

-- declared schema; eyeball types, string caps, numeric precision
-- (information_schema.columns, or DESCRIBE {{table}}, per engine)
SELECT column_name, data_type, character_maximum_length,
       numeric_precision, numeric_scale
FROM information_schema.columns
WHERE table_schema = '{{schema}}' AND table_name = '{{table}}'
ORDER BY ordinal_position;

-- truncation trap: real max length vs declared cap, per string column
SELECT MAX(LENGTH({{col}})) AS observed_max_len FROM {{table}};
```

## 2. Cardinality

```sql
SELECT
  COUNT(*)                                              AS total,
  COUNT(DISTINCT {{col}})                               AS distinct_vals,
  ROUND(COUNT(DISTINCT {{col}}) * 100.0 / NULLIF(COUNT(*), 0), 2) AS distinct_pct
FROM {{table}};
-- distinct_pct ~100 -> candidate key; ~0 -> constant/low-signal;
-- mid-range -> categorical (capture the value set for accepted-values tests).
-- On large tables use your engine's approximate distinct count here, and an
-- exact COUNT(DISTINCT ...) only on the columns that look like keys.

-- capture a categorical value set (mid-range distinct_pct, non-PII only)
SELECT {{col}}, COUNT(*) AS n
FROM {{table}}
GROUP BY {{col}}
ORDER BY n DESC;
```

## 3. Key uniqueness (make-or-break)

```sql
-- must hold: COUNT(*) = COUNT(DISTINCT key). Surface a failure and STOP.
SELECT
  COUNT(*)                       AS rows,
  COUNT(DISTINCT {{key}})        AS distinct_keys,
  COUNT(*) - COUNT(DISTINCT {{key}}) AS dup_keys
FROM {{table}};

-- which keys duplicate (for the surfaced report)
SELECT {{key}}, COUNT(*) AS n
FROM {{table}}
GROUP BY {{key}}
HAVING COUNT(*) > 1
ORDER BY n DESC;

-- a nullable key is not a key
SELECT COUNT(*) AS null_keys FROM {{table}} WHERE {{key}} IS NULL;
```

For a composite key, `GROUP BY col_a, col_b, ...` and apply the same checks.

## 4. Completeness

```sql
SELECT
  COUNT(*)                                          AS total,
  COUNT(*) - COUNT({{col}})                         AS null_count,
  ROUND((COUNT(*) - COUNT({{col}})) * 100.0 / NULLIF(COUNT(*),0), 2) AS null_pct,
  SUM(CASE WHEN TRIM({{col}}) = '' THEN 1 ELSE 0 END)              AS empty_string,
  SUM(CASE WHEN UPPER(TRIM({{col}})) IN ('N/A','NULL','-','NONE','UNKNOWN')
          THEN 1 ELSE 0 END)                        AS sentinel_count
FROM {{table}};
-- for date columns, also count placeholder dates:
--   SUM(CASE WHEN {{date_col}} = DATE '1900-01-01' THEN 1 ELSE 0 END) AS zero_dates
-- decide per column: is null expected, or a defect?

-- every spelling of missing, one row each, so the convention can be agreed
SELECT TRIM({{col}}) AS spelling, COUNT(*) AS n
FROM {{table}}
WHERE {{col}} IS NULL
   OR UPPER(TRIM({{col}})) IN ('', 'NULL', 'NONE', '\N', 'N/A', 'NA', '#N/A',
                               '-', 'NAN', '(NULL)', 'UNKNOWN', 'TBD')
GROUP BY TRIM({{col}})
ORDER BY n DESC;

-- completeness per segment: the overall figure can hide the segment that matters
SELECT {{segment_col}},
       COUNT(*)                                                    AS total,
       ROUND(COUNT({{col}}) * 100.0 / NULLIF(COUNT(*), 0), 2)      AS complete_pct
FROM {{table}}
GROUP BY {{segment_col}}
ORDER BY complete_pct;
```

## 5. Distribution & outliers

```sql
-- numeric: spread + impossible values
SELECT
  MIN({{col}}) AS min_v,
  MAX({{col}}) AS max_v,
  AVG({{col}}) AS mean_v,
  -- quartiles: APPROX_PERCENTILE / PERCENTILE_CONT per engine
  APPROX_PERCENTILE({{col}}, 0.25) AS p25,
  APPROX_PERCENTILE({{col}}, 0.50) AS median,
  APPROX_PERCENTILE({{col}}, 0.75) AS p75
FROM {{table}};

-- flag impossibles (negative ages, future dates, etc.)
SELECT COUNT(*) AS impossible FROM {{table}}
WHERE {{col}} < 0 OR {{date_col}} > CURRENT_DATE;
```

> Use null-safe comparison (`IS DISTINCT FROM` / your dialect's equivalent)
> whenever NULLs are in play.

## 6. Types, formats, sensitivity

```sql
-- regex-scan for PII patterns; classify by sensitivity
SELECT
  SUM(CASE WHEN {{col}} ~ '^[^@]+@[^@]+\.[^@]+$' THEN 1 ELSE 0 END) AS looks_like_email,
  SUM(CASE WHEN {{col}} ~ '^\+?[0-9 ()-]{7,}$'    THEN 1 ELSE 0 END) AS looks_like_phone
FROM {{table}};
-- also confirm date formats and numeric precision match assumptions

-- time-zone semantics: list the timestamp columns and their exact types
-- (without a zone, with a zone, or session-local) before trusting any time
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = '{{schema}}' AND table_name = '{{table}}'
  AND data_type LIKE 'TIMESTAMP%';
```

```sql
-- content vs declared type, per string column
SELECT
  COUNT({{col}})                                                         AS non_null,
  SUM(CASE WHEN {{col}} ~ '^[0-9]+$' THEN 1 ELSE 0 END)                  AS digits_only,
  SUM(CASE WHEN {{col}} ~ '^0[0-9]+$' THEN 1 ELSE 0 END)                 AS leading_zero,
  SUM(CASE WHEN {{col}} <> TRIM({{col}}) THEN 1 ELSE 0 END)              AS padded,
  SUM(CASE WHEN {{col}} ~ '[^ -~]' THEN 1 ELSE 0 END)                    AS non_printable_or_non_ascii,
  SUM(CASE WHEN {{col}} ~ '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4}$' THEN 1 ELSE 0 END) AS slash_dates
FROM {{table}};
-- digits_only near non_null → a numeric code: keep it a string, or zeros vanish
-- non_printable_or_non_ascii → look for non-breaking / zero-width spaces, a BOM
-- slash_dates → ambiguous day/month order; agree ISO 8601 with the source
```

> `~` is POSIX regex match in some engines; use your dialect's operator or
> function (`RLIKE`, `REGEXP_LIKE`, `REGEXP_CONTAINS`, …). `[^ -~]` matches
> anything outside printable ASCII — legitimate accented text shows up too, so
> inspect the matches before calling them defects.

---

## 7. Baseline report shape (`docs/profiles/<table>.md`)

Write this **only with the user's consent**. Aggregates only — never sample
rows or record-level values. PII columns (flagged in step 6) get statistics
only: no observed value sets, no min/max for free-text identifiers.

```markdown
# Profile: <table>

Profiled-at: 2026-01-15
Source: <where this data came from>
Verdict: safe to build on  |  not yet (keys fail / anomalies)

## Shape
- Rows: 1,240,318
- Columns: 24
- Partitioned by: load_date (≈ 4,100 rows/day)

## Candidate keys
| Key            | Unique? | Nullable? | Implied grain           |
|----------------|---------|-----------|-------------------------|
| order_id       | PASS    | no        | one row per order       |
| (order_id, ln) | PASS    | no        | one row per order line  |

## Cardinality & completeness
| Column     | Distinct% | Null% | Classification        |
|------------|-----------|-------|-----------------------|
| status     | 0.004     | 0     | categorical (6 values)|
| email      | 98.2      | 1.1   | PII — stats only      |

## Accepted value sets (non-PII categoricals)
- status: active, cancelled, pending, refunded, shipped, returned

## Distributions (non-PII numerics)
| Column      | Min | P25 | Median | P75 | Max   |
|-------------|-----|-----|--------|-----|-------|
| order_total | 0   | 18  | 42     | 96  | 9,940 |

## Anomalies found
- 312 rows with order_total = 0 (refunds?) — confirm with business
- email observed max length 254 vs declared VARCHAR(255) — near cap

## Columns that need tests (hand to test-data)
| Column      | DQ dimension   | Test                        | Severity |
|-------------|----------------|-----------------------------|----------|
| order_id    | Uniqueness     | unique, not null            | error    |
| status      | Validity       | accepted values             | warn     |
| order_total | Reasonableness | non-negative                | error    |
| order_total | Consistency    | volume/variance vs baseline | warn     |
```

This baseline is what `test-data` (if installed) turns into volume/variance
thresholds, and what drift detection diffs against on the next load.
