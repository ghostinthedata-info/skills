---
name: setup-ghost-skills
description: Sets up an `## Agent skills` block in AGENTS.md/CLAUDE.md and `docs/agents/` so the ghost-skills pack knows this repo's warehouse platform & SQL dialect, transform/orchestration tooling, and domain-doc layout. Run before first use of profile-data, test-data, performance-tuning, dimensional-modeling, or data-vault — or if those skills appear to be missing context about the platform, tooling, or domain docs.
disable-model-invocation: true
---

# Setup Ghost Skills

Scaffold the per-repo configuration the ghost skills assume (repo-level
facts only — SLAs and freshness vary per pipeline/source system and are
captured by `gather-requirements`, not here):

* **Platform & dialect** — which warehouse/engine and SQL dialect to write for
* **Tooling** — which transform/orchestration tools are in play
* **Domain docs** — where `CONTEXT.md` and ADRs live

This is a prompt-driven skill, not a deterministic script. Explore, present
what you found, confirm with the user, then write.

## Process

### 1. Explore

Read whatever exists; don't assume.

* `git remote -v` — host and repo name.
* `AGENTS.md` and `CLAUDE.md` at the root — does either exist? Already an
  `## Agent skills` section?
* `CONTEXT.md` and `CONTEXT-MAP.md` at the root.
* `docs/adr/`, `docs/agents/`.
* `dbt_project.yml`, `profiles.yml`, `*.sql`, `dags/`, `dagster.yaml` —
  infer the platform/tooling if you can.

### 2. Present findings and ask

Summarise what's present and missing. Then walk the user through the three
decisions **one at a time** — present a section, get the answer, then move
on. Don't dump all three at once. Assume the user may not know the terms;
start each section with a one-line explainer.

**Section A — Platform & SQL dialect.**
> Explainer: Skills like `profile-data`, `test-data`, and
> `performance-tuning` emit SQL and pick optimisation patterns. They need to
> know your engine so they use the right functions and don't suggest
> features your platform lacks.

Offer: Snowflake / BigQuery / Databricks (Spark SQL) / Redshift / Postgres /
Other (describe in one line). Default: infer from the repo if obvious, else
ask.

**Section B — Transform & orchestration tooling.**
> Explainer: The skills need to know what artifacts to emit — dbt models and
> schema tests, Airflow DAG tasks, Dagster assets, or plain SQL scripts —
> and where your run metadata lives for performance measurement.

Offer: dbt / Airflow / Dagster / SQLMesh / plain SQL / Other (describe).
Multiple selections are fine (e.g. dbt + Airflow). Default: infer from the
repo if obvious, else ask.

**Section C — Domain docs.**
> Explainer: `refine-context` and the modeling skills read `CONTEXT.md` for
> the project's ubiquitous language and `docs/adr/` for past decisions. They
> need to know whether you have one global context or several.

Offer: Single-context (one `CONTEXT.md` + `docs/adr/` at root — most repos)
or Multi-context (`CONTEXT-MAP.md` pointing to per-domain `CONTEXT.md`).

### 3. Confirm and edit

Show a draft of the `## Agent skills` block and of
`docs/agents/platform.md`, `docs/agents/tooling.md`, `docs/agents/domain.md`.
Let the user edit before writing.

### 4. Write — pick the file to edit

* If `CLAUDE.md` exists, edit it.
* Else if `AGENTS.md` exists, edit it.
* If neither exists, **ask the user which one to create — don't pick for
  them.**
* **Never** create `AGENTS.md` when `CLAUDE.md` already exists (or vice
  versa) — always edit the one that's already there.
* If an `## Agent skills` block already exists, update it in place rather
  than appending a duplicate. Don't overwrite the user's surrounding edits.

The block:

    ## Agent skills

    ### Platform
    [one-line: engine + dialect]. See `docs/agents/platform.md`.

    ### Tooling
    [one-line: transform + orchestration tools]. See `docs/agents/tooling.md`.

    ### Domain docs
    [one-line: single-context or multi-context]. See `docs/agents/domain.md`.

Then write the three `docs/agents/*.md` files from the answers.

### 5. Done

Tell the user setup is complete and which skills now read these files. They
can edit `docs/agents/*.md` directly later; only re-run this skill to switch
platforms or reset. Note: per-pipeline SLAs are captured by
`gather-requirements` when each pipeline is specced, and the incident
severity matrix is tailored lazily by `incident-comms` on first use.
