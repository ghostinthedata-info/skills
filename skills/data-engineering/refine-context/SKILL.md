---
name: refine-context
description: Grilling session that challenges your data plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. Use when the user wants to stress-test a model/pipeline plan against their project's language and documented decisions, or says "refine context".
disable-model-invocation: true
---

# Refine Context

Interview the user relentlessly about every aspect of this plan until you
reach shared understanding. Walk down each branch of the design tree, one
question at a time, giving your recommended answer each time. If a question
can be answered by exploring the warehouse/repo, explore instead of asking.

## Domain awareness

During exploration, look for existing docs:

    /
    ├── CONTEXT.md          ← ubiquitous language / glossary
    └── docs/adr/           ← architecture decision records

If `CONTEXT-MAP.md` exists, the repo has multiple domains; the map points to
each domain's `CONTEXT.md`. Create files lazily — only when you have
something to write.

## During the session

**Challenge against the glossary.** When the user uses a term that conflicts
with `CONTEXT.md`, call it out: "Your glossary defines 'order' as the header;
you seem to mean the line item — which is it?"

**Sharpen fuzzy language.** Replace vague terms with one canonical term.
"'Account' — do you mean the billing Account or the login User? Different
grains, different keys."

**Probe with concrete scenarios.** Invent edge cases that force precision:
"A customer is refunded after 40 days — is that revenue, negative revenue, or
excluded? Which fact row changes?"

**Cross-reference the data.** When the user states how something works, check
whether the data agrees (profile it — see `profile-data` if installed).
Surface contradictions: "You said one order has one customer, but 0.3% of
orders have two customer_ids."

**Update CONTEXT.md inline.** When a term resolves, write it down right then —
don't batch. Keep it domain-level, not implementation detail. CONTEXT.md is
a glossary, not a spec or scratch pad.

**Offer ADRs sparingly.** Only when all three hold: (1) hard to reverse,
(2) surprising without context, (3) the result of a real trade-off. Examples
worth an ADR: "why incremental not full refresh", "why we exclude post-30-day
returns", "why this warehouse over that one". Three paragraphs and a status
field; fifteen minutes; saves a future meeting (Ghost in the Data,
"Don't Go Dark").
