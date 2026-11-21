---
name: review-data-change
description: Decide whether a change to a data pipeline, model, or table is ready to merge, and how much human ownership it needs — set the review level by the kind of work, require reconciliation evidence (a data diff against production; counts, keys and totals that tie out), run the data reviewer's checks (grain, fan-out, re-runs, tests at the grain, breaking changes, docs and classification), refuse to accept tests written by the change's own author — human or agent — as the only proof, make sure the reviewer can explain the change without the author, and fix the pattern behind any defect, not just this instance. Use when reviewing a pull or merge request that touches SQL, models, pipelines, or schemas; when asked "is this ready to merge", "review this change", or "sign off this model"; or when an agent wrote the change.
---

# Review a Data Change

A data change can build, pass its tests, and still be wrong — data doesn't
crash. A subtly wrong join builds fine, the tests written alongside it pass,
the row count looks plausible, and the first sign of trouble is an analyst
asking three weeks later why a metric doubled. This skill answers one
question: **is this change ready to merge, and how much human ownership does
it need?**

## 1. Set the review level by the kind of work

Decide before reading the diff. Write the mapping down once for the team, and
follow it:

| Kind of work | Level | What it means |
|---|---|---|
| Exploration, scratch analysis, boilerplate ingestion from a known pattern | **Light** | The author or an agent runs it; the reviewer checks the output and the evidence |
| A new model, or a change to transformation logic | **Standard** | Every check below, plus reconciliation evidence |
| SCD or dimension logic; anything touching money, compliance, or personal data; migrations; backfills over published history; breaking changes | **Owned** | An agent may draft; a person owns every line, and the reviewer reads all of it |

When a change mixes kinds, the highest level wins.

## 2. Ask for the evidence before reading the code

Reading SQL is a poor way to find a wrong number. Ask what the change does to
the data:

* **A data diff against production** — the changed model against the current
  one: rows added, removed, and changed, and which columns moved
  (`reconcile-data`'s validate-a-change mode, if installed). A refactor should
  show an empty diff; any other difference needs a reason.
* **Shape that ties out** — row counts, distinct keys, and key totals,
  compared with the source or the previous version.
* **The tests, run** — the results, not just the test files.
* **For a new source or model** — the profile and the one-sentence grain
  (`profile-data`, if installed).

No evidence, no merge — however clean the code reads. A short reconciliation
beats a long explanation. The author, or the agent, can write the
reconciliation; a person reads its result.

## 3. Don't accept the author's tests as the only proof

Tests written by the change's own author — a person or an agent — share the
author's understanding, and so its blind spots: the model builds, the tests
pass, and the number is still wrong. At least one piece of evidence has to
come from outside that understanding: the data diff, a reconciliation against
an independent source of truth, expected rows worked out from the definition
rather than from the query's output (`tdd`, if installed), or a test the
reviewer writes.

## 4. Run the data reviewer's checks

* **Grain and logic** — the stated grain is the actual grain (`COUNT(*)`
  equals the distinct count of the grain key); no silent fan-out (every join
  on a key that's tested unique); row counts make sense against production.
* **Re-runs** — a second run gives identical results: no `CURRENT_TIMESTAMP`
  in business logic, no blind appends, deterministic dedupe; an incremental
  model has a unique key and a lookback that covers late data.
* **Tests** — unique and not-null at the grain; data tests for any
  grain-changing transform; business rules as tests, not only comments; a
  regression test if the change fixes a bug.
* **Schema and breaking changes** — contracts on public models; a rename,
  removal, or type change shipped as a new version with a deprecation window;
  downstream consumers found through lineage and told.
* **Docs and classification** — model and column descriptions; new columns
  classified (`data-security-classification`, if installed); a comment
  carrying the *why* for any rule that isn't obvious.
* **Cost** (Standard and Owned) — partitioning and clustering considered for
  the heavy steps, and a rough cost where it matters.

`sql-antipatterns`' pipeline checklist covers the same ground as a tick-list,
if your repo has it.

## 5. Can the reviewer explain it without the author?

The reviewer — not the author, not the agent — must be able to say what the
change does, what it assumes, and what would break it. If they can't, it isn't
ready, whatever the tests say. A quick way to find the gap: draw the change
step by step, one box per step, with what each step does to the rows.

## 6. Fix the pattern, not just the output

When review finds a defect, get it fixed — then ask what produced it. A rule
missing from the team's skills or templates? A gap in the source pre-mortem?
A prompt that didn't give the agent the grain or the keys? Feed the correction
back there, so the next change doesn't repeat it. Fixing only the output keeps
you on a treadmill.

## Verdict

End with one of:

* **Ready to merge** — the level, the evidence that settled it, and anything
  to watch after release.
* **Ready after changes** — each change needed, tied to the check it fails.
* **Not ready** — the missing evidence or the defect, and who has to own it.

Add any pattern fix to feed back, naming the skill, template, or checklist it
belongs in.
