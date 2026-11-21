---
name: gather-requirements
description: Pin down what a data pipeline, model, or report must deliver, and why, before anyone designs or builds it — value and consumers, grain, sources and their owners, metric definitions, freshness/volume SLAs, history needs, and testable acceptance criteria — interviewing one question at a time, or synthesising when the conversation already holds the answers. Produces a one-page requirements spec, records terms in CONTEXT.md and hard-to-reverse decisions as ADRs, and can publish the spec to the issue tracker. Use when a new data ask arrives, scope is fuzzy, or people disagree on what a metric means. The how (patterns, stories, estimates) is solution-design's job.
disable-model-invocation: true
---

# Gather Requirements

"No-one knows exactly what they want." Your job is to make them precise about
**what** this must deliver and **why** — not how it will be built. Interview
the user **one question at a time**, waiting for each answer, and give your
recommended default with every question so they can react, not invent. If the
conversation already answers a question, don't ask it again: write the answer
down and confirm it. One question per message means one: don't tack an "also,
tell me…" onto it, however related — save it for the next turn.

Stop at the what and the why. Ingestion patterns, design rules, stories, and
estimates belong to `solution-design` (if installed), which starts from the
spec this skill produces.

## What you must leave the session knowing

### 1. Value and consumers

Use [VALUE-DISCOVERY.md](./VALUE-DISCOVERY.md) for the prompts.

* Who consumes it, in role terms, and the job it does for them. There may be
  more than one consumer — profile each, because their needs can conflict.
* How they'll read it — SQL, dashboard, extract, another system — the columns
  they'll filter on, and the query latency they can live with.
* The pain today and the gain they want — as a **measurable target**.
  Quantify the pain (hours a week of manual compilation, how long a wait
  before it hurts, what an error costs) and the gain (what improvement would
  make a real difference): "month-end close by day 3, not day 6", not
  "better data".
* The stakes, as a **criticality tier**, because each tier carries
  obligations the design must meet:
  * **Tier 1** — revenue reporting, regulatory returns, production ML.
  * **Tier 2** — executive dashboards, KPI packs.
  * **Tier 3** — ad-hoc analysis and exploration.
* Whether the data is **regulated**, and under which regime. Regulated data
  adds two requirements at any tier: auditability (who accessed what, when,
  and why; lineage from source to report) and deletion (honouring erasure
  requests within the mandated time).

### 2. Grain (the pivotal decision)

* What does one row represent? Declare it in one sentence. Everything else
  hangs off this; the most common modelling failure is a fuzzy grain.

### 3. Sources and owners

* Which systems, and which is the **agreed source of truth** when two
  disagree? Internal or vendor? (A vendor changes escalation paths, achievable
  SLAs, and how much you can trust schema-change notice.)
* A **named owner** per source — a person, not a team or channel — accountable
  for its quality, availability, and definitions, and how they announce
  changes.
* What the source can actually give: full history or current state only? Full
  snapshots or changes? Are deletes visible? Known issues — late-arriving rows,
  several updates a day, back-dated changes?

### 4. Definitions (ubiquitous language)

* Define every metric and entity precisely. "Active customer" how, exactly?
  "Revenue" — gross, net, returns within 30 days included? Capture these in
  `CONTEXT.md` so two people never compute the same metric two ways — write
  each term down as soon as it resolves, using
  [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md). Create the file lazily, only when
  there's a term to record.
* When a decision is hard to reverse, surprising without context, and the
  result of a real trade-off ("why event time, not load time"), record it as
  an ADR in `docs/adr/` using [ADR-FORMAT.md](./ADR-FORMAT.md).

### 5. SLAs (per pipeline, not repo-wide)

These are pipeline-level facts and can differ per source system — capture them
here, per pipeline, not in repo-wide config.

* Freshness: by when must it land? How fresh do consumers truly need it
  (real-time vs "today not yesterday" vs daily)? Push back on "real-time"
  that's really "faster batch."
* Volume: expected rows now, and daily/monthly growth.
* Reliability: what happens, and who's told, when it's late or wrong?

### 6. History

Ask three questions — they lead to different builds:

1. **Current state only?** → overwrite.
2. **The value as it was on a past date?** → point-in-time history (SCD2: a new
   row per change, a validity interval, a current flag — see `data-modelling`
   if installed). Needs full source history (question 3).
3. **What was known — or how a record was categorised — when it was
   processed, even after later corrections or rule changes?** → bi-temporal:
   keep both event time and processing time. Ask this one explicitly; it
   changes the build significantly.

If none applies, don't pay for history.

### 7. Acceptance criteria

* Explicit and testable: the grain holds (uniqueness tested), the freshness
  SLA is met, each metric matches its agreed definition, and the history
  question gets the answer it should for a known past date.
* How the value target will be measured after go-live, by whom, and when.

### 8. Priority — green, orange, red

Tag each requirement so effort goes where it pays:

* **Green** — low effort, high impact: data from known sources or an
  existing API, essential to the job. Build these first.
* **Orange** — medium effort, real but not critical impact: needs extra
  collection work (a new extract, a manual feed). Schedule them.
* **Red** — high effort, questionable impact: custom development or a costly
  integration for a nice-to-have. Challenge these; build them only when the
  value target says they're worth it.

## Deliver

A one-page **requirements spec**, in this order: value statement (the
sentence in VALUE-DISCOVERY.md) with its measurable target, criticality tier
(and regime, if regulated), consumers, **grain (bold)**, sources with owners
and caveats, metric definitions (linked to `CONTEXT.md`), SLAs, the history
decision, acceptance criteria, each requirement's priority, and open
questions.

Then offer to publish it. If `docs/agents/issue-tracker.md` exists, publish the
spec as one ticket following that file — titled "Requirements: <name>", with
the "needs evaluation" label from `docs/agents/triage-labels.md` — and give the
user the link or path. Without a tracker, deliver the spec inline; nothing
else in this skill depends on one.
