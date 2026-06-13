---
name: data-as-a-product
description: Apply data mesh thinking — domain ownership, data-as-a-product, self-serve platform, and federated computational governance. Use when designing data ownership/org structure, deciding who owns a dataset, defining data-product SLAs, or scaling beyond a single central data team.
---

# Data as a Product

Data mesh is an organisational + architectural shift,
**not a tool you install**. Reach for it when a single central team has
become the bottleneck for many domains. Four interlocking principles —
apply them together; any one alone fails.

## 1. Domain-oriented ownership

The domain that understands the data owns it end-to-end — ingestion through
serving. Align ownership with the **business** (sales, finance, marketing),
not with technology. This is the hardest shift and the foundation for the
rest.

## 2. Data as a product

Treat consumers as customers and the dataset as a product. A real data
product is **discoverable, addressable, trustworthy (with explicit SLAs),
self-describing, and interoperable.** It ships with its code, metadata,
tests, and documentation — not just a table. Define freshness/quality SLAs
per product and own them (see `gather-requirements` and `test-data` if
installed).

## 3. Self-serve platform

Give domain teams a harmonised, automated platform so they can ingest,
transform, test, and publish products without filing tickets with a central
team. **Underinvesting here is the classic failure** — if self-serve is
painful, teams build shadow infra and the mesh collapses.

## 4. Federated computational governance

Set global standards centrally (interoperability, security, conformed key
formats, naming) but **enforce them as automated checks**, not manual
reviews. Too much autonomy with no governance → incompatible silos; too much
central control → the bottleneck you were escaping.

## Practical guidance

* **Migrate incrementally.** Big-bang decentralisation overwhelms teams.
  Start with one or two domains.
* Conformed dimensions are how you keep "customer" and "revenue" meaning the
  same across federated domains — governance with teeth (see
  `dimensional-modeling` if installed).
* Don't adopt the org model just for the buzzword; if you're a small single
  team, plain good modeling + ownership clarity may be all you need.
