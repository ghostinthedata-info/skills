# Ghost Skills

The publisher repo for the **ghost-skills** pack: methodology and practice skills for AI coding agents, tuned for data engineering. Skills are organized into bucket folders under `skills/`, catalogued in `README.md`, and registered in `.claude-plugin/plugin.json`.

## Language

**Skill**:
A single agent capability — a folder under `skills/<bucket>/<name>/` containing a `SKILL.md` plus any templates or reference files it needs. Self-sufficient for its core decision.
_Avoid_: command, plugin, behavior

**Bucket**:
A top-level category folder under `skills/` that groups skills by purpose: `data-engineering/`, `setup/`, `productivity/`, and `in-progress/`.
_Avoid_: category, group, pack folder

**Pack**:
The published, installable collection of skills as a whole (the "ghost-skills" pack). Distinct from a single bucket.
_Avoid_: bundle, collection

**Soft reference**:
A cross-skill mention written so the referenced skill is helpful but not required — the referencing skill still completes its core decision if the other skill is absent. The default style for all cross-skill references.
_Avoid_: hard reference, dependency link

**Hard dependency**:
A skill that cannot function correctly without per-repo config seeded by `/setup-ghost-skills` (e.g. it must publish to a specific issue tracker or apply a specific label). These carry an explicit setup pointer.
_Avoid_: required dependency

**Soft dependency**:
A skill that only uses per-repo config to sharpen its output and degrades gracefully without it. Refers to project docs in vague prose, with no explicit setup pointer.
_Avoid_: optional dependency

**Setup pointer**:
The explicit one-liner ("… run `/setup-ghost-skills` if not") included only in hard-dependency skills.
_Avoid_: setup hint, config note

## Relationships

- The **pack** is divided into **buckets**; each **bucket** holds many **skills**
- A **skill** references other **skills** via **soft references** by default
- A **hard dependency** skill carries a **setup pointer**; a **soft dependency** skill does not
- Skills in the `in-progress/` **bucket** are not part of the published **pack** until promoted out

## Flagged ambiguities

- "soft reference" (a writing style for cross-skill mentions) vs "soft dependency" (a skill's reliance on per-repo config) — related but distinct; do not conflate.
