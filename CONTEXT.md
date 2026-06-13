# Project context (ubiquitous language)

Shared glossary for agents and humans working in this repo. Keep entries
domain-level — no implementation detail.

## Terms

- **Publisher repo** — this repo. It authors and publishes skills; other
  people install them into their own projects. (As opposed to a *consumer
  repo*, which installs skills produced elsewhere.)
- **Consumer repo** — any project that installs skills from a publisher repo
  via the skills.sh CLI (`npx skills@latest add <owner>/<repo>`).
- **Skill** — a single `SKILL.md` (plus optional companion files) under
  `skills/<bucket>/<name>/`, with `name` + `description` frontmatter. The
  unit of installation.
- **Bucket** — a top-level grouping folder under `skills/` that organises
  skills by purpose. Published buckets appear in the README and plugin
  manifest; unpublished buckets (e.g. personal, deprecated) do not.
- **Setup skill** — the one skill a consumer must run once per repo. It
  interviews the user one question at a time and writes per-repo
  configuration that the other skills read. Here: `setup-ghost-skills`.
- **Ghost Skills** — the name of this skill pack (plugin name
  `ghost-skills`), published from the `ghostinthedata-info/skills` GitHub
  org/repo and branded after the *Ghost in the Data* blog
  (ghostinthedata.info).
- **refine-context** — this pack's interview skill that stress-tests a data
  plan against the consumer repo's glossary and decisions. Deliberately *not*
  named `grill-with-docs`, to avoid colliding with Matt Pocock's skill of
  that name.
- **Repo-level facts** — facts true of the whole consumer repo, captured once
  by the setup skill: warehouse platform & SQL dialect, transform/
  orchestration tooling, domain-doc layout.
- **Pipeline-level facts** — facts that vary per pipeline or source system,
  captured by `gather-requirements` per pipeline: freshness SLA, volume SLA,
  grain, sources, historization. Never asked at setup time.
- **Baseline (profile)** — the saved, aggregates-only output of profiling a
  table (counts, cardinalities, null rates, ranges — never sample rows, no
  observed value sets for PII columns). Saved only with the user's consent;
  later diffed for drift detection and volume/variance thresholds.
- **Soft reference** — a mention of another skill phrased as enrichment
  ("see `keys` if installed"), never as a dependency. Every skill must remain
  self-sufficient for its core decision, because consumers install subsets.
