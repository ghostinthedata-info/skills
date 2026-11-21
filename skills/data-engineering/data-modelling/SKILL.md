---
name: data-modelling
description: Base orchestrator for designing analytics data models, following the Kimball grain-first workflow — profile source data first, then route to the right deep-dive (keys, SCD types, SCD1, SCD2, backfilling and healing, fact-table design). Use this skill whenever the user is designing, building, or refactoring dimensions, facts, a star schema, a dimensional model, or a gold/presentation layer; whenever they mention dims, facts, grain, SCD/slowly-changing dimensions, surrogate keys, or history tracking; or when they ask "how should I model this?" — even if they don't explicitly say "data modelling". Always clarify grain and history requirements BEFORE emitting DDL.
---

# Data Modelling

This is the **entry point** for any analytics modelling task. It does not do
the deep work itself — it sequences the work and hands off to the reference
files below.

Write SQL for the engine named in `docs/agents/platform.md`. If that file
doesn't exist, ask which engine once, or write portable SQL and mark the lines
that are dialect-specific. The reference files are engine-agnostic: portable,
ANSI-style SQL (standard types, `MERGE`, `IS DISTINCT FROM`, window
functions), with engine features described by what they do ("a zero-copy
clone, if your engine has one") rather than by product. Translate them to the
target dialect; never let one engine's syntax become the default.

Kimball's core move: **separate measurements (facts) from context
(dimensions)**, declare the grain before anything else, and pick history
policy per attribute. Never default everything to Type 2.

## Workflow (do not reorder)

### 0. Profile first — you cannot model what you haven't profiled

Before any design, run the **`profile-data`** skill (if installed) on each
source table. You need row counts, candidate-key uniqueness, null/blank
rates, cardinality, and type/precision facts. **Do not declare a key or a
grain until key-uniqueness passes.** If `profile-data` is not installed, at
minimum confirm `COUNT(*) = COUNT(DISTINCT <business_key>)` and check the key
for nulls.

### 1. Clarify before designing — ask, don't assume

A fuzzy grain is the #1 dimensional-design failure. Ask the questions in the
**Clarifying questions** section below and wait for answers before emitting
DDL. The most expensive modelling mistakes are committed silently at this
step.

### 1a. Confirm the layer and the shape — a star is a default, not a rule

The model takes the shape of the question, not of the framework. Confirm which
layer this is and what its consumer needs before reaching for a star:

* **Reporting / BI layer** → a star: facts and conformed dimensions. This is
  the default, and where Kimball earns its keep.
* **Integration layer** (between raw and presentation) → stay close to the
  sources (normalised, or Data Vault); don't force dimensions here.
* **Feature store / ML** → flatter and wider: one row per entity per as-of
  time, with every feature as it was known at that time (no leakage from
  later corrections).
* **Prototype or a one-off with a single consumer** → one big table is fine.
  Write down the hardening plan with it — the prototype becomes the spec for
  the star.

If every consumer needs a relationship the star can't express cleanly (a
many-to-many), model it — a bridge ([DIMENSIONS.md](./DIMENSIONS.md)) or a
different shape — rather than build a star the analysts route around.

### 1b. If the model already exists, refactor it — don't redesign it

A rewrite throws away the reasons behind every odd filter and join. Refactor
in small, proven steps instead:

1. List the consumers and the behaviour they depend on (columns, order, null
   handling, precision).
2. Find out why each odd filter, join, or Type 2 attribute exists before you
   touch it — someone usually needed it.
3. Port the legacy logic unchanged and prove the output matches row for row,
   column for column. That's the baseline.
4. Restructure in small steps, diffing against the baseline after each. Don't
   fix data-quality issues mid-refactor — log them and fix them separately.
5. For breaking changes, expand (add the new shape), migrate consumers one at
   a time, then contract (remove the old). Publish through write-audit-publish.

Add the baseline diff to the output contract below.

### 2. Apply the four-step Kimball process

Summary (dimension techniques, conformed dimensions, and the bus matrix are in
[DIMENSIONS.md](./DIMENSIONS.md)):

1. **Select the business process** — the verb (taking an order, a payment).
2. **Declare the grain** — one unambiguous sentence; most atomic possible.
3. **Identify the dimensions** — who/what/where/when/why/how.
4. **Identify the facts** — numeric measures true to the grain.

### 3. Design the facts

Use [FACT-TABLES.md](./FACT-TABLES.md) — transaction vs periodic vs
accumulating snapshot, additivity classification for every measure, factless
facts, and degenerate dimensions.

