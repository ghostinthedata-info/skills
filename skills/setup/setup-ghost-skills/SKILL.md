---
name: setup-ghost-skills
description: One-time setup that records this repo's facts for the ghost-skills pack — warehouse platform and SQL dialect, transform and orchestration tooling, where issues are tracked (GitHub, GitLab, local markdown, or another tracker), the triage label vocabulary, and the domain-doc layout — as an "## Agent skills" block in CLAUDE.md or AGENTS.md plus files in docs/agents/. Run it before first using the pack in a repo, or when a skill seems to be missing the platform, tooling, tracker, labels, or domain docs.
disable-model-invocation: true
---

# Setup Ghost Skills

The pack's skills read a handful of repo-level facts instead of asking for
them every session. This skill finds out what it can, asks for the rest, and
writes them down once. It records only facts that hold for the whole repo —
SLAs and freshness differ per pipeline, so `gather-requirements` captures
those when each pipeline is specced.

| Fact | Written to | Read by |
|---|---|---|
| Platform and SQL dialect | `docs/agents/platform.md` | `profile-data`, `data-modelling`, `test-data`, `reconcile-data`, `diagnose`, `tdd`, `performance-tuning` |
| Transform and orchestration tooling | `docs/agents/tooling.md` | `test-data`, `reconcile-data`, `tdd`, `data-security-classification`, `performance-tuning` |
| Issue tracker | `docs/agents/issue-tracker.md` | `to-tickets` and `triage` (required), `gather-requirements` (publishes its spec), `data-incident-management` (logs incidents) |
| Triage labels | `docs/agents/triage-labels.md` | `triage` and `to-tickets` (required), `gather-requirements` (labels the spec) |
| Domain-doc layout | `docs/agents/domain.md` | `gather-requirements` (writes the glossary and ADRs), `data-modelling`, `solution-design`, `to-tickets`, `triage`, `diagnose` |

This is a conversation, not a script: look first, show what you found, confirm,
then write.

## 1. Look before asking

Read what's there; don't assume.

* `git remote -v` — the host (GitHub, GitLab, self-hosted) and the repo name.
* `CLAUDE.md` and `AGENTS.md` at the root — which exists, and whether either
  already has an `## Agent skills` block.
* `CONTEXT.md`, `CONTEXT-MAP.md`, and any `docs/adr/` folders.
* Tooling clues: `dbt_project.yml`, `profiles.yml`, SQLMesh or Dagster
  config, an Airflow `dags/` folder, the dialect of existing `*.sql`.
* `docs/agents/` — the output of an earlier run.
* `.scratch/` — a sign that local-markdown tickets are already in use.

## 2. Ask the five questions, one at a time

For each, say in one line why the skills need it, offer what you found as the
recommended answer, and wait for the reply. The user may not know the terms —
explain rather than quiz.

**A. Platform and SQL dialect.** Skills that write SQL need the engine, so they
use functions it has and features it supports: Snowflake, BigQuery, Databricks
/ Spark SQL, Redshift, Postgres, SQL Server, Oracle, Teradata, MySQL, or
another (one line).

**B. Transform and orchestration tooling.** Skills emit artefacts in your
tools' shapes — models and tests, DAG tasks, assets — and read run history
from them: dbt, SQLMesh, Dagster, Airflow, plain SQL, or another. More than one
is normal (dbt with Airflow).

**C. Issue tracker.** Where this repo's work is tracked, so skills that publish
or read tickets do it in the right place. Propose what the remote suggests —
GitHub (via `gh`) or GitLab (via `glab`) — or local markdown under `.scratch/`
for a solo repo or one with no remote. For anything else (Jira, Linear, …),
ask for a paragraph on how tickets are created, read, labelled, and closed,
and record that.

**D. Triage labels.** Skills move tickets through five roles — needs
evaluation, waiting on the reporter, ready for an agent, ready for a person,
won't do — and need *your* label for each, or they'll create duplicates. The
defaults are `needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`; ask whether the tracker already uses different
strings.

**E. Domain docs.** Where the glossary and decisions live: one `CONTEXT.md` and
`docs/adr/` at the root (most repos), or a `CONTEXT-MAP.md` pointing to a
`CONTEXT.md` per area.

## 3. Show the drafts

Draft the `## Agent skills` block and each `docs/agents/` file, and let the user
edit them before anything is written. Start from the seed files in this folder:

* [issue-tracker-github.md](./issue-tracker-github.md),
  [issue-tracker-gitlab.md](./issue-tracker-gitlab.md), or
  [issue-tracker-local.md](./issue-tracker-local.md) — whichever matches the
  tracker
* [triage-labels.md](./triage-labels.md) — the label mapping
* [domain.md](./domain.md) — the layout, and how skills use it

`platform.md` and `tooling.md` have no seed; keep them short — the engine and
dialect (and version, where it matters); the tools, what each is used for,
and where run history lives.

The block:

```markdown
## Agent skills

### Platform
<engine and dialect, one line>. See `docs/agents/platform.md`.

### Tooling
<transform and orchestration tools, one line>. See `docs/agents/tooling.md`.

### Issue tracker
<where tickets live, one line>. See `docs/agents/issue-tracker.md`.

### Triage labels
<the defaults, or what's mapped>. See `docs/agents/triage-labels.md`.

### Domain docs
<single context, or several>. See `docs/agents/domain.md`.
```

## 4. Write

* Put the block in whichever of `CLAUDE.md` and `AGENTS.md` already exists —
  `CLAUDE.md` if both do.
* If neither exists, ask which to create. Never create one when the other is
  already there.
* If an `## Agent skills` block exists, update it in place and leave the rest
  of the file alone.
* Write the `docs/agents/` files.

## 5. Finish

Tell the user what was written and which skills read each file (the table at
the top). From now on they can edit `docs/agents/*.md` by hand; re-run this
skill only to change platform or tracker, or to start over. Per-pipeline SLAs
are captured by `gather-requirements` when each pipeline is specced, and
`data-incident-management` records the team's incident specifics in
`docs/agents/incident.md` the first time it runs.
