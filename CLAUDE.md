# Governance

This is the publisher repo for the **ghost-skills** pack. Skills are
organized into bucket folders under `skills/`:

* `data-engineering/` — the published data-engineering pack (profiling,
  requirements and solution design, tickets and triage, modelling — keys,
  SCDs, facts, backfills — test-first transformations, testing,
  reconciliation and change review, diagnosis, performance, incidents, security
  classification)
* `management/`       — leading and developing data engineers (`de-feedback`)
* `setup/`            — one-time per-repo configuration (`setup-ghost-skills`)
* `productivity/`     — general-purpose authoring/comms skills
* `in-progress/`      — drafts not yet promoted; not published

Every skill in `data-engineering/`, `management/`, `productivity/`, or
`setup/` must have a reference in the top-level `README.md` and an entry in
`.claude-plugin/plugin.json`. Skills in `in-progress/` must not appear in
either until promoted out of that folder.

Each skill entry in the top-level `README.md` must link the skill name to
its `SKILL.md`. A skill's folder name must equal the `name` in its
`SKILL.md` frontmatter (the Agent Skills spec requires it).

Skills are methodological and engine-agnostic: write portable SQL, describe
engine features by what they do ("a zero-copy clone, if your engine has
one"), and never make one vendor's syntax the default. Where a subject is
genuinely engine-specific (performance tuning), keep a tool-agnostic spine in
`SKILL.md` and put engine detail in optional per-engine reference files.
Cross-skill references must be **soft
references** (see `CONTEXT.md` for the definition); every skill must remain
self-sufficient for its core decision. Only a skill that can't produce
correct output without the per-repo config (`to-tickets`, `triage`) carries an
explicit "run `/setup-ghost-skills`" line; the rest read the config when it
exists and carry on when it doesn't.

## Checks

`python3 scripts/check_governance.py` enforces the rules above — bucket
layout, README catalogue, `plugin.json`, frontmatter, links, and cross-skill
references — and runs in CI (`.github/workflows/governance.yml`) on every
push to `main` and every pull request, with its unit tests
(`python3 -m unittest discover -s scripts/tests`). Run both before pushing.
When you rename, merge, or remove a skill, add the old name to
`RETIRED_SKILLS` in the script so stale references to it fail the check.

Behaviour is tested separately, in an eval suite kept local (`evals/` is
git-ignored, like `docs/`: repo-building material isn't published). If it's
present, run a changed skill's case with `claude plugin eval` before pushing,
and see `evals/README.md` for re-running it when a new model ships.

## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo — one `CONTEXT.md` and `docs/adr/` at the root. See `docs/agents/domain.md`.
