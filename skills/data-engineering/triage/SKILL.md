---
name: triage
description: Sort incoming data work on the issue tracker — new data requests, "this number looks wrong" reports, missing or late data, access requests, and questions — by checking what each ticket really is, reproducing data defects with a query before labelling them, routing incidents and access requests to the right process, and moving every ticket to one of five triage roles (needs evaluation, waiting on the reporter, ready for an agent, ready for a person, won't do), with a brief for whoever picks it up. Use when the user wants to triage tickets or issues, review incoming requests or bug reports, prepare tickets for an agent, or clear a triage backlog.
---

# Triage

Move every ticket to a role a person or an agent can act on. Don't leave
anything sitting in "needs evaluation".

The tracker and label vocabulary should be in `docs/agents/issue-tracker.md`
and `docs/agents/triage-labels.md` — run `/setup-ghost-skills` if they're
missing. Skills name the *role*; apply the label that file maps it to.

## The roles

| Role | Means | Moves on when |
|---|---|---|
| needs evaluation | New; nobody has looked yet | Triage decides one of the four below |
| waiting on the reporter | Can't move until someone answers a specific question | The answer arrives → triage it again |
| ready for an agent | Specified well enough that an agent can finish it with no further conversation | An agent picks it up |
| ready for a person | Needs judgement, access, or a conversation an agent can't have | A person picks it up |
| won't do | Decided against, with the reason on the ticket | — |

## For each ticket

### 1. What kind of ticket is it?

Data work arrives mislabelled. Decide what it actually is first:

* **An incident** — data people are relying on *now* is wrong, late, or
  missing. Don't sit on it in triage: hand it straight to the incident process
  (`data-incident-management`, if installed), apply the incident label it
  uses, and link the two.
* **A data defect** — a number is wrong, but nothing urgent depends on it.
  Verify it (step 2) before it goes anywhere.
* **A new request or enhancement** — a new dataset, report, column, or
  source. Small and clear? Treat it like any other ticket. Anything with a new
  grain, a new source, or a disputed definition needs a requirements spec
  first (`gather-requirements`, if installed).
* **An access request** — "can I see X". It's a decision about who may see
  what, not engineering work: route it to the access process, with the
  column's classification if one exists (`data-security-classification`, if
  installed).
* **A question** — "what does active customer mean?" Answer it from
  `CONTEXT.md` and close it. If the glossary has no answer, that's a gap to
  fill, not a ticket to build.

### 2. Verify data defects before labelling them

"The number is wrong" is a claim until a query shows it. You need:

* **The asset** — which report, dashboard, table, or column.
* **The slice** — the period, the filters, the grain being looked at.
* **Expected vs actual** — with numbers, and how the reporter knows the
  expected one (another system? last month? a definition?).
* **An example** — a record key or two (keys only, never names or emails).

Then reproduce it: run the query that returns the wrong number from the
published table, and save that query on the ticket. Check the definition in
`CONTEXT.md` too — many "wrong" numbers are a different definition,
correctly computed. Can't reproduce it? Check the reporter's side (filters,
a cached or exported copy, the time zone they're viewing in) before deciding.

### 3. Assign the role

* **waiting on the reporter** — the asset, the slice, or expected-vs-actual is
  missing, or it won't reproduce. Post the specific questions, not "more
  info please".
* **ready for an agent** — reproducible (or, for a request, clear), scoped to
  named models, with testable acceptance criteria, and needing no production
  access, no business decision, and no personal data. Write the brief (step 4).
* **ready for a person** — needs a business decision (changing a definition is
  one), production access, a conversation with a stakeholder or a source
  owner, or it touches restricted data.
* **won't do** — out of scope, a duplicate, superseded, working as defined
  (link the definition), or costs more than it's worth. Write the reason on
  the ticket and close it.

Apply the label using `issue-tracker.md`, and remove the "needs evaluation"
label.

### 4. Write the brief for "ready for an agent"

Add a comment that makes the ticket self-sufficient:

* **What to change** — the models or files, and the behaviour wanted.
* **The reproduction** — the saved query and the number it returns now.
* **The expected result** — the number or rows it should return, and where
  that comes from (the definition, the source of truth).
* **The first test** — the failing test to write before the fix (`tdd`, if
  installed).
* **Done when** — acceptance criteria someone else can check.

## Several tickets at once

Triage one at a time, in the order given (incidents first if you spot any).
After each, say the role and the reason in one line. Finish with a tally —
ready for an agent, ready for a person, waiting on the reporter, won't do,
routed elsewhere — and the tickets that need a person's attention first.
