# Reconciliation Template

Copy-paste scaffolds for the escalating battery, the permanent tests the
keepers graduate into, and the per-model plan. They're portable SQL — swap in
your engine's functions where marked. **Assertion queries return zero rows on
pass.**

Replace the placeholders once, at the top:

- `{{target}}` — the new, changed, or migrated table
- `{{source}}` — the source of truth. Mode A: the copy of the prior version.
  Mode B: the landed source of truth.
- `{{key}}` — the business or surrogate key that both sides share
- the **exclusion list** — metadata columns left out of levels 2–3 (load
  timestamps, batch IDs, CDC bookkeeping, ingestion hashes, audit columns).
  State it in the plan, so a reviewer can correct it.

---

## Level 1 — Shape (counts and key-set diffs)

```sql
-- 1a. Row count and distinct-key count, side by side
SELECT 'target' AS side, COUNT(*) AS row_count, COUNT(DISTINCT {{key}}) AS key_count
FROM {{target}}
UNION ALL
SELECT 'source', COUNT(*), COUNT(DISTINCT {{key}})
FROM {{source}};
-- row_count = key_count on each side → no duplicates; both sides equal → grain holds

-- 1b. Keys in SOURCE missing from TARGET (rows we dropped) — expect zero
SELECT s.{{key}}
FROM {{source}} s
LEFT JOIN {{target}} t ON t.{{key}} = s.{{key}}
WHERE t.{{key}} IS NULL;

-- 1c. Keys in TARGET not in SOURCE (rows we invented) — expect zero
SELECT t.{{key}}
FROM {{target}} t
LEFT JOIN {{source}} s ON s.{{key}} = t.{{key}}
WHERE s.{{key}} IS NULL;
```

---

## Level 2 — Checksums (per-column fingerprints)

One row per side; any column whose fingerprint differs is a suspect for
level 3. Fingerprint **business columns only**.

```sql
SELECT
    'target'                        AS side,
    COUNT(*)                        AS row_count,
    SUM(amount)                     AS sum_amount,
    COUNT(amount)                   AS nonnull_amount,
    {{hash_agg}}(status)            AS fp_status,
    {{hash_agg}}(effective_date)    AS fp_effective_date,
    COUNT(status)                   AS nonnull_status
FROM {{target}}
UNION ALL
SELECT
    'source',
    COUNT(*), SUM(amount), COUNT(amount),
    {{hash_agg}}(status), {{hash_agg}}(effective_date), COUNT(status)
FROM {{source}};
```

`{{hash_agg}}` is an **order-independent** fingerprint of a column. Use your
engine's hash aggregate where it has one (Snowflake `HASH_AGG`; BigQuery
`BIT_XOR(FARM_FINGERPRINT(CAST(col AS STRING)))`), or the sum of a per-row
hash converted to a number. Where there's nothing suitable, a weaker but
portable stand-in is `COUNT(DISTINCT col)` + `MIN(col)` + `MAX(col)` +
`SUM(LENGTH(CAST(col AS VARCHAR)))`.

For a tidy pass/fail instead of comparing two rows by eye:

```sql
WITH t AS (SELECT {{hash_agg}}(status) AS fp, SUM(amount) AS total FROM {{target}}),
     s AS (SELECT {{hash_agg}}(status) AS fp, SUM(amount) AS total FROM {{source}})
SELECT t.fp = s.fp       AS status_matches,
       t.total = s.total AS amount_matches
FROM t CROSS JOIN s;    -- expect TRUE, TRUE
```

---

## Level 3 — Cell-by-cell (suspect columns only)

```sql
-- Only rows where a value differs. IS DISTINCT FROM treats NULL vs NULL as a
-- match. Cap the output — you want the PATTERN of the break, not every row.
SELECT
    t.{{key}},
    t.amount         AS tgt_amount,  s.amount         AS src_amount,
    t.status         AS tgt_status,  s.status         AS src_status,
    t.effective_date AS tgt_eff,     s.effective_date AS src_eff
FROM {{target}} t
JOIN {{source}} s ON s.{{key}} = t.{{key}}
WHERE t.amount         IS DISTINCT FROM s.amount
   OR t.status         IS DISTINCT FROM s.status
   OR t.effective_date IS DISTINCT FROM s.effective_date
LIMIT 200;   -- or FETCH FIRST 200 ROWS ONLY / TOP 200, per dialect
-- Read the pattern: every amount off by ×100 → scaling bug; every date out by
-- the same hours → time zone; NULLs only in status → a bad COALESCE.
```

---

## Beyond parity — business-rule checks (SCD2 example)

```sql
-- Exactly one current row per key — counted over ALL rows, so a key with NO
-- current row is caught too — expect zero
SELECT {{key}}, SUM(CASE WHEN is_current THEN 1 ELSE 0 END) AS current_rows
FROM {{target}}
GROUP BY {{key}}
HAVING SUM(CASE WHEN is_current THEN 1 ELSE 0 END) <> 1;

-- No overlapping validity windows per key, including two versions that start
-- at the same instant — expect zero
SELECT {{key}}, valid_from
FROM (
  SELECT {{key}}, valid_from, valid_to,
         LEAD(valid_from) OVER (PARTITION BY {{key}} ORDER BY valid_from, valid_to) AS next_from
  FROM {{target}}
) w
WHERE next_from < valid_to;
```

With rows sorted by `valid_from`, an overlap anywhere in a key's history
shows up between two neighbours, so this check flags every key that has one.
To list every overlapping *pair* (for the report, not the gate), self-join on
the key and `a.valid_from < b.valid_to AND b.valid_from < a.valid_to`.

---

## Graduate the keepers → permanent tests

One-shot reconciliation stays as the SQL above. The checks that should guard
*every* future change become tests in the project's framework:

- **Structural keepers** — unique and not-null on the key, relationships to
  dimensions, accepted values on categoricals. In dbt these are schema tests
  in `schema.yml`; in SQLMesh, audits; with no framework, assertion queries
  that CI runs and fails on any returned row.
- **Logic keepers** — the business rules (the SCD2 checks above) as singular
  tests: the assertion query, saved as a test that passes when it returns
  zero rows.

Severity: **error** for keys, referential integrity, and load-bearing logic
(they corrupt downstream facts); **warn** for soft anomalies. See `test-data`
(if installed) for the severity model and the write-audit-publish gate.

---

## Per-model reconciliation plan (deliverable shape)

State the source of truth and the grain first, then the ordered checklist.

> **Source of truth:** `<table>` — <why it's the authority, and from when>
> **Target:** `<table>` · **Grain:** one row per <…>
> **Excluded (metadata) columns:** <list — assumed / confirmed by …>

| # | Level | Check                            | Proves                        | Pass |
|---|-------|----------------------------------|-------------------------------|------|
| 1 | 1     | row and distinct-key count       | grain, no duplicates or drops | ☐    |
| 2 | 1     | source-minus-target key diff     | no rows lost                  | ☐    |
| 3 | 1     | target-minus-source key diff     | no rows invented              | ☐    |
| 4 | 2     | per-column fingerprints          | which column (if any) broke   | ☐    |
| 5 | 3     | cell-by-cell on suspect columns  | the pattern of the break      | ☐    |
| 6 | rule  | one current row per key (SCD2)   | history logic correct         | ☐    |
| 7 | rule  | no overlapping validity windows  | history logic correct         | ☐    |

Stop escalating at the first ☐ that fails — fix, then re-run from #1. The
keepers (#1 uniqueness, relationships, #6, #7) graduate to permanent tests.
