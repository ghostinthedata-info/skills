![Ghost Skills](https://img.shields.io/badge/skills-for%20data%20engineers-blue)

# Ghost Skills — Data-Engineering Skills For AI Coding Agents

Methodology and practice skills for AI coding agents — tuned for data
engineering, from the [Ghost in the Data](https://ghostinthedata.info) blog.
Repo structure and install flow modeled on
[mattpocock/skills](https://github.com/mattpocock/skills), but focused on the
durable, vendor-neutral parts of the data craft: profiling, requirements,
dimensional & vault modeling, keys, slowly changing dimensions, testing,
incident communications, performance, and data products.

These skills are deliberately **tool-agnostic**. There is no Snowflake-only
or BigQuery-only logic baked in — fork this repo and add a cloud-specific
layer for GCP / Azure / AWS / Databricks if you want (see `CONTRIBUTING.md`).

They are small, composable, and opinionated. Hack on them. Make them yours.

## Quickstart (30-second setup)

1. Run the installer (uses the open [skills.sh](https://skills.sh) CLI):

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
   - Ask your **domain-doc layout** (single `CONTEXT.md` or a monorepo
     `CONTEXT-MAP.md`).

   It then writes an `## Agent skills` block into **`CLAUDE.md` _or_
   `AGENTS.md`** (your choice — see below) and seeds `docs/agents/*.md`.

4. That's it — your agent now reads your data conventions before it builds.

### AGENTS.md vs CLAUDE.md — the choice

`/setup-ghost-skills` follows a strict rule (see
[ADR-0002](docs/adr/0002-claude-vs-agents-file-choice.md)):

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
agents that use `AGENTS.md`), or register this repo as a Claude Code plugin
marketplace and `/plugin install` from it.

## Why these skills exist

Data work fails in predictable ways: nobody pinned the **grain**; the
**business key** wasn't really unique; an SCD2 backfill compounded errors for
six months; a pipeline got 5% slower every month until it missed its SLA; an
incident happened and nobody told the stakeholders. None of those are tooling
problems. They're **methodology** problems. These skills encode the durable
fixes so your agent stops re-learning them every session.

## Skill catalogue

### Discovery
- **[profile-data](skills/discovery/profile-data/SKILL.md)** — Profile a new dataset before you build on it: row counts, cardinality, null/blank analysis, key-uniqueness, distributions, and an optional saved baseline for drift detection.
- **[gather-requirements](skills/discovery/gather-requirements/SKILL.md)** — Elicit and pin down requirements for a pipeline or model: grain, sources, consumers, definitions, freshness/volume SLAs, historization, and acceptance criteria — one question at a time.
- **[refine-context](skills/discovery/refine-context/SKILL.md)** — Stress-test a data plan against the project's domain model and documented decisions, sharpen terminology, and update `CONTEXT.md` and ADRs inline as decisions crystallise.

### Modeling
- **[dimensional-modeling](skills/modeling/dimensional-modeling/SKILL.md)** — Kimball's four-step process: select the business process, declare the grain, identify dimensions, identify facts. Fact-table types, conformed dimensions, and the bus matrix.
- **[data-vault](skills/modeling/data-vault/SKILL.md)** — Hubs, links, satellites; raw vault vs business vault; business-key identification; when Data Vault beats dimensional and when it doesn't.
- **[keys](skills/modeling/keys/SKILL.md)** — Business, natural, surrogate, composite, and durable ("super-natural") keys: when to use which, and the anti-patterns that bite later.
- **[slowly-changing-dimensions](skills/modeling/slowly-changing-dimensions/SKILL.md)** — SCD types 0–7, trade-offs, and the Healing Tables approach to deterministic, path-independent SCD2.

### Quality
- **[test-data](skills/quality/test-data/SKILL.md)** — A test plan you can defend: what to test (uniqueness, referential integrity, nulls, accepted values, freshness, volume/variance), severity levels, and where tests live (Write-Audit-Publish).
- **[performance-tuning](skills/quality/performance-tuning/SKILL.md)** — Measure first, find the critical path, then fix: partition pruning, incremental processing, avoiding full scans, killing phantom dependencies. Tool-agnostic.

### Operations
- **[incident-comms](skills/operations/incident-comms/SKILL.md)** — The communications workflow for a data incident: who to notify and when, severity classification, update cadence, copy-paste templates, and the post-incident review.
- **[pipeline-design](skills/operations/pipeline-design/SKILL.md)** — Idempotency, reproducibility, backfills, and defensive engineering as default design principles.
- **[data-as-a-product](skills/operations/data-as-a-product/SKILL.md)** — Data mesh thinking: domain ownership, data-as-a-product (discoverable, trustworthy, SLAs), self-serve platform, federated computational governance.

### Setup
- **[setup-ghost-skills](skills/setup/setup-ghost-skills/SKILL.md)** — Scaffold the per-repo config (warehouse/dialect, tooling, domain-doc layout) the other skills consume. Run once per repo.

## Credits & sources

Paradigms drawn from **Chris Hillman's _Ghost in the Data_**
(https://ghostinthedata.info) — Healing Tables, Write-Audit-Publish,
"Don't Go Dark", the pipeline shifting-right framing, and the data-profiling
and data-vault posts. Modeling grounded in the **Kimball Group**
(kimballgroup.com) dimensional-modeling techniques, **Dan Linstedt's Data
Vault 2.0**, and **Zhamak Dehghani's data mesh** principles. Repo structure
and install flow modeled on **Matt Pocock's**
[skills](https://github.com/mattpocock/skills) — if you want general
engineering skills (TDD, diagnosis, planning interviews), install his pack.

MIT licensed. Forks for cloud-specific extensions are encouraged.
