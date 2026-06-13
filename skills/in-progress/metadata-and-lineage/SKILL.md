---
name: metadata-and-lineage
description: Capture business, technical, and operational metadata and end-to-end data lineage so data is discoverable, understood, and trustworthy. Covers the three metadata types, the metadata repository/catalog, lineage vs impact analysis, and stewardship. Use when standing up a catalog, documenting a pipeline's provenance, onboarding a dataset, or answering "what does this column mean / where did this number come from?".
---

# Metadata and Lineage

Metadata is the card catalog of a data environment: it tells people where data
is, where it came from, how it got there, what was done to it, how good it is,
and what it means (DMBOK, "Meta-data Management"). Without it, every dataset is
a black box and every analyst re-derives the same tribal knowledge. The job is
to capture it as a deliberate by-product of building, not a documentation
project bolted on later.

## The three kinds of metadata (capture all three)

* **Business metadata** — meaning for humans: the business definition of a
  table/column, the calculation rule behind a measure, valid value sets, the
  owner/steward, sensitivity classification, and SLAs. Answers *"what is this
  and can I trust it?"* This is the type most often missing — prioritise it.
* **Technical metadata** — structure for systems: physical schema, data types,
  keys and FK relationships, source-to-target mappings, transformation logic,
  and the models that bind them. Answers *"how is it stored and wired?"*
* **Operational metadata** — runtime facts: load timestamps, row counts,
  job durations, success/failure, refresh frequency, and data-quality scores
  per run. Answers *"is it fresh, complete, and did the last run work?"*
  (This is the same operational signal `pipeline-design` and `test-data`
  already emit — capture it as metadata, don't strand it in logs.)

## Lineage — provenance in both directions

**Lineage** is the documented path data travels from origin to consumption,
including every transformation. Capture it at column grain where it matters,
not just table-to-table. Two questions, two directions:

* **Backward (provenance):** "Where did this number come from?" — trace a
  report figure back through models to source columns and rules. This is what
  answers a *data content research request* when a consumer disputes a value.
* **Forward (impact analysis):** "If I change/break this, what downstream
  breaks?" — trace a source column forward to every model, dashboard, and
  extract that depends on it. Run this **before** any schema change.

Lineage that is hand-drawn rots immediately. Prefer lineage **derived from the
code** (parsed SQL/transform definitions) so it stays true as the pipeline
changes. Document the transformation rule on each hop, not just the arrow.

## The repository / catalog

A metadata repository (catalog) is the single integrated place the three types
live so users can search and trust data. Founded rules:

* **Integrated, not a silo per tool** — one searchable view across sources,
  models, and BI. Federate from authoritative sources rather than re-typing.
* **Metadata is itself data** — it has quality, owners, and a change process.
  Stale metadata is worse than none because it's trusted.
* **Capture at the source, automatically** — harvest schema, mappings, and
  operational stats from the systems that produce them; only the business
  layer needs human authoring.
* **Make it the path of least resistance** — if finding meaning in the catalog
  is easier than asking a person, it gets used and stays current.

## Stewardship

Every business-critical data element needs a **data steward** accountable for
its definition, sensitivity classification, and change process — metadata
without an owner decays. Use the agreed names from `CONTEXT.md` so a concept
has one definition across the repo. Where the same entity is defined by
conflicting sources, the golden-record rules live in `master-data-management`
(see it if installed); sensitivity classification and required controls live in
`data-security-classification` (see it if installed) and should be recorded as
business metadata on the column.

## Deliver

For a dataset: a catalog entry with business definition, owner/steward,
sensitivity, technical schema + source-to-target mapping, operational
freshness/volume stats, and a column-grain lineage trace back to source. Wire
impact analysis into the change-review step so no schema change ships blind.
