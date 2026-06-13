# 2. Setup writes to CLAUDE.md or AGENTS.md, never both

Status: Accepted

## Context

Different agents read different root config files (Claude Code reads
`CLAUDE.md`; most other agents read `AGENTS.md`). When a setup skill scaffolds
consumer-repo config it must pick a file. Creating both, or guessing on the
user's behalf, causes drift and duplication — two files claiming to be the
source of truth for the same `## Agent skills` block.

## Decision

`setup-ghost-skills` follows the selection rule established by Matt Pocock's
`setup-matt-pocock-skills`:

1. If `CLAUDE.md` exists, edit it.
2. Else if `AGENTS.md` exists, edit it.
3. If neither exists, **ask the user which to create** — never pick for them.
4. Never create one file when the other already exists.
5. If an `## Agent skills` block already exists, update it in place rather
   than appending a duplicate; do not disturb the user's surrounding content.

## Consequences

+ One source of truth for agent config in every consumer repo; no drift.
+ Consistent with the convention consumers already know from Matt's pack.
- Teams running both Claude Code and other agents must symlink or duplicate
  intentionally; documented in the README.
