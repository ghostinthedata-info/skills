# Contributing

These skills are deliberately **tool-agnostic** so anyone can fork them for a
specific cloud or stack. Two great ways to contribute:

## 1. Improve a core (methodology) skill

Keep the voice concise, opinionated, and principle/checklist-driven. A skill
is methodology, not vendor docs — if it would go stale when a product ships a
new feature, it belongs in a fork, not here (see
`docs/adr/0001-tool-agnostic-skills.md`). Every published skill needs:

- a folder `skills/<bucket>/<name>/SKILL.md`
- `name` + `description` (with "Use when…" trigger guidance) frontmatter
- a linked entry in `README.md` **and** in `.claude-plugin/plugin.json`

### Writing rules

- **Soft references only.** Consumers install subsets of the pack, so a skill
  may mention another ("see `keys` if installed") but must never depend on
  it. Every skill must remain self-sufficient for its core decision — state
  the rule inline, reference the other skill as enrichment.
- **One question at a time** for interview-style skills, with a recommended
  answer for each question. Interview-style and side-effecting skills get
  `disable-model-invocation: true`.
- Prefer checklists and decision rules over prose.
- Attribute external paradigms (Ghost in the Data, Kimball Group, Data
  Vault 2.0, data mesh) where used.
- Repo-level facts belong in the setup skill; pipeline-level facts (SLAs,
  grain, sources) belong in `gather-requirements`. Don't ask at setup time
  for things that vary per pipeline.

## 2. Fork for your cloud

Want `ghost-skills-gcp`, `ghost-skills-azure`, `ghost-skills-databricks`,
`ghost-skills-snowflake`? **Please do.** Fork this repo, keep the methodology
skills, and add a cloud bucket (e.g. `skills/gcp/`) with vendor-specific
companions (BigQuery clustering, Dataform, Synapse, Unity Catalog, etc.).
Open an issue linking your fork and we'll list it in the README.

## DCO

By contributing you agree your contribution is MIT-licensed.
