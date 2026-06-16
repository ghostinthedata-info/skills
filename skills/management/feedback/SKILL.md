---
name: de-feedback
description: Structured, honest, empathetic feedback for data engineers at any level (junior, mid, senior, principal/staff). Identifies the engineer's expected maturity level from their position, then scores observed performance against SFIA-anchored, industry-benchmarked behaviours across technical, delivery/ops, collaboration, and leadership themes — producing an underperform/meet/exceed rating per skill plus a written narrative. Use this whenever someone wants to evaluate, review, assess, coach, or give feedback to a data engineer (performance reviews, 1:1 coaching, interview/hiring assessment, calibration, promo cases, growth plans). Trigger even when the user just says "help me give feedback to my engineer," "assess this person," "is X performing at senior level," "write a review for," or pastes evidence about someone's work and wants it judged. Pulls in reference rubrics rather than improvising scores.
---

# Data Engineer Feedback

A skill for giving **honest, specific, and kind** feedback to data engineers. It separates two judgements that people routinely collapse:

1. **What level is this person *expected* to operate at?** (set by their position)
2. **What level are they *actually* operating at, per skill?** (set by evidence)

Feedback is the gap between those two, communicated well. The skill anchors expectations to SFIA (Skills Framework for the Information Age) responsibility levels and common DE industry ladders, scores observed behaviour as **Underperform / Meet / Exceed** against the *expected* level, and frames delivery using Brené Brown's work on feedback (clear is kind; empathy over sympathy; the rumble; "I'm not here to be right, I'm here to get it right").

## When NOT to use this

- Pure technical review of an artifact (a PR, a dbt model, a pipeline) with no person-evaluation intent → just review the artifact.
- Generic career advice unrelated to a specific person's performance.

## The workflow

Run these steps in order. Do not skip step 0 — a feedback artifact with the wrong expected level is worse than useless.

### Step 0 — Establish the expected maturity level

Determine the engineer's level. If the initiator states it ("she's a senior"), use it but sanity-check against the title's real scope (titles inflate). If unstated, ask, or infer from scope cues (autonomy, blast radius, who they influence). The five levels and their SFIA mapping live in `LEVELS.md` — **read that file now** before rating anything. Summary:

| Level | SFIA band | One-line expectation |
|---|---|---|
| Junior | 2 | Executes well-defined tasks with supervision; learning the stack. |
| Mid | 3 | Owns features end-to-end under broad direction; reliable independent delivery. |
| Senior | 4–5 | Owns systems/ambiguous problems; sets local technical direction; multiplies others. |
| Staff | 5–6 | Drives cross-team technical strategy; force-multiplier across the org via influence, not authority. |
| Principal | 6–7 | Sets org/function-wide technical direction; owns the hardest, most ambiguous bets. |

Staff and Principal are both "above senior" but differ in axis: Staff = breadth of technical leverage across teams; Principal = depth/altitude of strategic ownership. Confirm which ladder the org uses if it matters.

### Step 1 — Pick the themes in scope

Default to all four. Each has its own rubric file in this directory:

- **Technical craft** — `RUBRIC-TECHNICAL.md` (data modelling, SQL/transform, pipeline/orchestration, IaC/cloud, data quality/testing, performance/cost).
- **Delivery & operations** — `RUBRIC-DELIVERY.md` (reliability/on-call, incident handling, estimation/scoping, ownership, documentation).
- **Collaboration & communication** — `RUBRIC-COLLABORATION.md` (written/verbal clarity, stakeholder management, code review, knowledge sharing).
- **Leadership & influence** — `RUBRIC-LEADERSHIP.md` (mentoring, technical direction, decision-making, driving alignment, raising the bar).

Read only the rubric files for themes in scope. Each file lists, **per level**, what Underperform / Meet / Exceed looks like for every skill — concrete behaviours, not adjectives.

### Step 2 — Gather evidence (ask only where it's thin)

The point is an *honest* evaluation, which requires real evidence, not vibes. For each skill in scope, you need at least one concrete example before you rate it.

- If the initiator already pasted evidence (PRs, incident write-ups, project descriptions, peer comments, examples of work), mine it first and map each piece to the relevant skill.
- Only ask clarifying questions for skills where evidence is **absent or ambiguous**. Don't re-ask what you already know.
- Prefer specifics: "Tell me about a time they…", "What did they do when the pipeline broke at 2am?", "Show me a PR you thought was strong / weak." Use the `ask_user_input_v0` tool for closed questions; use prose for open ones.
- A skill with no evidence is rated **"Insufficient evidence"** — never guessed. Flag these so the initiator can go observe.

Guard against bias: anchor each rating to a behaviour in the rubric, not to overall impression (halo/horns). Recency, likeability, and "reminds me of myself" are not data.

### Step 3 — Score against the *expected* level

For each skill, compare observed behaviour to the **Meet** bar **for the engineer's expected level** (from step 0):

- **Underperform** — below the Meet bar for their level.
- **Meet** — at the Meet bar.
- **Exceed** — at or above the Meet bar for the *next* level up.

This is the crucial mechanic: a senior doing solid mid-level work is *Underperforming*; a mid doing senior-level work is *Exceeding*. Always rate against expectation, never in absolute terms. Record the specific evidence next to each rating.

### Step 4 — Produce the artifact

Fill out `FEEDBACK-TEMPLATE.md` (copy it; don't edit the reference in place). It contains:

- A header (name, role, expected level, period, evidence basis).
- The **scoring matrix** — one row per skill: expected level · rating · evidence · the specific next-step behaviour.
- A **narrative** section structured for delivery (see step 5).
- A short **growth plan** (2–4 focused items, not a laundry list).

Save the finished artifact as a markdown file in the working/output directory and present it. If the user explicitly wants a Word doc to share formally, use the `docx` skill to convert.

### Step 5 — Frame the delivery (Brené Brown)

Honesty without empathy is cruelty; empathy without honesty is a disservice. Hold both. Apply these to the narrative and to how you advise the initiator to deliver it:

- **Clear is kind. Unclear is unkind.** Vague feedback ("be more senior") protects the giver, not the receiver. Name the specific behaviour and the specific gap.
- **Separate the person from the behaviour.** Rate what they *did*, not who they *are*. "The design skipped a failure-mode review," not "you're careless."
- **Empathy, not sympathy.** Connect with the difficulty ("ambiguous scoping is genuinely hard") without lowering the bar.
- **The rumble.** Frame growth areas as a shared problem to solve, with the receiver's input, not a verdict handed down. Leave room: "Here's what I'm seeing — does that match your experience?"
- **Ground it in care + candour.** Lead with the genuine strengths (specific, not flattery), be straight about gaps, and make the standard you're holding explicit so it doesn't feel personal.
- **Own your part.** Where the environment, unclear expectations, or lack of support contributed, say so.

The matrix gives the *what*; this gives the *how*. A good artifact reads as something you'd be comfortable having the engineer read over your shoulder.

## Output expectations

A completed evaluation always includes: the expected level (with reasoning), the filled scoring matrix with evidence per skill, any "insufficient evidence" flags, a delivery-ready narrative, and a tight growth plan. Never output bare scores without evidence, and never rate a skill you have no evidence for.
