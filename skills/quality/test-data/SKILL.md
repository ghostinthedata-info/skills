---
name: test-data
description: Build a defensible data test plan — what to test (uniqueness, referential integrity, nulls, accepted values, freshness, volume/variance), severity (error vs warn), and where tests run (Write-Audit-Publish). Use when adding tests to a model/pipeline, designing data-quality gates, or deciding what "good data" means here.
---

# Test Data

Tests are the gatekeeper between bad data and your consumers. Decide what to
test, how loud each failure is, and where the gate sits.

Consult `docs/agents/platform.md` and `docs/agents/tooling.md` (if present)
for the SQL dialect and test framework to emit. SLA thresholds (freshness,
volume) are pipeline-level facts — read them from the pipeline's spec, not
from repo-wide config.

## What to test (the core battery)

* **Uniqueness** — every key (and composite) is unique. Non-negotiable.
* **Not-null** — keys and any column the business calls mandatory.
* **Referential integrity** — every fact FK resolves to a dimension row.
  Catches orphaned facts and bad joins.
* **Accepted values** — categorical columns contain only the agreed set
  (catch the fourteen spellings of "active" before they accumulate).
* **Freshness** — source/loaded-at timestamp is within the pipeline's SLA.
  Run freshness checks at least twice as often as the tightest SLA.
* **Volume & variance** — row count is within expected bounds and today's
  load isn't wildly off yesterday's (drift vs the saved profile baseline in
  `docs/profiles/`, if one exists).
* **Business rules** — singular tests for logic that needs
  joins/aggregations ("returns after 30 days are excluded from revenue").

## Severity — make failures mean something

* **error** (block the pipeline) — key uniqueness, not-null on keys,
  referential integrity, anything that corrupts downstream facts.
* **warn** (flag, don't block) — soft anomalies, a few unexpected
  categorical values, mild volume drift worth a human glance.

Tune thresholds as data grows — e.g. warn at >10 nulls, error at >100.
Severity inflation (everything is "error") destroys the signal, same as it
does for incidents.

## Where tests live — Write-Audit-Publish (Ghost in the Data)

Don't test in production after the fact. Use **WAP**:

1. **Write** — build the new data into a staging table/branch, production
   untouched.
2. **Audit** — run the full test battery against staging. Compare row counts
   to production; validate schema, types, business rules, and historical
   trend.
3. **Publish** — only if the audit passes, swap staging into production —
   **after backing up** the current production table. Alert on audit
   failure; never publish on red.

This is blue-green deployment for data: consumers never see unaudited data,
and you can roll back to the backup instantly. Make every load idempotent so
re-runs are safe (see `pipeline-design` if installed).

## Deliver

A test list per model, each with severity and (where useful) thresholds,
plus the WAP gate wired into the pipeline.
