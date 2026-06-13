# Pipeline Design Checklist

A pre-build / review checklist for the non-negotiable defaults in the skill,
plus a tool-agnostic idempotent-merge skeleton and the Write-Audit-Publish
shape. Substitute your engine's syntax (consult `docs/agents/platform.md` if
present) and wire into your transform tool (`docs/agents/tooling.md`).

---

## Design / review checklist

### Idempotency
- [ ] Every write is **merge/upsert on a unique key**, never blind insert.
- [ ] Re-running the same task on the same input yields the same output (no dupes).
- [ ] Merge is **guarded** so newer data isn't clobbered by older on replay
      (`WHEN MATCHED AND source.updated_at > target.updated_at`).

### Reproducibility
- [ ] Output depends only on **input data + code**, not on run history
      (path-independent; the Healing Tables principle — see
      `slowly-changing-dimensions` if installed).
- [ ] You can **drop and rebuild** the layer from source.
- [ ] Time is pinned (no implicit `CURRENT_DATE` mid-logic), randomness seeded,
      transform logic versioned.

### Backfills
- [ ] Date/ID range is a **parameter**; one pass processes the whole range
      (don't loop the daily job N times — it compounds errors).
- [ ] Temporal integrity validated before publish.

### Defensive engineering
- [ ] Inputs validated at the boundary (schema, types, freshness); **fail fast**
      with a clear message.
- [ ] Late-arriving / out-of-order data handled explicitly.
- [ ] Soft vs hard deletes decided up front.
- [ ] Bad records **quarantined** (error mart), not silently dropped.

### Safe deployment
- [ ] **Write-Audit-Publish**: stage → audit → swap with backup; never publish
      on red (see `test-data` if installed).
- [ ] Core spine models kept lean so the DAG stays **wide and parallel**, not a
      serial chain.
- [ ] Every task emits metrics (duration, queue wait, row counts) for later
      tuning (see `performance-tuning` if installed).

### Visibility
- [ ] A thin visible slice ships early; progress is observable.
- [ ] Stakeholders get updates on a cadence ("Don't Go Dark").

---

## Idempotent guarded merge (skeleton)

```sql
MERGE INTO {{target}} AS t
USING {{staging}} AS s
  ON t.{{key}} = s.{{key}}
WHEN MATCHED AND s.{{updated_at}} > t.{{updated_at}} THEN
  UPDATE SET
    col_1 = s.col_1,
    col_2 = s.col_2,
    {{updated_at}} = s.{{updated_at}}
WHEN NOT MATCHED THEN
  INSERT ({{key}}, col_1, col_2, {{updated_at}})
  VALUES (s.{{key}}, s.col_1, s.col_2, s.{{updated_at}});
```

> The `AND s.updated_at > t.updated_at` guard is what makes a replay safe:
> re-running with older/equal data is a no-op instead of an overwrite.

## Boundary validation (fail fast)

```sql
-- run before the merge; abort the task if any return rows
-- schema/freshness gate
SELECT 'stale' AS reason
WHERE (SELECT MAX({{loaded_at}}) FROM {{staging}})
      < CURRENT_TIMESTAMP - INTERVAL '{{freshness_sla}}';

-- key sanity gate (a non-unique key fans out every join downstream)
SELECT {{key}}, COUNT(*) FROM {{staging}}
GROUP BY {{key}} HAVING COUNT(*) > 1;
```

## Quarantine instead of drop

```sql
-- route invalid rows to an error mart, keep the good rows flowing
INSERT INTO {{error_mart}}
SELECT *, 'negative_amount' AS reject_reason, CURRENT_TIMESTAMP AS rejected_at
FROM {{staging}}
WHERE amount < 0;

-- main load excludes them, but they're inspectable, not lost
-- ... build {{target}} from {{staging}} WHERE amount >= 0 ...
```

---

## Write-Audit-Publish shape

```
WRITE   → build into staging / a branch; production untouched
AUDIT   → run the full test battery on staging (see test-data)
PUBLISH → on green only: back up prod, then swap staging in
```

Make the swap atomic (table rename / partition swap / branch merge) so
consumers never see a half-written table and rollback is instant.
