# Healing Table Template

Mock-up SQL scaffolds for the six-step, path-independent SCD2 build described
in the skill. 

These are **pseudo-SQL skeletons**, not runnable models. Keep them
tool-agnostic: swap the windowing/hashing functions for your engine's
equivalents (consult `docs/agents/platform.md` if present), and wire them into
your transform tool (dbt model, SQLMesh model, plain SQL script).

Replace every `{{ ... }}` placeholder:

- `{{source}}` — the source table or staging view
- `{{durable_key}}` — the business/durable key that identifies one entity over time
- `{{change_ts}}` — the timestamp that orders changes (e.g. `updated_at`, `effective_date`)
- `{{tracked_cols}}` — the descriptive columns whose change you want to capture
- `{{high_date}}` — your "open interval" sentinel, e.g. `DATE '9999-12-31'`

---

## Step 1 — Effectivity table (extract real change points)

Keep only the rows where a tracked attribute actually changed. Use a
**null-safe** comparison so a value going to/from NULL counts as a change.

```sql
-- effectivity: one row per real change point per durable key
WITH ordered AS (
  SELECT
    {{durable_key}},
    {{change_ts}}                                  AS effective_from,
    {{tracked_cols}},
    LAG({{tracked_cols_concat_or_hash}}) OVER (
      PARTITION BY {{durable_key}}
      ORDER BY {{change_ts}}
    )                                              AS prev_state
  FROM {{source}}
)
SELECT *
FROM ordered
WHERE prev_state IS NULL                            -- first appearance
   OR {{tracked_cols_concat_or_hash}} IS DISTINCT FROM prev_state
```

> `IS DISTINCT FROM` is the null-safe comparison; substitute your dialect's
> equivalent if it lacks it (e.g. `NOT (a <=> b)` in MySQL, or wrap both sides
> in `COALESCE(..., <sentinel>)`).

---

## Step 2 — Time slices (derive validity intervals)

Use `LEAD()` over the effectivity rows to close each interval at the start of
the next one. Left-closed / right-open: `valid_from <= t < valid_to`.

```sql
SELECT
  {{durable_key}},
  {{tracked_cols}},
  effective_from                                    AS valid_from,
  COALESCE(
    LEAD(effective_from) OVER (
      PARTITION BY {{durable_key}}
      ORDER BY effective_from
    ),
    {{high_date}}
  )                                                 AS valid_to,
  LEAD(effective_from) OVER (
    PARTITION BY {{durable_key}}
    ORDER BY effective_from
  ) IS NULL                                         AS is_current
FROM effectivity
```

---

## Step 3 — Join sources (build the unified timeline)

When attributes come from several sources, as-of join each onto the spine of
change points. Document **attribute ownership** — which source wins per column
— right here in the model so it is not lost.

```sql
-- as-of join: pick the source row in effect at each slice's valid_from
SELECT
  s.{{durable_key}},
  s.valid_from,
  s.valid_to,
  a.attr_owned_by_source_a,                         -- source A owns these
  b.attr_owned_by_source_b                          -- source B owns these
FROM time_slices s
LEFT JOIN source_a a
  ON a.{{durable_key}} = s.{{durable_key}}
 AND a.{{change_ts}} <= s.valid_from
 AND s.valid_from < COALESCE(a.next_change_ts, {{high_date}})
LEFT JOIN source_b b
  ON b.{{durable_key}} = s.{{durable_key}}
 AND b.{{change_ts}} <= s.valid_from
 AND s.valid_from < COALESCE(b.next_change_ts, {{high_date}})
```

---

## Step 4 — Hash (identity + change detection)

A **key hash** for identity and a **row hash** over the tracked columns for
change detection. COALESCE NULLs to a sentinel so `NULL` and `''` don't
collide.

```sql
SELECT
  *,
  {{hash_fn}}(CAST({{durable_key}} AS STRING))      AS dim_key_hash,
  {{hash_fn}}(
    CONCAT_WS('||',
      COALESCE(CAST(col_1 AS STRING), '^^'),
      COALESCE(CAST(col_2 AS STRING), '^^'),
      COALESCE(CAST(col_3 AS STRING), '^^')
    )
  )                                                 AS row_hash
FROM joined_timeline
```

> `{{hash_fn}}` = `MD5` / `SHA2` / `FARM_FINGERPRINT` etc. — pick what your
> engine offers. `'^^'` is the null sentinel; any value no real column can take.

---

## Step 5 — Compress (collapse consecutive identical states)

Islands-and-gaps: merge adjacent slices only when they are **both** temporally
contiguous **and** row-hash-equal. This is what makes the result independent of
how the source was loaded.

```sql
WITH flagged AS (
  SELECT
    *,
    CASE
      WHEN row_hash = LAG(row_hash) OVER (
             PARTITION BY dim_key_hash ORDER BY valid_from)
       AND valid_from = LAG(valid_to) OVER (
             PARTITION BY dim_key_hash ORDER BY valid_from)
      THEN 0 ELSE 1
    END AS is_new_island
  FROM hashed_timeline
),
islands AS (
  SELECT *,
    SUM(is_new_island) OVER (
      PARTITION BY dim_key_hash ORDER BY valid_from
    ) AS island_id
  FROM flagged
)
SELECT
  dim_key_hash,
  {{durable_key}},
  {{tracked_cols}},
  row_hash,
  MIN(valid_from)                                   AS valid_from,
  MAX(valid_to)                                     AS valid_to,
  BOOL_OR(is_current)                               AS is_current
FROM islands
GROUP BY dim_key_hash, {{durable_key}}, {{tracked_cols}}, row_hash, island_id
```

---

## Step 6 — Validate (block publish on failure)

Run these before swapping into production (Write-Audit-Publish; see
`test-data` if installed). Each should return **zero rows**.

```sql
-- a) exactly one current row per durable key
SELECT {{durable_key}}, COUNT(*) AS current_rows
FROM healed_dim
WHERE is_current
GROUP BY {{durable_key}}
HAVING COUNT(*) <> 1;

-- b) no overlapping intervals
SELECT a.{{durable_key}}
FROM healed_dim a
JOIN healed_dim b
  ON a.{{durable_key}} = b.{{durable_key}}
 AND a.valid_from < b.valid_to
 AND b.valid_from < a.valid_to
 AND a.valid_from <> b.valid_from;

-- c) no inverted intervals
SELECT * FROM healed_dim WHERE valid_from >= valid_to;

-- d) no gaps (only if continuity is required)
SELECT a.{{durable_key}}, a.valid_to AS gap_starts
FROM healed_dim a
LEFT JOIN healed_dim b
  ON a.{{durable_key}} = b.{{durable_key}}
 AND a.valid_to = b.valid_from
WHERE NOT a.is_current
  AND b.{{durable_key}} IS NULL;

-- e) no consecutive duplicate versions (compression worked)
SELECT {{durable_key}}, valid_from
FROM (
  SELECT {{durable_key}}, valid_from, row_hash,
         LAG(row_hash) OVER (PARTITION BY {{durable_key}} ORDER BY valid_from) AS prev_hash,
         LAG(valid_to)  OVER (PARTITION BY {{durable_key}} ORDER BY valid_from) AS prev_to
  FROM healed_dim
) t
WHERE row_hash = prev_hash AND valid_from = prev_to;
```

---

## The payoff

Fix the logic, reprocess the whole range, and you get exactly what a full
rebuild would — the dimension **heals** accumulated drift because the output
depends only on the source data and the code, never on load history. Use it
when you have full source history and rebuild time is acceptable; keep plain
incremental SCD2 for very high volume or real-time.
