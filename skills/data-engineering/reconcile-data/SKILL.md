---
name: reconcile-data
description: Prove a changed model or a migrated table is correct before it ships — a reconciliation plan and checklist, runnable SQL that compares the target with a source of truth (escalating from counts and key-set diffs, to per-column checksums, to a cell-by-cell diff), and permanent tests for the checks worth keeping. Use whenever you've built or changed a model and need to show it reconciles, when migrating a table between platforms and need to prove parity, when a backfill needs sign-off, or when standing up a reconciliation check. Triggers on "does this reconcile", "validate this model", "prove the migration matches", "check the numbers tie out", "reconcile against source", or finishing a model or backfill that needs sign-off.
---

# Reconcile Data

A model that *runs* is not a model that's *right*. This skill produces a
reconciliation **plan and checklist** and the **runnable SQL** to work
through it, escalating from cheap shape checks to expensive cell-level diffs
— and stopping the moment you've localised the break. The checks worth
keeping graduate into **permanent tests**, so they survive the next change.

Write SQL for the engine in `docs/agents/platform.md`, and tests in the
framework in `docs/agents/tooling.md`, if those files exist.
[RECONCILE-TEMPLATE.md](./RECONCILE-TEMPLATE.md) has the queries.

## Pick the mode

The battery is the same; what changes is *what you trust as truth*.

* **Mode A — Validate a change.** You changed a model (a refactor, a new
  column, a logic fix, a backfill). Truth is the **prior version** of the same
  table, captured before the change — a clone or snapshot, time travel if your
  engine has it, or a plain copy. You're proving the diff is *exactly* what
  you intended and nothing else moved.
* **Mode B — Reconcile a migration or a load.** The target must match a
  source of truth held elsewhere. Name the authority explicitly — and if it
  changes on a date (a migration cutover, say), state which one applies to
  this run, so the plan doesn't quietly go stale.

If the user hasn't said which, ask. The first question is always *"what's the
source of truth, and where can we query it next to the target?"* Both sides
have to be queryable together. If the legacy system can only be reached
through a landed copy, reconcile against that copy and say so in the plan.

## The escalating battery (cheap → expensive)

Run in order. **Stop escalating the moment a level fails** — a count mismatch
makes a cell-by-cell diff premature. Fix, then re-run from the top.

### 1. Shape — counts and key-set diffs (always)

Cheapest, and catches the most. Confirms the grain and that the *right rows*
are present before you trust any value.

* **Row count** target vs source (and per partition or load date if
  relevant).
* **Distinct key count** — catches fan-out and duplicates a raw count hides.
* **Key-set diff** — keys in the source missing from the target, and keys in
  the target not in the source. *These two anti-joins are the heart of
  reconciliation.*
* **Declared totals** — if the producer declares what it sent (a manifest's
  row count or checksum, a control record's sums), the landed data must match
  exactly. No tolerance band: a declared total is a fact, not an estimate.

If counts and key sets tie out, the grain is right, and the next levels are
about *values*, not *rows*.

### Exclude metadata columns (avoid false positives)

Some columns *should* differ between source and target and must be left out
of levels 2–3, or they'll fail a fingerprint for no reason: load timestamps,
batch or run IDs, CDC bookkeeping, ingestion hashes, audit columns. Reconcile
*business* columns; ignore *plumbing*.

Keep an explicit exclusion list. If the project hasn't supplied one, derive it
from the load pattern and **state your assumptions in the plan** so a reviewer
can correct them. Apply it the same way everywhere: the checksums fingerprint
only non-excluded columns, and the cell-by-cell diff compares only
non-excluded columns. Level 1 is unaffected — metadata doesn't change row
identity.

### 2. Checksums — per-column fingerprints

Localises *which column* broke for a fraction of the cost of a cell-by-cell
diff. One pass yields a fingerprint per column; mismatched fingerprints point
straight at the offender.

* **Numerics:** `SUM`, `MIN`, `MAX`, `COUNT` (and the `SUM` of a rounded value
  if float noise is expected).
* **Strings, dates, everything else:** an order-independent hash aggregate,
  so the two sides agree regardless of row order (the template lists options).
* **Null count per column** — a column that's right on non-nulls but wrong on
  null handling shows up here, not in a `SUM`.

Only the columns whose fingerprints disagree go to level 3. A full-row
`EXCEPT` / `MINUS` across every column is a level-3 check in disguise — it
compares every cell — so it comes after the fingerprints, not before them.

### 3. Cell-by-cell — the value anti-join

Most expensive; kept for the columns level 2 fingered. Join on the key and
return only the rows where a value differs, both sides side by side, so the
*pattern* of the break is visible: off by a factor, a time-zone shift,
trailing whitespace, rounding, a bad `CASE` branch.

Cap the output — you want the *shape* of the discrepancy, not all four million
rows. Use `IS DISTINCT FROM` (or your dialect's null-safe equivalent) so NULLs
compare correctly.

### Beyond parity

Reconciliation proves the target equals the source. It does **not** prove the
source was sane, or that the business logic is right. Where relevant, add:

* **Business-rule checks** — what the model is *supposed* to do (for SCD2:
  exactly one current row per key, no overlapping validity windows,
  contiguous dates).
* **Profile drift** — compare with the saved baseline in `docs/profiles/`
  (see `profile-data` if installed) to catch "matches source, but the source
  changed shape this load".

## Output — the deliverable

Produce all three:

1. **A reconciliation plan and checklist** — a short ordered list to work top
   to bottom, each item with its level, what it proves, and a pass/fail box.
   Lead with the source-of-truth declaration and the grain.
2. **Runnable SQL** — one copy-paste block per check, in battery order,
   parameterised at the top (table names, key, exclusion list), so it runs
   ad hoc straight away.
3. **Permanent tests for the keepers** — the checks that should guard *every*
   future change (key uniqueness, not-null, relationships, the load-bearing
   business rules), written in the project's test framework. One-shot
   reconciliation stays as SQL; recurring guards become tests.

## Where this sits

`test-data` (if installed) owns the overall test strategy — severities,
DQ-dimension coverage, and the write-audit-publish gate. **This skill is the
reconciliation deep-dive** for when the job is specifically "prove the target
equals the source". Reconciliation proves *this* change is correct;
`test-data` defends every future one. When reconciliation passes, graduate the
keepers into the `test-data` gate so they run permanently.

Other skills this one leans on, if installed:

* **`profile-data`** — the baseline the drift check compares against.
* **`data-modelling`** — if reconciliation surfaces a grain or SCD problem
  rather than a data problem, the fix is a modelling decision, not another
  query.
* **`review-data-change`** — asks for this evidence on every logic change
  before it merges.

## Deliver

The plan and checklist, the parameterised SQL in battery order, and the
permanent tests for the keepers — with the source of truth and the grain
stated up front, so anyone reading the sign-off knows what "reconciles" meant
here.
