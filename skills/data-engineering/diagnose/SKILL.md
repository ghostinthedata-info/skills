---
name: diagnose
description: Find out why a number is wrong — a disciplined loop for data defects (totals too high or too low, duplicates, missing rows, stale or shifted values) that pins the symptom, reproduces it with a query, bisects the lineage hop by hop to the transformation that breaks it, tests one hypothesis at a time, fixes the cause rather than the output, and locks the fix in with a regression test. Use when the user says a number, report, or table is wrong, doesn't match another system, changed unexpectedly, or has duplicates or gaps, or asks to diagnose, debug, or root-cause a data problem. For slow pipelines use performance-tuning; for stakeholder comms during an incident use data-incident-management.
---

# Diagnose

Don't guess and don't patch the output. Prove where the number goes wrong,
fix the step that breaks it, and leave a test behind.

Write queries for the engine in `docs/agents/platform.md` (if present), and use
the glossary in `CONTEXT.md` for what each metric is supposed to mean.

## 1. Pin the symptom

Write down, before touching anything:

* **Which number** — the report or table, the column, the measure.
* **Which slice** — period, filters, grain.
* **Expected vs actual** — both numbers, and how "expected" is known: another
  system, last month's value, a definition, a hand count.
* **Since when** — always wrong, or wrong since a date? A start date points at
  a change (a deploy, a schema change, a backfill, a new source value).

Read the metric's definition in `CONTEXT.md` first. A "wrong" number is often
the right number for a different definition — and then the fix is the
definition or the report, not the pipeline.

## 2. Reproduce it with a query

Write the query that returns the wrong number from the published table, and
save it: it's the reproduction and, later, the basis of the regression test.
If you can't reproduce the reporter's number, check their side before the
pipeline's — report filters, a cached or exported copy, the time zone they
view in.

## 3. Bisect the lineage

Walk upstream one hop at a time — report → mart → intermediate → staging →
raw → source — and compute the **same measure for the same slice** at each
hop: the row count, the distinct keys, the total.

```sql
-- the same slice, at every hop: does the number still hold here?
SELECT '<hop>' AS hop,
       COUNT(*)                  AS row_count,
       COUNT(DISTINCT <key>)     AS key_count,
       SUM(<measure>)            AS total
FROM <hop_table>
WHERE <the reporter's slice, translated to this hop's columns>;
```

The bug lives in the transformation between the **last hop that's right** and
the **first hop that's wrong**. If the source itself is wrong, it's a source
problem: take the evidence to the source's owner. To compare two tables
precisely, the battery in `reconcile-data` (if installed) works at any hop.

## 4. Test one hypothesis at a time

Name a cause, predict what a query will show if it's true, run it, and keep
or drop the hypothesis. Never change two things at once. The usual suspects,
by symptom:

| Symptom | Usual causes |
|---|---|
| Too high | A join on a key that isn't unique (fan-out); duplicates from a re-run that wasn't idempotent; a semi-additive measure (a balance) summed over time; two current rows in an SCD2 dimension |
| Too low | An inner join dropping rows with no dimension match (no ghost row); a filter on a nullable column; late rows outside the load window; a time-zone cut-off; deletes not captured |
| Wrong in some segments only | A new source value that isn't mapped; a `CASE` branch that misses it; a lookup missing rows for one region or product |
| Changed since a date | An upstream schema or type change; a definition change; a backfill; a fact joined to the *current* dimension row instead of the version in effect at the event |
| Duplicates | A non-unique grain key; the batch loaded twice; a merge keyed on the wrong column |

## 5. Fix the cause, not the number

* Fix the transformation. Never correct the output by hand — a manual update
  is overwritten by the next run and leaves no record.
* Decide how far back the damage reaches. If history is wrong too, rebuild it
  deterministically (`data-modelling`'s BACKFILLING reference, if installed) —
  and confirm with the user before reprocessing published history; it's hard
  to undo.
* If people have already used the wrong figures, it's an incident: they need a
  correction notice (`data-incident-management`, if installed).
* If the cause is a pattern — the same non-unique join in five models — fix
  the pattern, not just this instance.

## 6. Lock it in

* **A regression test** built from the reproduction: it fails on the broken
  logic and passes on the fix. Write it before the fix if you can (`tdd`, if
  installed).
* **A monitor** if the cause can come back — a uniqueness test on the grain, a
  two-sided volume band, an accepted-values check (`test-data`, if installed).
* **A note on the ticket**, if there is one: the cause, the hop where it
  broke, the fix, how far back it reached, and the test that now guards it.

## Deliver

The cause in one sentence, the evidence (the reproduction query and the hop
where the numbers diverge), the fix, how far back it reaches and what was
done about it, and the regression test.
