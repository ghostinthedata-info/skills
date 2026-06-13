# Governance

This is the publisher repo for the **ghost-skills** pack. Skills are
organized into bucket folders under `skills/`:

* `data-engineering/` — the published data-engineering pack (profiling,
  requirements, modeling, keys, SCDs, testing, performance, incidents,
  pipelines, data products, security classification)
* `setup/`            — one-time per-repo configuration (`setup-ghost-skills`)
* `productivity/`     — general-purpose authoring/comms skills
* `in-progress/`      — drafts not yet promoted; not published

Every skill in `data-engineering/`, `productivity/`, or `setup/` must have a
reference in the top-level `README.md` and an entry in
`.claude-plugin/plugin.json`. Skills in `in-progress/` must not appear in
either until promoted out of that folder.

Each skill entry in the top-level `README.md` must link the skill name to
its `SKILL.md`.

Skills are purely methodological — no vendor-specific SQL or product
features in the core buckets. Cross-skill references must be **soft
references** (see `CONTEXT.md` for the definition); every skill must remain
self-sufficient for its core decision. The setup-pointer convention is
recorded in `docs/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md`.

## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo — one `CONTEXT.md` and `docs/adr/` at the root. See `docs/agents/domain.md`.
