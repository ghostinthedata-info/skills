---
name: solution-design
description: Turn agreed requirements for a data pipeline, model, or report into a buildable design — how each source is ingested and what can go wrong with it, the pattern recipe (ingestion → transformation → delivery), the design rules every load follows (idempotent, rebuildable, raw stays raw, audited before publish), day-sized stories with handovers and seams, an estimate, a decisions register, and risks — written up as a solution-design doc with an SVG overview. Use once you know what to build and need to decide how and when. It starts from a requirements spec (gather-requirements, a ticket, or a brief) and asks only for what's missing.
---

# Solution Design

This skill decides **how** and **when**: the patterns, the rules every load
follows, the work packages, the seams between them, and the risks. It starts
from the **what** and **why** — a requirements spec from `gather-requirements`
(if installed), a ticket, or a brief — rather than re-running that interview.

Work through the steps in order; each feeds the next. Ask one question at a
time, each with a recommended default to react to. When you have enough to
act on, produce the design using `SOLUTION-DESIGN-TEMPLATE.md`. The reference
files carry the reusable knowledge so this file stays a process, not an
encyclopaedia:

* `PIPELINE-PATTERNS.md` — the patterns we assemble pipelines from
* `ENGINEERING-STEPS.md` — the DE tasks/steps per pipeline stage
* `COMMON-RISKS.md` — a risk library to reference, not reinvent

---

## Step 0 — Start from the spec

Read the spec if there is one. Check it gives you the five facts every design
hangs off, and ask only for the ones that are missing — if most are missing,
suggest running `gather-requirements` first:

1. **Value statement** — who it's for, the job, the pain, the gain (as a
   measurable target), and the criticality tier (with the regime, if the data
   is regulated) — the tier sets how much rigour the design earns.
2. **Grain** — one row represents what, in one sentence.
3. **Sources** — each with its named owner and the agreed source of truth.
4. **SLAs** — freshness, volume, reliability.
5. **History** — current state, point-in-time (SCD2), or bi-temporal.

If designing exposes a gap or a wrong answer in the spec, fix the spec and log
the change in the decisions register; don't quietly design around it.

## Step 1 — Source mechanics (per source)

Use `ENGINEERING-STEPS.md` (ingestion stage) for the full checklist. Leave
knowing, per source:

* **Delivery & delta mechanics** — full snapshot or delta/incremental? If
  delta: cadence (e.g. daily) and the watermark column driving it.
* **Deletes** — soft or hard? In a delta feed, do deletes appear at all, or do
  rows just silently stop arriving? (The classic delta trap.)
* **Real-time consistency** — if polled via API: latency between calls? Risk of
  a record changing *between* two calls — torn reads, missed mid-flight
  updates?
* **Gap & recovery** — if you miss a day, is it a permanent hole or does the
  next delta backfill it? Can you replay?
* **Initial load** — day-zero from current state only, or full history
  backfill? (Decides whether a rebuildable or SCD2 design is even possible.)

Then run the **pre-mortem** for each source: answer these ten questions
before a single row lands, and put the answers in the design doc's
pre-mortem table. An unanswered question is a risk, so log it as one.

1. **Schema change without warning** — how do we detect it (compare what
   landed with the agreed contract at staging) and respond (halt with a
   readable alert; quarantine new columns rather than load them)?
2. **Late-arriving data** — what's the tolerance window, and how are late rows
   reprocessed (a lookback window over event-time partitions)?
3. **Key reuse** — does the warehouse key stay independent of the source key,
   with a mapping that handles a recycled ID?
4. **NULLs where they shouldn't be** — what's the rule per column: accept,
   quarantine, or reject?
5. **Duplicates** — how is uniqueness defined and enforced at each layer, and
   do we track the duplicate rate?
6. **The job runs twice** — is every load idempotent?
7. **Time zones** — stored in UTC, with each source's time-zone semantics
   documented and converted on ingest?
8. **A bad day of garbage** — what circuit-breakers stop it (a two-sided volume
   band, a validation-failure threshold that quarantines the batch)?
9. **Who gets paged at 2am** — a named person on a rota, with a runbook, and
   an alert route that matches the tier?
10. **Who owns the data** — a named source owner accountable for content,
    delivery, and definition, with an agreed change-notice process?

