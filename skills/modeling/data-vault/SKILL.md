---
name: data-vault
description: Model an integration layer with Data Vault 2.0 — hubs, links, satellites; raw vault vs business vault; business-key identification; hash keys. Use when integrating many source systems, when sources change schema often, when full auditability/lineage is required, or when deciding between Data Vault and dimensional modeling.
---

# Data Vault

Data Vault is an **integration-layer** technique: a hybrid of 3NF and star
schema built for auditability and for absorbing source-system change without
rebuilds (Dan Linstedt's Data Vault 2.0; Ghost in the Data, "Data Vault
Modeling with Python and dbt"). It is *not* a presentation layer — build
Kimball stars on top for consumers.

## The three structures

* **Hub** — the list of unique **business keys** for a core entity (customer
  number, VIN, order code). Contains only: business key, a hash key, load
  date, record source. No descriptive attributes. Stable forever.
* **Link** — a relationship between hubs (customer placed order at store).
  Contains the related hub hash keys, its own hash key, and metadata. No
  descriptive attributes. Can connect more than two hubs.
* **Satellite** — all the descriptive, time-variant attributes hanging off a
  hub or link. Insert-only; a new row when a `hash_diff` of the attributes
  changes. This is where history lives.

## Data Vault 2.0 essentials

* **Hash keys** (a hash of the business key) replace sequence surrogates so
  hubs, links, and satellites load **in parallel** with no dependencies.
  Tip: keep the business key in at least one satellite so you can debug a
  hash.
* Insert-only + load-date + record-source = complete, automatic lineage.

## Raw vault vs business vault

* **Raw Vault** — pure integration. No business rules; only key hashing and
  change detection. It records exactly what each source said, when. You must
  be able to reload it entirely from sources at any time.
* **Business Vault** — additive layer on top: derived links ("same-as" to
  dedupe a customer across sources), computed satellites, bridge/PIT tables.
  Business logic lives here, separate from raw and from the marts.

## When to use Data Vault vs dimensional

* **Use Data Vault** when you integrate many sources, sources change schema
  often, or regulators require full audit/lineage.
* **Use dimensional directly** when sources are few and stable and consumers
  want speed and simplicity.
* **Polyglot is the mature answer:** Vault (or 3NF) in the silver/integration
  layer for flexibility + auditability; Kimball stars in the
  gold/presentation layer for query performance and business usability.

## Anti-patterns (call these out)

* Descriptive columns on a hub — they belong in a satellite.
* Skipping the business vault and smearing business logic across mart views.
* Over-debating hash algorithm choice instead of shipping.
