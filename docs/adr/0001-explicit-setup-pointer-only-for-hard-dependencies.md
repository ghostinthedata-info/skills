# Explicit setup pointer only for hard dependencies

The pack's skills read per-repo facts that `/setup-ghost-skills` writes to
`docs/agents/`: the platform, the tooling, the issue tracker, the triage
labels, and the domain-doc layout. A few skills can't produce correct output
without those facts — they publish tickets to a particular tracker or apply a
particular label, and a guess puts duplicates in the wrong place. The rest
only use the facts to sharpen their output, and work without them.

We treat the two kinds differently:

- **Hard dependency** — `to-tickets` and `triage`. Each carries one explicit
  line: the tracker and labels "should be in `docs/agents/…` — run
  `/setup-ghost-skills` if they're missing." Without the config their output
  is wrong, not just less sharp.
- **Soft dependency** — `diagnose`, `tdd`, `gather-requirements`,
  `data-modelling`, `profile-data`, `test-data`, and the rest. They read
  `docs/agents/*.md`, `CONTEXT.md`, and the ADRs when those exist, and carry
  on when they don't. `gather-requirements` publishes its spec only if a
  tracker is configured, so it stays soft.

No setup pointer where it isn't load-bearing: it costs tokens in every
session, and it would make every skill depend on setup having run.
