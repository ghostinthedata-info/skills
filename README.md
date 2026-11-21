[![skills.sh](https://www.skills.sh/b/ghostinthedata-info/skills)](https://www.skills.sh/ghostinthedata-info/skills)
![Ghost Skills](https://img.shields.io/badge/skills-for%20data%20engineers-blue)

# Ghost Skills — Data-Engineering Skills For AI Coding Agents

Methodology and practice skills for AI coding agents — tuned for data
engineering, from the [Ghost in the Data](https://ghostinthedata.info) blog.
Focused on the durable, vendor-neutral parts of the data craft: profiling,
requirements and solution design, tickets and triage, dimensional modelling
(keys, slowly changing dimensions, facts, backfills), test-first
transformations, testing and reconciliation, diagnosis, performance, incident
management, and security classification.

These skills are deliberately **tool-agnostic**. There is no Snowflake-only
or BigQuery-only logic baked in — fork this repo and add a cloud-specific
layer for GCP / Azure / AWS / Databricks if you want.

They are small, composable, and opinionated. Hack on them. Make them yours.

## Quickstart (30-second setup)

1. Run the installer:

   ```
   npx skills@latest add ghostinthedata-info/skills
   ```

2. Pick the skills you want and which coding agents to install them on
   (Claude Code, Codex, Cursor, etc.). **Make sure you select
   `setup-ghost-skills`.**

3. Run `/setup-ghost-skills` in your agent. It will, one question at a time:

   - Ask which **warehouse platform and SQL dialect** you target
     (Snowflake, BigQuery, Databricks/Spark, Redshift, Postgres, or "other").
   - Ask which **transform/orchestration tooling** you use
     (dbt, Airflow, Dagster, SQLMesh, plain SQL, or "other").
   - Ask where your **issues live** (GitHub, GitLab, local markdown, or
     another tracker) and which **triage labels** you use.
   - Ask your **domain-doc layout** (single `CONTEXT.md` or a monorepo
     `CONTEXT-MAP.md`).

   It then writes an `## Agent skills` block into **`CLAUDE.md` _or_
   `AGENTS.md`** (your choice — see below) and seeds `docs/agents/*.md`.

4. That's it — your agent now reads your data conventions before it builds.

### AGENTS.md vs CLAUDE.md — the choice

`/setup-ghost-skills` follows a strict rule:

- If `CLAUDE.md` already exists → it edits `CLAUDE.md`.
- Else if `AGENTS.md` exists → it edits `AGENTS.md`.
- If **neither** exists → it **asks you which one to create**. It will not
  pick for you.
- It will **never** create `AGENTS.md` when `CLAUDE.md` exists (or vice
  versa), and if an `## Agent skills` block already exists it updates it
  in place instead of appending a duplicate.

Prefer `AGENTS.md` if you use multiple agents (Codex, Cursor, Gemini, etc.);
prefer `CLAUDE.md` if you're Claude-Code-only. Both are plain Markdown and
the skills read either.

### Manual install (no CLI)

Copy any skill folder into your agent's skills directory
(`.claude/skills/<name>/` for Claude Code, `.agents/skills/<name>/` for
agents that use `AGENTS.md`), or install the whole pack as a Claude Code
plugin:

```
/plugin marketplace add ghostinthedata-info/skills
/plugin install ghost-skills@ghost-skills
```

## Why these skills exist

Data work fails in predictable ways: nobody pinned the **grain**; the
**business key** wasn't really unique; an SCD2 backfill compounded errors for
six months; a pipeline got 5% slower every month until it missed its SLA; an
incident happened and nobody told the stakeholders. None of those are tooling
problems. They're **methodology** problems. These skills encode the durable
fixes so your agent stops re-learning them every session.

## Skill catalogue

### Discovery
- **[profile-data](skills/data-engineering/profile-data/SKILL.md)** — Profile a new dataset before you build on it: row counts, cardinality, null/blank analysis, key-uniqueness, distributions, and an optional saved baseline for drift detection. Hands the keys and grain to modelling and the tagged columns to testing.
- **[gather-requirements](skills/data-engineering/gather-requirements/SKILL.md)** — The *what* and *why*: value and consumers, grain, sources and their owners, metric definitions, freshness/volume SLAs, history needs, and acceptance criteria — one question at a time. Produces a one-page requirements spec, records terms in `CONTEXT.md` and hard-to-reverse decisions as ADRs, and can publish the spec to your issue tracker.
- **[solution-design](skills/data-engineering/solution-design/SKILL.md)** — The *how* and *when*, starting from the requirements spec: source mechanics, a pattern recipe with an SVG overview, the design rules every load follows, day-sized stories with handovers and seams, an estimate, a decisions register, and risks.

### Delivery
- **[to-tickets](skills/data-engineering/to-tickets/SKILL.md)** — Turn a solution design's stories, or any agreed plan, into tracker tickets: day-sized slices with a done-when, a handover, what each needs to start, and blocking links, labelled for triage.
- **[triage](skills/data-engineering/triage/SKILL.md)** — Sort incoming data work: route incidents and access requests, reproduce "this number looks wrong" with a query before labelling it, answer definition questions from the glossary, and move every ticket to one of five triage roles with a brief for whoever picks it up.

### Modeling
- **[data-modelling](skills/data-engineering/data-modelling/SKILL.md)** — Entry point for analytics modelling, Kimball grain-first: profile, pin grain and history, then design facts (transaction / periodic / accumulating, additivity), dimensions and keys (surrogate, durable, conformed, the bus matrix), SCD types 0–7 with SCD1/SCD2 implementations, and deterministic Healing-Table backfills.

### Quality
- **[tdd](skills/data-engineering/tdd/SKILL.md)** — Test-first transformations: fixture rows in, the exact rows the definition demands out, watch it fail, write the least SQL, then add the edge cases (NULLs, duplicates, late rows, boundaries, unmatched keys, re-runs). Shapes for dbt and SQLMesh unit tests, plain SQL, and pytest.
- **[test-data](skills/data-engineering/test-data/SKILL.md)** — A test plan you can defend: what to test (uniqueness, referential integrity, nulls, accepted values, freshness, volume/variance), severity levels, and where tests live (Write-Audit-Publish).
- **[reconcile-data](skills/data-engineering/reconcile-data/SKILL.md)** — Prove a changed model or a migrated table matches its source of truth: counts and key-set diffs, then per-column checksums, then a cell-by-cell diff, stopping at the first break — and graduate the keepers into permanent tests.
- **[performance-tuning](skills/data-engineering/performance-tuning/SKILL.md)** — Measure first, find the critical path, then fix: partition pruning, incremental processing, avoiding full scans, killing phantom dependencies. A tool-agnostic method plus engine references for Oracle/SQL Server, cloud warehouses, and Spark (shuffles, skew, broadcast joins, caching).

### Operations
- **[diagnose](skills/data-engineering/diagnose/SKILL.md)** — Find out why a number is wrong: pin the symptom, reproduce it with a query, bisect the lineage hop by hop to the transformation that breaks it, test one hypothesis at a time, fix the cause rather than the output, and leave a regression test.
- **[data-incident-management](skills/data-engineering/data-incident-management/SKILL.md)** — Work a data or reporting incident end to end: classify severity (D1–D4), contain, notify on a set cadence with copy-paste emails, resolve, run a blameless post-incident review, and feed the fix back as a permanent test or monitor.
- **[data-security-classification](skills/data-engineering/data-security-classification/SKILL.md)** — Classify every column by sensitivity and recommend the controls: the metadata to record with the model, masking or pseudonymisation, an RBAC role grid, encryption and auditing, retention and deletion, and controls on every copy. Runs after profiling and inside solution design.

### Management
- **[de-feedback](skills/management/de-feedback/SKILL.md)** — Honest, empathetic feedback for data engineers at any level: set the expected level (SFIA-anchored), rate observed behaviour as underperform / meet / exceed across technical, delivery, collaboration, and leadership rubrics, write the narrative, and keep a running per-engineer log for growth conversations.

### Productivity
- **[caveman](skills/productivity/caveman/SKILL.md)** — Terse reply mode for data work: no filler, pleasantries or hedging, but every fact, number and identifier kept exact — and full sentences whenever something is destructive.
- **[write-a-skill](skills/productivity/write-a-skill/SKILL.md)** — Write or rework a skill for this pack: pin the decision it owns, place and name it, write a description that triggers, keep SKILL.md short with reference files for depth, and register it until the governance checker passes.

### Setup
- **[setup-ghost-skills](skills/setup/setup-ghost-skills/SKILL.md)** — Scaffold the per-repo config the other skills consume (warehouse/dialect, tooling, issue tracker, triage labels, domain-doc layout). Run once per repo.

Drafts live in [`skills/in-progress/`](skills/in-progress/) and aren't part of the pack until they're promoted.

## Credits & sources

Paradigms drawn from **Chris Hillman's _Ghost in the Data_**
(https://ghostinthedata.info) — Healing Tables, Write-Audit-Publish,
"Don't Go Dark", the pipeline shifting-right framing, and the data-profiling
and data-vault posts. Modeling grounded in the **Kimball Group**
(kimballgroup.com) dimensional-modeling techniques and **Dan Linstedt's Data
Vault 2.0**.

MIT licensed. Forks for cloud-specific extensions are encouraged.
