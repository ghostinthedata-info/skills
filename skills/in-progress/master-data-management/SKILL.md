---
name: master-data-management
description: Build one authoritative version of essential business entities (customer, product, account) from conflicting sources using match and survivorship rules, and control shared reference data (code/domain value lists). Covers master vs reference vs transaction data, golden records, identity resolution, hub architecture styles, and stewardship. Use when the same entity exists in multiple systems and you need one trustworthy version, or when code lists drift apart across systems.
---

# Master Data Management

When "customer" lives in five systems with five spellings and three IDs, no
report agrees with another. Master Data Management (MDM) is the ongoing
reconciliation of the **most accurate, timely, and relevant version of truth**
about essential business entities so they can be shared consistently across
systems (DMBOK, "Reference and Master Data Management"). It is a continuous
data-quality program, not a one-off project.

## Classify the data first

* **Master data** — the core business entities transactions act upon:
  customer, product, employee, account, location, supplier. Few rows relative
  to transactions, but referenced everywhere; errors propagate widely.
* **Reference data** — defined domain value sets (vocabularies): country codes,
  status codes, currency codes, category lists. Slowly changing, shared,
  standardised. Manage these too — divergent code lists break joins and
  conformance just like divergent entities do.
* **Transaction data** — the events/activities (orders, payments, clicks).
  High volume; *not* mastered, but it references master and reference data.

Get the classification right before designing: master data needs matching and
survivorship; reference data needs a controlled distribution/approval process.

## The golden record

A **golden record** is the organisation's best current effort at the single
authoritative value for an entity, assembled from the contributing sources for
shared, contextual use. Founded rules:

* **Replicate master data only from the database of record.** Pick the
  authoritative source per attribute; don't let every system write back.
* **Golden values are a best effort, not gospel.** New data can prove earlier
  assumptions wrong — so **apply matching rules with caution and make every
  merge reversible.** Never hard-delete the contributing records.
* **Shared master/reference data belongs to the organisation**, not to one
  application or department.

## Identity resolution (matching)

Deciding whether two records are the same entity:

* **Deterministic matching** — exact/normalised key match (same tax ID,
  normalised email). Fast and safe; use it first where a reliable identifier
  exists.
* **Probabilistic matching** — weighted similarity across attributes (name,
  address, DOB) with a score threshold. Use when no clean key exists. Tune for
  the cost of error: a **false merge** (two real customers collapsed) is
  usually worse and harder to undo than a **false split** — so set thresholds
  conservatively and route the uncertain band to a steward for review.
* Profile and standardise inputs before matching (see `profile-data` if
  installed) — most "bad matching" is unnormalised input.

## Survivorship (merge rules)

When matched records disagree, survivorship rules pick the surviving value
**per attribute**, not per record. Common founded rules: most-recent-updated,
most-trusted-source, most-complete, or most-frequent. Record *why* each value
survived (its source) as metadata so the golden record is explainable and
reversible.

## Hub architecture styles (pick by control needed)

* **Registry** — hub stores only keys/cross-references and matches on the fly;
  sources keep their data. Lightest, read-mostly, no single physical golden
  record. Good when systems must stay authoritative.
* **Consolidation** — sources feed a hub that builds golden records for
  downstream analytics/reporting; sources aren't updated back. Common for the
  warehouse.
* **Coexistence** — golden records are mastered in the hub *and* synced back to
  sources; bidirectional, more governance.
* **Transaction / centralized** — the hub is the system of entry and
  authoritative store; applications consume from it. Strongest control,
  highest integration cost.

## Stewardship and governance

* **Business data stewards are accountable** for controlling reference and
  master data values, working with data professionals to improve quality.
* **Govern changes to reference data**: request, communicate, and (where
  needed) approve value changes *before* implementation — a code added or
  retired silently breaks downstream consumers.
* The conformed-dimension stewardship in `conformed-dimensions` (if installed)
  is the warehouse-facing expression of these same golden/owned entities; keep
  names aligned with `CONTEXT.md`.

## Deliver

A per-entity master spec: classification (master/reference), database of record
per attribute, match strategy (deterministic/probabilistic + thresholds),
survivorship rules, chosen hub style, and the steward + change process. For
reference data, a controlled value list with an approval workflow.