## Step 2 — Choose the pattern recipe

Assemble the recipe from `PIPELINE-PATTERNS.md`: one ingestion pattern + the
transformation pattern + one or more delivery patterns. This becomes the SVG
overview in the design doc. Pick the thinnest recipe that meets the SLAs and
the history need.

Tag each part of the recipe with an effort signal: **known** (built before,
with actual timings), **known with caveats** (name the caveat — e.g. "the
source sends no delivery receipt"), or **novel**. From each pattern's entry,
note what it hands over and what it needs to start, and how it's validated —
those become the stories' handovers and done criteria.

**Build or buy the ingestion?** For a common SaaS or database source, compare
a managed connector with a custom build over the pipeline's life, not the
first build: schema changes, API versions, credential rotation, and rate
limits are where a custom connector eats engineer-days every month. Buy when
a managed connector covers the source and handles schema evolution; build
when the source is bespoke, the managed option isn't production-supported for
a critical pipeline, or its pricing at your volume is worse. Log the decision,
with the maintenance estimate, in the decisions register.

## Step 3 — Apply the design rules

Every pipeline gets these, whatever the recipe (details in the cross-cutting
section of `ENGINEERING-STEPS.md`):

* **Idempotent** — a load gives the same result whether it runs once or ten
  times; replace partitions or merge on the grain key, never blind-append.
* **Rebuildable** — any table rebuilds from raw in one command, and the
  incremental result is checked against a full rebuild.
* **Raw stays raw** — no typing, dedupe, or business logic on landing; types
  and the data contract apply in staging.
* **Audited before publish** — write-audit-publish for correctness-critical
  data; nothing unaudited reaches a consumer.
* **Data ships before code** — transformation starts once real batches land
  where production builds can see them, and business validation runs on real
  history.
* **Classified with the model** — classify columns and design access as you
  design the tables (`data-security-classification`, if installed), not after
  go-live.
* **Meets its tier's obligations** — the tier comes from the spec; the
  obligations are concrete:

  | Tier | Alerting | Tests and gates | Freshness SLA (example) |
  |---|---|---|---|
  | 1 | Pages the on-call person | Unique + not-null on every key, WAP, named owner | Under 4 hours, breaches alerted |
  | 2 | Team-channel alert | Core key tests, named owner | Under 12 hours |
  | 3 | Weekly digest | Best effort | Under 24 hours |

  Regulated data, at any tier, also needs an access audit trail, lineage from
  source to report, and a deletion path built with the same rigour as the
  ingestion (retention and erasure — see `data-security-classification`, if
  installed).

## Step 4 — Stories, seams, and the estimate

Break the recipe into themed stories of about one effort-day each, at most
five per slice, each with subtasks and an explicit handover (e.g. "Story 1 ·
Environment & Access Setup"). Draw tasks from `ENGINEERING-STEPS.md`.

* Size known parts from actual past timings; give each caveat an explicit
  buffer or an early spike; give a novel component one time-boxed discovery
  story with an exit question, and re-estimate after the proof of concept —
  don't break novel work into days.
* Walk the seams: what each stage hands the next, what the receiving side
  needs before it can start, and who is waiting on whom.
* The estimate is effort plus elapsed time at the seams, estimated
  separately — overruns happen at the seams.

## Step 5 — Produce the solution design

Fill `SOLUTION-DESIGN-TEMPLATE.md`:

1. **Summary** — the value statement and grain, carried from the spec.
2. **Overview (hand-authored inline SVG)** — source → ingestion → transform →
   delivery, focused on high-level tools/patterns, using the zone colours in
   the template. Model the phases on the pattern-bank flow.
3. **Tasks & steps** — the stories, the seams table, and the estimate from
   Step 4.
4. **Decisions register** — every material decision, why, alternatives, date,
   owner (official format in the template).
5. **Dependencies & risks** — reference `COMMON-RISKS.md`; list only the
   relevant ones plus any project-specific additions.
6. **Acceptance criteria** — the spec's criteria, plus the engineering checks:
   idempotent, rebuildable, validated on real history.

Deliver in thin vertical slices. Don't accept ad-hoc scope changes mid-slice —
route them through the decisions register instead.
