---
name: tdd
description: Test-driven development for data transformations — for each behaviour a model must have, write small fixture input rows and the exact output rows the definition demands, watch the test fail for the right reason, write the least SQL that makes it pass, then add the edge cases (NULLs, duplicates, late rows, boundary timestamps, unmatched keys, re-runs) before refactoring. Use when building a new model or changing transformation logic test-first, fixing a data bug with a failing test first, writing unit tests for SQL or Python transforms (dbt or SQLMesh unit tests, pytest), or when the user mentions red-green-refactor. Validating real data on every load is test-data's job.
---

# TDD for Data Transformations

Red, green, refactor — applied to the logic that turns inputs into a table.
A model is a function from input rows to output rows; test it like one.

This is for **transformation logic**: joins, business rules, dedupe, SCD and
incremental logic. Checking real data on every load — uniqueness,
freshness, volume bands, the write-audit-publish gate — is `test-data`'s job
(if installed). The two meet in one rule: **fabricated rows belong in these
tests, and nowhere else**; business validation runs on real history.

Write tests in the framework named in `docs/agents/tooling.md` (if present).
[TEST-HARNESS.md](./TEST-HARNESS.md) has the shape for dbt and SQLMesh unit
tests, a plain-SQL harness, and pytest.

## The cycle

### 1. Name one behaviour, in business words

"A refund within 30 days nets against the original order's date." "A customer
who moves region gets a new version from the move date." One behaviour per
test, named so a failure says what broke.

### 2. Write the fixture and the expected rows — from the definition

* **Input:** the fewest rows, per upstream model, that exercise the behaviour.
  Name the fixture after the scenario (`refund_after_30_days`), not the data.
* **Expected output:** the exact rows the model must produce, at its grain —
  every column the behaviour touches.
* Work the expected rows out **from the definition** — `CONTEXT.md`, the spec,
  the source of truth — never by running the query you're testing and copying
  what it returns. A test copied from the output only proves the code does
  what the code does.

### 3. Watch it fail — for the right reason

Run it against the current model, or a stub that returns nothing. It must fail
on the assertion — the wrong rows — not on a syntax error or a missing table.
A test that passes before you've written the logic is testing nothing; fix the
test.

### 4. Make it pass with the least SQL

Write only what this behaviour needs. No speculative columns, no refactoring
yet. Green first.

### 5. Add the edges, one test at a time

For each, write it, watch it fail (or confirm on purpose that it already
passes), then make it pass:

* **NULLs** in every column the logic branches or joins on.
* **Duplicates** in an input — does the grain still hold?
* **A late or back-dated row** — does it land in the right period, or version?
* **Boundaries** — an event exactly at a `valid_to`, the first and last day of
  a period, midnight in another time zone.
* **An unmatched key** — does the fact reach the ghost row, or vanish?
* **An entity that disappears and comes back.**
* **Empty input** — the model runs and returns nothing, rather than failing.
* **A re-run** — for incremental logic, the existing target plus the same
  batch twice must equal the target plus the batch once.

### 6. Refactor with the tests green

Extract repeated logic into a macro or an intermediate model, rename to the
glossary's words, simplify — running the tests after each step. Then run the
model on real data and validate it there (`test-data`, if installed); the
unit tests prove the logic, not the data.

## Fixing a bug test-first

When a bug turns up (`diagnose`, if installed, finds the cause), turn its
reproduction into a fixture first: the smallest input that produces the wrong
output, and the right output as the expectation. Watch it fail, fix the
logic, watch it pass, and keep the test — it's the regression test.

## Deliver

For each behaviour: the test (fixture, expected rows, a name that says what
it protects), proof that it failed before the change and passes after, and
the edge cases covered — plus the model code that makes them pass.
