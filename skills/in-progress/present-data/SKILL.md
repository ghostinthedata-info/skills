---
name: present-data
description: Turn analysis into a decision — work in the explanatory (not exploratory) space, lock Who/What/How, lead with the Big Idea, choose the right visual, declutter, and direct attention so the audience acts. Use when presenting results, building a dashboard, writing an analytical summary, or whenever a chart needs to drive a decision rather than just show numbers.
---

# Present Data

Based on Cole Nussbaumer Knaflic's *Storytelling with Data*. The communication
of an analysis is usually the **only part the audience ever sees** — yet it's
the step analysts are least trained for. A chart's job is not to show data; it
is to move a specific person to a specific decision. Tools don't know your
story, so the work is yours. Lessons here are tool-agnostic.

This is the consumer-facing complement to `data-as-a-product` (which is about
owning a dataset as a product); reach for this skill when communicating a
*finding*, not shipping a table.

## Explanatory, not exploratory (start here)

Exploratory analysis is opening 100 oysters to find 2 pearls. **Never present
the oysters.** Showing every cut of the data "as evidence of the work" forces
the audience to redo your analysis. Communicate only the pearls — the specific
thing they need to know. If you catch yourself adding a chart because it was
hard to make, cut it.

## Lock Who / What / How (before opening any tool)

Answer these three, in order, and write them down:

* **Who** — name a *specific* audience and, ideally, the decision maker.
  "Internal and external stakeholders" is not an audience; you can't speak to
  everyone, so you end up speaking to no one. Also note your relationship and
  credibility with them.
* **What** — what do you need them to **know or do**? State an explicit ask
  for action (recommend, approve, change, invest…). If you can't articulate
  the action, reconsider whether to communicate at all. Take the confident,
  subject-matter-expert stance; "that's interesting" is a failure.
* **How** — *only now* turn to the data: what evidence makes the point? Data
  is supporting evidence for the story, not the story itself.

Also fix the **tone** (celebratory / urgent / cautionary) and the
**mechanism**, which sits on a continuum:

* **Live presentation** — you control pace; keep slides sparse, hold detail in
  your head. Don't use slides as a teleprompter.
* **Written / emailed document** — the reader controls pace, so it must carry
  more detail and pre-empt questions.
* A single artefact forced to do both becomes a **"slideument"** that serves
  neither — pick the primary vehicle and design for it.

Don't cherry-pick: hiding non-supporting data is misleading and a discerning
audience will find the hole. This Who/What/How discipline mirrors
`gather-requirements` (see it if installed) — same instinct, applied to the
delivery instead of the build.

## Boil it down: 3-minute story & Big Idea

* **3-minute story** — what you'd say if your 30-minute slot were cut to 3 (or
  if you met the stakeholder in an elevator). Frees you from your slides.
* **Big Idea** — one complete sentence that (1) states your unique point of
  view, (2) conveys what's at stake, and (3) is a full sentence. If you can't
  write it, you don't yet know your story.

**Lead with the Big Idea** so the audience can't miss the point or wonder why
they're in the room.

## Storyboard low-tech

Outline the narrative on a whiteboard or Post-its **before** any slideware.
Starting in presentation software breeds attachment to slides you should cut,
and a deck that says nothing at length. Post-its let you reorder the flow
freely; get stakeholder sign-off on the storyboard before building.

## Choose the right visual

Match the visual to the message, not to the tool's defaults:

* **Simple text / a big number** when there are only one or two numbers — a
  chart would bury the point.
* **Table** when the audience will look up specific values; sparingly in a live
  talk (tables pull people in to read).
* **Line / slopegraph** for trends and before-after over a continuous axis.
* **Bar** (horizontal for long/many category labels) for comparison across
  categories; **always baseline at zero**.
* **Heatmap** to saturate a table with relative magnitude.
* **Avoid** pie and donut charts (humans judge angles/area poorly) and **all
  3D** and secondary y-axes — they distort.

## Declutter — every element earns its place

Every pixel adds cognitive load. Maximise the **data-ink ratio**: remove chart
borders, gridlines, tick marks, redundant legends, and decoration. Lean on
**Gestalt principles** (proximity, similarity, enclosure, alignment, white
space) so structure comes from layout, not heavy lines. Clutter is not a data
property — it's a design failure you introduced.

## Direct attention with pre-attentive attributes

The eye processes **size, colour, and position** before conscious thought. Use
them sparingly and deliberately to build a visual hierarchy: grey out the
context, and use one accent colour (and/or bold/size) for the one thing that
matters. If everything is emphasised, nothing is. Colour is a strategic tool,
not decoration — and check it works for colour-blind viewers and in greyscale.
Use words too: a descriptive **title carrying the takeaway** ("Support volume
fell 30% after launch", not "Tickets by month"), plus direct labels and
annotations instead of a detached legend.

## Anti-patterns (call these out)

* Presenting exploratory dumps — every slice "to be thorough".
* No ask: ending on "any questions?" instead of a recommendation.
* A vague, everyone audience → a message that fits no one.
* Chart title that names axes instead of stating the point.
* Default-tool clutter, 3D, pie charts, rainbow colour.
* Building slides before storyboarding the narrative.

## Template

See [PRESENTATION-PLANNER.md](PRESENTATION-PLANNER.md) for a fill-in
Who/What/How + Big Idea worksheet and a pre-send checklist.
