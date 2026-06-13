---
name: conformed-dimensions
description: Design an enterprise bus matrix of conformed dimensions so facts from different business processes drill across consistently. Covers conformed dimensions and facts, the bus matrix, drill-across, and avoiding stovepipe data marts. Use when more than one fact table must share dimensions or be compared, or when separate marts can't be joined.
---

# Conformed Dimensions

The reason a warehouse is more than a pile of data marts is **conformance**: a
dimension that means the same thing everywhere lets you compare measurements
from different processes side by side. This is Kimball's integration backbone.
It's the enterprise view behind the per-model design in `dimensional-modeling`
(see it if installed for the four-step process and per-dimension design).

## What "conformed" means

A **conformed dimension** is shared across two or more fact tables with
**identical keys, attribute names, and meaning**. "Customer" must be the same
customer, keyed the same way, with the same `segment` values, in Orders and in
Support Tickets — otherwise the two can't be compared. Conformance is the
*agreement*, not the copy: define the dimension **once, with the business**,
and reuse it everywhere.

Dimensions conform at two levels:

* **Identical** — the same physical dimension table used by many facts.
* **Conformed rollup** — one dimension is a strict subset of another (Month is
  a conformed rollup of Date; Brand of Product). Lower-grain facts can still
  drill across with higher-grain facts as long as the shared attributes are
  drawn from the same domain with the same values.

A **conformed fact** is a measure defined identically across processes — same
name, same unit, same business rule — so "revenue" in one mart equals
"revenue" in another. If they can't be defined identically, **name them
differently** so no one sums apples and oranges.

## The bus matrix (build this first)

The enterprise bus matrix is the master plan:

* **Rows** = business processes (Orders, Shipments, Returns, Payments).
* **Columns** = conformed dimensions (Date, Customer, Product, Store…).
* **Mark** each cell where a dimension applies to that process.

It's simultaneously your data model, your roadmap, and your prioritisation
tool. Read across a row to scope one process; read down a column to see who
shares (and must agree on) a dimension. Agree the matrix with the business
before building, then deliver **one row at a time**.

## Drill-across

To combine measurements from two facts (e.g. revenue from Orders and cost from
Shipments by product), **don't join the fact tables**. Query each fact
separately, grouping by the **conformed dimension attributes**, then merge the
two result sets on those attributes ("multi-pass / split-and-combine"). This
works precisely because the dimensions conform — and only then.

## Anti-patterns (call these out)

* **Stovepipe marts** — each team builds its own "customer" with its own keys
  and definitions; nothing can be compared and you get the "multiple versions
  of the truth" problem the warehouse was meant to solve.
* **Same name, different meaning** — two "revenue" measures computed under
  different rules. Either conform them or rename one.
* **Re-keying per mart** — assigning local surrogate keys to a shared
  dimension so identical entities don't line up across facts.
* **Conforming late** — trying to retrofit conformance after marts ship. The
  agreement is cheap up front and expensive afterward.

## Governance

Conformed dimensions are owned, not owned-by-no-one. Assign a steward per
conformed dimension responsible for its definition and change process (see
`master-data-management` if installed for golden-record/survivorship rules
when sources disagree).

## Template

For a worked bus matrix and conformed dimension DDL, see
[STAR-SCHEMA-TEMPLATE.md](../dimensional-modeling/STAR-SCHEMA-TEMPLATE.md) in
`dimensional-modeling` (sections 2–3). Use the naming from `CONTEXT.md` so the
shared concepts have one agreed name across the repo.
