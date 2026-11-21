# Domain docs

This repo has a single context:

```
/
├── CONTEXT.md        ← the glossary: skill, bucket, pack, soft reference, …
└── docs/adr/         ← one file per hard-to-reverse decision, numbered in order
```

## Before working in an area

Read `CONTEXT.md` and the ADRs whose titles touch the area. If a file you'd
expect doesn't exist, carry on — glossary terms and ADRs are written when
they're settled, not up front.

## While working

* **Use the glossary's words** in commit messages, skill text, and issue
  titles; swap out any word it says to avoid.
* **A term you need isn't there?** Use an existing word if one fits; otherwise
  add the term to `CONTEXT.md` in the same change.
* **Contradicting an ADR?** Say so plainly — "this goes against ADR-0001,
  because …" — and let the maintainer decide whether to reopen it.
