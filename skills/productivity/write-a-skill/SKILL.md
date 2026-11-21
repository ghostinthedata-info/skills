---
name: write-a-skill
description: Write a new skill for the ghost-skills pack, or rework an existing one, so it passes the pack's governance — the right bucket and folder name, a description that triggers reliably, a short SKILL.md with reference files for depth, soft references to other skills, and the README and plugin.json entries the checker requires. Use when the user wants to create, write, add, promote, split, or restructure a skill in this repo.
---

# Write a Skill

A skill is a folder an agent loads when its description matches the task in
front of it. This repo's rules live in `CLAUDE.md` and are enforced by
`scripts/check_governance.py`, so a skill is finished when the checker passes
— not before.

## 1. Pin down the decision it owns

Agree these with the user before writing anything:

* **The core decision or job**, in one sentence ("decide which SCD type each
  attribute needs"). Two decisions means two skills.
* **The triggers** — the situations and phrases that should load it — and the
  near misses that shouldn't, because another skill owns them.
* **What it produces** — a spec, a DDL skeleton, a test plan, an email.
* **Its neighbours.** Read the descriptions of the skills it borders and draw
  the line between them now; two skills with overlapping triggers drift apart
  and confuse the agent choosing between them.

## 2. Place it

* `skills/<bucket>/<name>/SKILL.md`. The buckets are `data-engineering/` (the
  pack's core), `management/`, `productivity/`, `setup/`, and `in-progress/`
  for drafts.
* Start new skills in `in-progress/` unless the user says otherwise. Drafts
  stay out of `README.md` and `plugin.json` until they're promoted.
* The folder name equals the `name` in the frontmatter: lowercase letters,
  digits and single hyphens, at most 64 characters, unique in the repo, and
  not a name listed in `RETIRED_SKILLS`.

## 3. Write the description

The description is all an agent sees when deciding whether to load the skill,
so it does the triggering; the body never gets the chance.

* Open with what the skill does, in concrete nouns — its inputs and outputs.
* Follow with "Use when…": the situations, and the words people actually
  type, including indirect ones ("the numbers don't tie out").
* Name the hand-off if a neighbouring skill owns the next step.
* Third person; at most 1024 characters.
* Add `disable-model-invocation: true` only for skills that should run when
  someone asks for them by name (setup, long interviews).

## 4. Write SKILL.md

* **Method first.** The steps the agent follows, in order, with the decisions
  to make and the questions to ask. Background only where a step needs it.
* **Short, with depth on the side.** Keep what every run needs in `SKILL.md`;
  move templates, catalogues and per-engine notes into reference files, and
  link each one from `SKILL.md` or another reference file — the checker fails
  a file nothing points to.
* **Engine-agnostic.** Portable SQL, engine features described by what they do,
  and engine-specific detail only in optional per-engine reference files.
* **Self-sufficient.** The skill completes its core decision on its own.
  Mention other skills as soft references — "(see `test-data` if installed)".
* **Per-repo config** (platform, tooling, tracker, labels) comes from
  `docs/agents/*.md`. If the skill can't produce correct output without it,
  add one line pointing to `setup-ghost-skills`
  (`docs/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md`);
  otherwise read the files when they exist and carry on when they don't.
* **Scripts for repeatable mechanics.** Validation or formatting that would be
  re-derived on every run belongs in a script in the skill folder.

## 5. Register it and run the checks

For a published skill:

1. Add `- **[<name>](skills/<bucket>/<name>/SKILL.md)** — <one line>` under
   the right heading in `README.md`.
2. Add `./skills/<bucket>/<name>` to the `skills` array in
   `.claude-plugin/plugin.json`.
3. If you renamed or removed a skill, add the old name to `RETIRED_SKILLS` in
   `scripts/check_governance.py`, with where its content went.
4. Run `python3 scripts/check_governance.py` and
   `python3 -m unittest discover -s scripts/tests`. Both must pass.

## 6. Read it back cold

Read the description as an agent that has never seen the skill: would it load
for every trigger you listed, and stay quiet for the near misses? Then walk
one real task through the steps, and fix whatever you had to guess.
