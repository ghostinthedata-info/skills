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
* **Volume & variance** — the batch's row count sits inside a two-sided band
  for comparable periods — too few rows is as suspicious as too many (drift vs
  the saved profile baseline in `docs/profiles/`, if one exists).
* **Schema** — column names, types, and nullability match the contract or the
  baseline. A removed, renamed, retyped, or narrowed column is an error; an
  added column warns, with an owner.
* **Distribution** — key measures (sums, means, percentiles) and each
  category's share stay within an agreed band of history. Plausible-but-wrong
  values — an amount never converted to the reporting currency — pass every
  column test; only this catches them.
* **Business rules** — singular tests for logic that needs
  joins/aggregations ("returns after 30 days are excluded from revenue").

## Name what each test defends — the DQ dimensions

Frame the battery against the **DMBOK data-quality dimensions** so coverage is
explicit and gaps are visible. Every test should map to one:

* **Completeness** — not-null / mandatory-attribute checks (and "all expected
  rows present" — see volume below).
* **Uniqueness** — key and composite-key uniqueness; no entity appears twice.
* **Validity** — values conform to the domain: accepted-values, type/format,
  range/pattern. (Valid ≠ accurate — a well-formed value can still be wrong.)
* **Accuracy** — agreement with a reference source of truth; usually a
  business-rule test comparing to a system of record, not a column check.
* **Consistency** — values don't conflict across records, datasets, or over
  time (record-level, cross-record, temporal). Referential integrity lives
  here too: every FK resolves.
* **Timeliness / currency** — freshness within SLA.
* **Reasonableness** — volume/variance within expected operational bounds
  (e.g. fail a batch above 3× or below 0.1× the daily average — two-sided,
  because a drop is how data loss shows up).

If a critical column has no test in some dimension, that's a coverage gap to
raise. (Same vocabulary `profile-data` uses to assess a dataset, if installed.)

## Severity — make failures mean something

* **error** (block the pipeline) — key uniqueness, not-null on keys,
  referential integrity, anything that corrupts downstream facts.
* **warn** (flag, don't block) — soft anomalies, a few unexpected
  categorical values, mild volume drift worth a human glance.

A new check starts at **error**. Demote it to warn only once real runs show
it's a signal rather than a blocker, and write down why. Every warn carries an
owner and the threshold at which it becomes an error. Review warns on a
cadence: a check that has warned for more than two weeks with no
investigation is either a bug to fix or a threshold to change — "known issue"
is not a status. Change a threshold after an investigation, never just
because the data grew. Severity inflation (everything "error", forever)
destroys the signal too, same as it does for incidents.

## Where tests live — Write-Audit-Publish (Ghost in the Data)

Don't test in production after the fact. Use **WAP**:

1. **Write** — build the new data into a staging table/branch, production
   untouched.
2. **Audit** — run the full test battery against staging. Check the new batch
   against history (the two-sided volume band, distribution), check that
   staging minus production is the expected change, and validate schema,
   types, and business rules. The audit is read-only and safe to re-run.
3. **Publish** — only if the audit passes, swap staging into production
   **atomically** (a swap, rename, or pointer switch — never drop-and-recreate,
   which leaves consumers a window of partial data), keeping the previous
   version recoverable. When the audit fails, pick one per table and record
   the choice:
   * **Reject** — drop staging; production stays on the last good version;
     alert.
   * **Quarantine** — move the failing rows to an append-only quarantine store
     (what failed, which check caught it, when it arrived), re-audit the rest,
     publish the clean rows if that passes, and send the counts to the
     source's owner.

This is blue-green deployment for data: consumers never see unaudited data,
and you can roll back quickly. Make every load idempotent so re-runs are safe
(see `solution-design` if installed).

## Test the checks themselves

The battery above is **validation** — it runs on every load. **Testing** runs
in development and CI and proves the pipeline and its checks behave:

* For each business rule, state the invariant and run the check against small
  fixed inputs: it must fire on every violating case (adjacent, overlapping,
  identical, contained, touching at the boundary) and stay quiet on valid
  ones. A validation query can be wrong too.
* When a bug reaches production, write the failing test first, watch it fail,
  fix the bug, watch it pass — and keep the test.
* Fabricated rows belong in these tests only; business validation runs on real
  history.

## Deliver

A test list per model, each with severity and (where useful) thresholds,
plus the WAP gate wired into the pipeline.

## Template

For copy-paste scaffolds of the full battery (declarative dbt-style YAML
and assertion SQL), the per-model test-plan shape, and the WAP gate, see
[TEST-TEMPLATE.md](./TEST-TEMPLATE.md). Keep them tool-agnostic — match the flavour to your stack (consult
`docs/agents/tooling.md` and `docs/agents/platform.md` if present).
