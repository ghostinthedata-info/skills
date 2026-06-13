# Governance

This is the publisher repo for the **ghost-skills** pack. Skills are
organized into bucket folders under `skills/`:

* `discovery/`  — profile, scope, and align before building
* `modeling/`   — how to shape tables (dimensional, vault, keys, SCDs)
* `quality/`    — testing and performance methodology
* `operations/` — running pipelines, incidents, and data products
* `setup/`      — one-time per-repo configuration
* `personal/`   — tied to a specific team's setup, not promoted
* `deprecated/` — no longer used

Every skill in `discovery/`, `modeling/`, `quality/`, `operations/`, or
`setup/` must have a reference in the top-level `README.md` and an entry in
`.claude-plugin/plugin.json`. Skills in `personal/` and `deprecated/` must
not appear in either.

Each skill entry in the top-level `README.md` must link the skill name to
its `SKILL.md`.

Skills are purely methodological — no vendor-specific SQL or product
features in the core buckets (see `docs/adr/0001-tool-agnostic-skills.md`).
Cross-skill references must be soft references; every skill must remain
self-sufficient for its core decision (see `CONTRIBUTING.md`).

## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo — one `CONTEXT.md` and `docs/adr/` at the root. See `docs/agents/domain.md`.
