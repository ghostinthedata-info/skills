# CONTEXT.md — the glossary format

`CONTEXT.md` is the project's shared vocabulary: what each business term means
*here*, precisely enough that two people can't compute the same metric two
ways. Create it the first time a term is settled, not before. Keep one file at
the repo root unless the repo has a `CONTEXT-MAP.md` (see *Several contexts*).

## Two kinds of entry

Almost everything in a data project is one of these.

**An entity or a state** — a thing, or a condition a thing can be in:

```md
### Active customer
A customer with at least one paid order in the last 90 days, counted back from
the order date.
- Source of truth: paid orders in the billing system — not the CRM's status field.
- Avoid: live customer, current customer, "active" in the CRM's sense.
```

**A metric** — something people count, sum, or average:

```md
### Net revenue
Gross order value minus discounts and refunds, in the reporting currency,
recognised on the order date.
- Grain: one value per order line.
- Rule: line_amount - discount_amount - refund_amount, with refunds made within
  30 days netted back to the original order date.
- Additivity: additive across every dimension.
- Avoid: revenue (ambiguous), sales, turnover.
```

## Writing entries

* **One meaning per term.** Use the word the business already uses for the
  meaning you agreed, and put the rival words under *Avoid*.
* **Precise enough to compute.** State the time window, the date it's counted
  from, what's excluded, and the source of truth. "Customers who are active"
  isn't a definition.
* **Business vocabulary only.** Engineering terms ("incremental model", "CTE",
  "staging") don't belong here, however often the project uses them.
* **Record changes; don't rewrite history.** When a definition changes, update
  it and add `- Changed YYYY-MM-DD: was …`, so last quarter's report can still
  be explained.
* **Group by subject area** (Customers, Orders, Finance) once there are more
  than a dozen terms.

## Several contexts

When parts of the business use the same word differently — Sales' "customer"
is anyone with an opportunity, Finance's is anyone invoiced — give each area
its own `CONTEXT.md` and list them in a `CONTEXT-MAP.md` at the root:

```md
# Context map

- [Sales](./domains/sales/CONTEXT.md) — pipeline, opportunities, bookings
- [Finance](./domains/finance/CONTEXT.md) — invoicing, revenue recognition

## Shared or contested terms

- **Customer** — Sales: anyone with an opportunity. Finance: anyone invoiced.
  The conformed `dim_customer` follows Finance; Sales' meaning is a flag on it.
```

Which file to write to:

* `CONTEXT-MAP.md` exists → the context the topic belongs to (ask if it's
  unclear).
* Only a root `CONTEXT.md` → that one.
* Neither → create a root `CONTEXT.md` with the first settled term.
