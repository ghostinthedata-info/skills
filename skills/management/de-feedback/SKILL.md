---
name: de-feedback
description: Structured, honest, empathetic feedback for data engineers at any level (junior, mid, senior, staff/principal). Identifies the engineer's expected maturity level from their position, then scores observed performance against SFIA-anchored behaviours across technical, delivery/ops, collaboration, and leadership themes — producing an underperform/meet/exceed rating per skill plus a written narrative, and maintaining a running per-engineer feedback log that grows over time for growth conversations. Use whenever someone wants to evaluate, review, assess, appraise, coach, or give feedback to a data engineer, gauge what level they operate at, or set growth targets. Trigger when the user types /de-feedback or /feedback, or says "give feedback to my engineer," "assess this person," "is X performing at senior level," "what level is X," "write a review for," "log feedback for X," or pastes evidence about someone's work to be judged. Pulls in reference rubrics rather than improvising scores.
---

# Data Engineer Feedback

A skill for giving **honest, specific, and kind** feedback to data engineers. It separates two judgements that people routinely collapse:

1. **What level is this person *expected* to operate at?** (set by their position)
2. **What level are they *actually* operating at, per skill?** (set by evidence)

Feedback is the gap between those two, communicated well. The skill anchors expectations to SFIA (Skills Framework for the Information Age) responsibility levels and common DE industry ladders, scores observed behaviour as **Underperform / Meet / Exceed** against the *expected* level, and frames delivery using Brené Brown's work on feedback (clear is kind; empathy over sympathy; the rumble; "I'm not here to be right, I'm here to get it right").

## When NOT to use this

- Pure technical review of an artifact (a PR, a dbt model, a pipeline) with no person-evaluation intent → just review the artifact.
- Generic career advice unrelated to a specific person's performance.

## Pick the mode

The same rubrics serve four conversations. Ask which one this is if it isn't obvious:

- **Review** (the default) — the full workflow below: expected level, scoring matrix, narrative, growth plan, running log.
- **Promotion case** — the same workflow, but the bar is the *next* level, and at the next level's *scope*. Exceed here means already meeting the next level's Meet bar across the breadth that level owns (a senior making a staff case shows cross-team outcomes, not their own project done faster or better). Evidence at the current scope, however strong, is a Meet.
- **Interview / hiring assessment** — rate only the skills the interview actually probed; everything else is *not assessed* (not "insufficient evidence"). Evidence must be first-person and specific: what *they* did, with the numbers and the outcome ("I added row-level assertions on the CDC stream; duplicates fell from 12% to 0.3%"), not "we did" or a textbook definition. Output a hire / no-hire at a stated level, the evidence for each probed skill, and what the next interviewer should probe. No narrative for the candidate, no growth plan, no running log.
- **1:1 coaching** — no rating matrix. First decide what the moment needs from you: coaching, teaching, or counsel. Understand before advising — ask what's going on and what they've tried. Use the rubrics only as vocabulary for the behaviour you're aiming at, agree one next step, and add it to the running log (Step 4b) if there is one.

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
- **Delivery & operations** — `RUBRIC-DELIVERY.md` (reliability/on-call, incident handling, estimation/scoping, ownership, documentation, directing and checking AI agents).
- **Collaboration & communication** — `RUBRIC-COLLABORATION.md` (written/verbal clarity, stakeholder management, code review, knowledge sharing).
- **Leadership & influence** — `RUBRIC-LEADERSHIP.md` (mentoring, technical direction, decision-making, driving alignment, raising the bar).

Read only the rubric files for themes in scope. Each file lists, **per level**, what Underperform / Meet / Exceed looks like for every skill — concrete behaviours, not adjectives.

### Step 2 — Gather evidence (ask only where it's thin)

The point is an *honest* evaluation, which requires real evidence, not vibes. For each skill in scope, you need at least one concrete example before you rate it.

- If the initiator already pasted evidence (PRs, incident write-ups, project descriptions, peer comments, examples of work), mine it first and map each piece to the relevant skill.
- Only ask clarifying questions for skills where evidence is **absent or ambiguous**. Don't re-ask what you already know.
- Prefer specifics: "Tell me about a time they…", "What did they do when the pipeline broke at 2am?", "Show me a PR you thought was strong / weak." For closed questions, use your structured question or multiple-choice tool if you have one; use prose for open ones.
- A skill with no evidence is rated **"Insufficient evidence"** — never guessed. Flag these so the initiator can go observe.
- **One example to rate a skill at all; a pattern of several for Exceed.** One great week is a good quarter, not a skill — check the reps.
- **Counts aren't evidence.** Tickets closed, PRs merged, and incidents resolved measure activity, and reward chopping work up. Ask explicitly for the invisible prevention work: the schema drift caught before it reached the mart, the review that stopped a fan-out, the runbook nobody else wrote, the junior who's now autonomous on a system they couldn't touch six months ago.
- **Rate outcomes, not ceremony.** Following every process while shipping fragile pipelines is a gap — say so, kindly and specifically. But an outcome achieved once may be luck; look for the track record.
- **Read the self-evaluation**, if there is one, before you rate. Where it and the evidence disagree, the gap between knowing what to do and doing it is the finding.

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
- A short **growth plan** (2–4 focused items, not a laundry list). Each aim gets an **"in return" clause** — not "I want to lead streaming ingestion" but "by June I'll be the person the team hands streaming ingestion to; in return I'll have built late-arrival handling on both event pipelines, documented the watermark strategy, and carried the on-call the first three times it breaks." A wish without an "in return" gives neither of you anything to hold.

Save the finished artifact as a markdown file in the working/output directory and present it. If the user explicitly wants a Word doc to share formally, use the `docx` skill to convert.

### Step 4b — Update the running per-engineer log

Separate from the point-in-time report above, keep a **living log per engineer** — one file that grows over time, named `{EngineerName}-feedback.txt`. It's what you pull from in targeted growth conversations: the thread of what changed, and the specific examples behind each shift.

- **Check first.** If the initiator already has a log for this person (they may upload it, or it may be in the working directory), read it: carry the header forward, update `Last updated`, and **add a new dated entry at the top** (newest first). Never overwrite past entries.
- **If none exists,** copy `RUNNING-LOG-TEMPLATE.md` to `{EngineerName}-feedback.txt`, fill the header, and write the first entry.
- **Keep entries lean.** Log only what *changed* since the last entry (rating shifts, or "held"), the concrete *example* behind each, movement on open growth threads, and the agreed next step. Don't re-paste the full matrix — that's what the report is for.
- **Keep it private.** It's personal performance data: store it where the initiator keeps people records, never in a shared repo, a ticket, or a team channel.
- Write it as plain-text-friendly markdown and present it alongside the report. The two are complementary: the report is the formal snapshot, the log is the ongoing record.

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

A completed evaluation always includes: the expected level (with reasoning), the filled scoring matrix with evidence per skill, any "insufficient evidence" flags, a delivery-ready narrative, a tight growth plan, and an updated running log (`{EngineerName}-feedback.txt`) with a new dated entry at the top. Never output bare scores without evidence, and never rate a skill you have no evidence for.
