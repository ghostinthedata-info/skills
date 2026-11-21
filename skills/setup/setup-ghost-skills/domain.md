# Domain docs

Where this repo keeps its shared vocabulary and its decisions, and how the
pack's skills use them.

## Layout

*Keep the layout that applies and delete the other.*

**Single context** — most repos:

```
/
├── CONTEXT.md        ← the glossary: each term, what it means here, words to avoid
└── docs/adr/         ← one file per hard-to-reverse decision, numbered in order
    ├── 0001-<slug>.md
    └── 0002-<slug>.md
```

**Several contexts** — a `CONTEXT-MAP.md` at the root lists each context and
where its own `CONTEXT.md` and `docs/adr/` live. Decisions that span contexts
stay in the root `docs/adr/`.

```
/
├── CONTEXT-MAP.md
├── docs/adr/                    ← decisions that span contexts
└── domains/
    ├── sales/
    │   ├── CONTEXT.md
    │   └── docs/adr/
    └── finance/
        ├── CONTEXT.md
        └── docs/adr/
```

## Before working in an area

Read the glossary for the area (via `CONTEXT-MAP.md` if there is one) and the
ADRs whose titles touch it. If the files don't exist yet, carry on: they're
created as terms and decisions get settled — `gather-requirements` writes
them — not up front.

## While working

* **Use the glossary's words** — in ticket titles, model and column names,
  test names, and specs. If a word the glossary says to avoid creeps in, swap
  it.
* **A term you need isn't there?** Either you're inventing vocabulary (use the
  existing word) or the glossary has a gap — note it for the next
  `gather-requirements` session.
* **Contradicting an ADR?** Say so plainly — "this goes against ADR-0004
  (event time, not load time), because …" — and let the user decide whether
  to reopen it. Never override one quietly.
