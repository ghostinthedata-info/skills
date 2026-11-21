---
name: to-tickets
description: Turn a solution design's stories — or any agreed plan for a pipeline, model, or report — into tickets on the project's issue tracker, each a day-sized slice with a done-when, its handover, what it needs to start, and blocking links, labelled for triage. Use when the user wants to break a design or plan into tickets, issues, stories, or tasks, create work items for a data build, or publish a plan to GitHub, GitLab, or local markdown.
---

# To Tickets

Turn an agreed plan into tickets someone could pick up tomorrow with no
conversation. The input is usually the stories in a solution design (from
`solution-design`, if installed); a plan in the conversation or a spec works
too.

The tracker and label vocabulary should be in `docs/agents/issue-tracker.md`
and `docs/agents/triage-labels.md` — run `/setup-ghost-skills` if they're
missing.

## 1. Read the plan

Read the design or plan, and `CONTEXT.md` if it exists, so ticket titles use
the project's words. If there's no plan yet — only an idea — stop and suggest
`solution-design` (or `gather-requirements` for the what and why) first;
tickets cut from a fuzzy plan just move the fuzziness into the tracker.

## 2. Cut the slices

Each ticket is one slice of work that ends with something checkable:

* **About one effort-day.** Split anything bigger. A design's stories are
  usually the right size already — one story, one ticket.
* **Ends at a handover.** It produces something the next ticket can use — a
  landed table, a typed staging model, a published mart, an alert that fires.
  Pure set-up with nothing to check belongs inside the ticket that needs it.
* **Novel work is one discovery ticket.** A pattern the team hasn't built
  before gets a time-boxed spike with an exit question ("can the API give a
  reliable watermark?"), not a guess at day-sized pieces. Its outcome
  re-plans what follows.
* **Real data first.** The ticket that gets real batches landing where
  production builds can see them comes before the transformation tickets that
  need them.

## 3. Order them and link the blockers

* Dependency order first: a ticket can't start until whatever it needs to
  start exists.
* Among independent tickets, the riskiest goes first — spikes and anything
  that could change the design.
* Record each blocker as a link to the blocking ticket, in the form
  `issue-tracker.md` describes.

## 4. Write each ticket

```md
Title: <verb> <thing>, in the glossary's words — "Land daily orders extract in raw"

**Why** — one or two sentences, and a link to the spec or design.

**Build**
- [ ] <subtask>
- [ ] <subtask>

**Done when** — testable: tests pass in CI, row counts reconcile to the source,
deployed from version control, and another engineer could pick up what it
produced with no conversation.

**Hands over** — what the next ticket gets (a table, its contract, known quirks).
**Needs to start** — what must exist first (access, a sample file, a named contact).
**Blocked by** — <ticket links, or none>
**Effort** — known / known with caveats (<the caveat>) / novel (time-boxed: <n> days)
```

Keep personal data out of tickets: refer to records by key, never by name or
email address.

## 5. Show the list, then publish

Show the user the ticket titles in order, with their blockers and effort
signals, and wait for an OK — re-cutting is cheap now and expensive once
people have picked tickets up. Then publish in dependency order, so each
blocker already has an ID to link to. Label every ticket with the "needs
evaluation" label from `triage-labels.md`, unless the user says they're
already triaged; then use "ready for an agent" or "ready for a person" per
ticket.

## Deliver

The published tickets — links or paths — in build order, with the blocking
links between them, and a one-line note of anything left out of the tickets
on purpose.
