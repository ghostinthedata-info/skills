---
name: gather-requirements
description: Elicit and pin down requirements for a data pipeline or model before any code. Nails grain, sources, consumers, definitions, freshness/volume SLAs, historization, access patterns, and acceptance criteria. Use when the user starts a new pipeline/model/report, or when scope is fuzzy and you need to prevent rework and scope creep.
disable-model-invocation: true
---

# Gather Requirements

"No-one knows exactly what they want." Your job is to make them precise.
Interview the user **one question at a time**, waiting for each answer. For
every question, give your recommended default so they can react, not invent.

## What you must leave the session knowing

**Purpose & consumers**
* What decision does this data enable? What's broken about how it's done now?
* Who consumes it, and how — SQL, dashboard, API, reverse-ETL? What are the
  common filter columns and the acceptable query latency?

**Grain** (the pivotal decision)
* What does one row represent? Declare it in one sentence. Everything else
  hangs off this; the most common modeling failure is a fuzzy grain.

**Sources**
* Which systems? Known issues — late-arriving rows, soft vs hard deletes,
  multiple updates per day, backdated changes, schema-change process?
* Is full source history available (needed for any rebuildable design)?

**Definitions / ubiquitous language**
* Define every metric and entity precisely. "Active customer" how, exactly?
  "Revenue" — gross, net, returns within 30 days included? Capture these in
  `CONTEXT.md` so two people never compute the same metric two ways.

**SLAs** (these are pipeline-level facts and can differ per source system —
capture them here, per pipeline, not in repo-wide config)
* Freshness: by when must it land? How fresh do consumers truly need
  (real-time vs "today not yesterday" vs daily)? Push back on "real-time"
  that's really "faster batch."
* Volume: expected rows now, and daily/monthly growth.
* Reliability: what happens, and who's told, when it's late or wrong?

**Historization**
* Do consumers need point-in-time / "as it was when…" answers? If yes, you'll
  need SCD2 (see `slowly-changing-dimensions` if installed; the core rule:
  new row per change, validity interval, current flag). If not, don't pay
  for it.

## Deliver
A one-page spec: purpose, consumers, **grain (bold)**, sources + caveats,
metric definitions, freshness & volume SLAs, historization decision, and
explicit acceptance criteria. Deliver in thin vertical slices — don't accept
ad-hoc scope changes mid-slice.