### 4. Design the dimensions and choose history policy per attribute

Surrogate-key every dimension; keep the natural/business key as a column for
lineage, and for SCD2 carry the **durable ("super-natural") key** that ties
all versions of an entity together — and put that durable key on the fact too,
so you can report all history by current attributes. See
[KEYS.md](./KEYS.md) for the full decision rules, composite-key validation,
and anti-patterns. Most warehouses don't enforce key uniqueness — **test**
every key for unique + not-null.

For each dimension attribute, decide the SCD type with
[SCD-TYPES.md](./SCD-TYPES.md) (the full 0–7 catalogue). For the two you'll
reach for >90% of the time, use the implementation references:

* [SCD1.md](./SCD1.md) — overwrite (Type 1).
* [SCD2.md](./SCD2.md) — history rows (Type 2).

### 5. Build, backfill, or heal SCD2 history

With full source history, build SCD2 deterministically — as a one-off
backfill, as the main build for batch dimensions, or as a scheduled heal
alongside daily incremental loads. See [BACKFILLING.md](./BACKFILLING.md) for
the preconditions and the deterministic, rebuildable (Healing Tables)
approach — rebuild into a copy, stage before you publish, land history by
partition — and [HEALING-TABLE-TEMPLATE.md](./HEALING-TABLE-TEMPLATE.md) for
tool-agnostic pseudo-SQL of all six steps.

## Clarifying questions (ask these before emitting DDL)

Ask only the ones not already answered by profiling or the user:

0. **Layer & consumer** — reporting/BI, feature store, or prototype? Who reads
   it, and with what tool? (Step 1a.)
1. **Grain** — what does exactly one row in the target table represent, in
   business terms? (If they can't say it in one sentence, the grain isn't set.)
2. **Business process / fact type** — is this a measurement event
   (transaction), a state-at-a-point (periodic snapshot), or a workflow with
   milestones (accumulating snapshot)?
3. **Business key** — which column(s) uniquely identify the entity? Did
   uniqueness pass in profiling?
4. **History** — for each changing attribute: does anyone need to know its
   value *as of a past date*? If yes → Type 2; if only "latest" matters →
   Type 1; if it never changes → Type 0.
5. **Source history available?** — is full source history present (enables a
   clean backfill/rebuild), or only current state going forward? Does the
   source physically delete rows? Can an entity disappear and reappear?
6. **Volume & latency** — high-volume/real-time (favours plain incremental)
   or batch with acceptable rebuild time (favours Healing-Table rebuild)?
7. **Measures** — what gets counted/summed, and is each one additive,
   semi-additive (don't sum over time), or non-additive (a ratio — store the
   components)?

## Reference files (deeper knowledge)

| File | When to open it |
|---|---|
| [DIMENSIONS.md](./DIMENSIONS.md) | Dimension design rules and techniques, the generated date dimension, conformed dimensions, bus matrix, aggregates. |
| [KEYS.md](./KEYS.md) | Business/surrogate/composite/durable keys, naming, anti-patterns. |
| [SCD-TYPES.md](./SCD-TYPES.md) | Choosing a history policy per attribute — SCD types 0–7, and periodic full snapshots as an alternative to Type 2. |
| [SCD1.md](./SCD1.md) | Overwrite-in-place dimension attributes. |
| [SCD2.md](./SCD2.md) | History-tracking dimensions, effectivity intervals, validation. |
| [BACKFILLING.md](./BACKFILLING.md) | Building, backfilling, or periodically healing SCD2 history deterministically; preconditions; multi-source and snapshot sources. |
| [HEALING-TABLE-TEMPLATE.md](./HEALING-TABLE-TEMPLATE.md) | Tool-agnostic pseudo-SQL for the six Healing-Table steps. |
| [FACT-TABLES.md](./FACT-TABLES.md) | Fact grain, the three types, additivity, factless/degenerate. |

## Related skills (compose with these if installed)

* `profile-data` — run first (step 0).
* `gather-requirements` / `solution-design` — pin grain, consumers, and
  history needs before you model.
* `test-data` — key, referential-integrity, and SCD2 temporal-integrity tests.
* `data-security-classification` — classify columns as you design them.

## Output contract

End every modelling task with: the **one-sentence grain** per table, the
chosen **fact type** (or SCD type per attribute), candidate-key **uniqueness
verdict**, and a **DDL skeleton** in the target dialect. Use naming from
`CONTEXT.md` if present.
