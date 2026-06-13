---
name: setup-ghost-skills
description: Sets up an `## Agent skills` block in AGENTS.md/CLAUDE.md and `docs/agents/` so the ghost-skills pack knows this repo's warehouse platform & SQL dialect, transform/orchestration tooling, issue tracker (GitHub or local markdown), triage label vocabulary and domain-doc layout. Run before first use of profile-data, test-data, performance-tuning, dimensional-modeling, or data-vault — or if those skills appear to be missing context about the platform, tooling, or domain docs.
disable-model-invocation: true
---

# Setup Ghost Skills

Scaffold the per-repo configuration the data engineering skills assume (repo-level
facts only — SLAs and freshness vary per pipeline/source system and are
captured by `gather-requirements`, not here):

* **Platform & dialect** — which data warehouse or engine and SQL dialect to write for
* **Tooling** — which transform/orchestration tools are in play
* **Issue tracker** — where issues live (GitHub by default; local markdown is also supported out of the box)
* **Triage labels** — the strings used for the five canonical triage roles
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
* `docs/adr/`, `src/*/docs/adr/` directories.
* `dbt_project.yml`, `profiles.yml`, `*.sql`, `dags/`, `dagster.yaml` —
  infer the platform/tooling if you can.
* docs/agents/ — does this skill's prior output already exist?
* .scratch/ — sign that a local-markdown issue tracker convention is already in use

### 2. Present findings and ask

Summarise what's present and missing. Then walk the user through the five
decisions below **one at a time** — present a section, get the answer, then
move on. Don't dump them all at once. Assume the user may not know the terms;
start each section with a one-line explainer.

**Section A — Platform & SQL dialect.**
> Explainer: Skills like `profile-data`, `test-data`, and
> `performance-tuning` emit SQL and pick optimisation patterns. They need to
> know your engine so they use the right functions and don't suggest
> features your platform lacks.

Offer: Snowflake / BigQuery / Databricks / Redshift / Postgres / (Spark SQL) / Teradata / MSSQL / Oracle / MySQL
Other (describe in one line). Default: infer from the repo if obvious, else
ask.

**Section B — Transform & orchestration tooling.**
> Explainer: The skills need to know what artifacts to emit — dbt models and
> schema tests, Airflow DAG tasks, Dagster assets, or plain SQL scripts —
> and where your run metadata lives for performance measurement.

Offer: dbt / Airflow / Dagster / SQLMesh / plain SQL / Other (describe).
Multiple selections are fine (e.g. dbt + Airflow). Default: infer from the
repo if obvious, else ask.

**Section C — Issue tracker.**

> Explainer: The "issue tracker" is where issues live for this repo. Skills like to-issues, 
> triage, to-prd, and qa read from and write to it — they need to know whether to call gh 
> issue create, write a markdown file under .scratch/, or follow some other workflow you 
> describe. Pick the place you actually track work for this repo.

Default posture: these skills were designed for GitHub. If a git remote points at GitHub, propose that. If a git remote points at GitLab (gitlab.com or a self-hosted host), propose GitLab. Otherwise (or if the user prefers), offer:

- **GitHub** — issues live in the repo's GitHub Issues (uses the `gh` CLI)
- **GitLab** — issues live in the repo's GitLab Issues (uses the [`glab`](https://gitlab.com/gitlab-org/cli) CLI)
- **Local markdown** — issues live as files under `.scratch/<feature>/` in this repo (good for solo projects or repos without a remote)
- **Other** (Jira, Linear, etc.) — ask the user to describe the workflow in one paragraph; the skill will record it as freeform prose


**Section D — Triage label vocabulary.**

> Explainer: When the `triage` skill processes an incoming issue, it moves it through a state machine — needs evaluation, waiting on reporter, ready for an AFK agent to pick up, ready for a human, or won't fix. To do that, it needs to apply labels (or the equivalent in your issue tracker) that match strings *you've actually configured*. If your repo already uses different label names (e.g. `bug:triage` instead of `needs-triage`), map them here so the skill applies the right ones instead of creating duplicates.

The five canonical roles:

- `needs-triage` — maintainer needs to evaluate
- `needs-info` — waiting on reporter
- `ready-for-agent` — fully specified, AFK-ready (an agent can pick it up with no human context)
- `ready-for-human` — needs human implementation
- `wontfix` — will not be actioned

Default: each role's string equals its name. Ask the user if they want to override any. If their issue tracker has no existing labels, the defaults are fine.

**Section E — Domain docs.**
> Explainer: `refine-context` and the modeling skills read `CONTEXT.md` for
> the project's ubiquitous language and `docs/adr/` for past decisions. They
> need to know whether you have one global context or several.

Offer: Single-context (one `CONTEXT.md` + `docs/adr/` at root — most repos)
or Multi-context (`CONTEXT-MAP.md` pointing to per-domain `CONTEXT.md`).

### 3. Confirm and edit

Show a draft of the `## Agent skills` block and of the docs files it will
seed — `docs/agents/platform.md`, `docs/agents/tooling.md`,
`docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, and
`docs/agents/domain.md`. Let the user edit before writing.

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

```markdown
## Agent skills

### Platform
[one-line: engine + dialect]. See `docs/agents/platform.md`.

### Tooling
[one-line: transform + orchestration tools]. See `docs/agents/tooling.md`.

### Issue tracker

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### Domain docs
[one-line: single-context or multi-context]. See `docs/agents/domain.md`.

```

Then write the docs files using the seed templates in this skill folder as a starting point:

- [issue-tracker-github.md](./issue-tracker-github.md) — GitHub issue tracker
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md) — GitLab issue tracker
- [issue-tracker-local.md](./issue-tracker-local.md) — local-markdown issue tracker
- [triage-labels.md](./triage-labels.md) — label mapping
- [domain.md](./domain.md) — domain doc consumer rules + layout

### 5. Done

Tell the user setup is complete and which skills now read these files. They
can edit `docs/agents/*.md` directly later; only re-run this skill to switch
platforms or reset. Note: per-pipeline SLAs are captured by
`gather-requirements` when each pipeline is specced, and the incident
severity matrix is tailored lazily by `incident-comms` on first use.
