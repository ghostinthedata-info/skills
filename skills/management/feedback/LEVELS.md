# Maturity Levels & SFIA Mapping

Use this to set the **expected** level in Step 0. Rate against the expectation, never in absolute terms.

## SFIA primer

SFIA (Skills Framework for the Information Age) defines 7 **levels of responsibility**, each described along five generic attributes: **Autonomy, Influence, Complexity, Knowledge, Business skills**. DE ladders don't map 1:1 to SFIA, but the responsibility bands below are a reliable anchor. When in doubt, judge by *autonomy* and *blast radius* (how much breaks, and how widely, if they get it wrong) rather than years served.

| SFIA L | Autonomy | Influence | Complexity |
|---|---|---|---|
| 2 | Works under routine direction; uses discretion on familiar problems. | Interacts with own team. | Defined, routine tasks. |
| 3 | Works under general direction; plans own work to deadlines. | Some external interaction. | Varied tasks; selects appropriate methods. |
| 4 | Works under general direction in a clear framework; substantial personal responsibility. | Influences team and stakeholders. | Broad range of complex activities. |
| 5 | Broad direction; full accountability for own technical work + others'. | Influences org; advises. | Wide variety, often unpredictable. |
| 6 | Defined authority for a significant area; high-level direction only. | Influences policy/strategy across org. | Highly complex, strategic. |
| 7 | Authority across a large area; sets strategy. | Industry/org-wide. | Leadership-level ambiguity. |

## The five DE levels

### Junior Data Engineer — SFIA ~2
- **Autonomy:** Needs well-scoped tasks and supervision; asks for help appropriately rather than thrashing.
- **Scope:** A single task or small ticket within an existing pipeline.
- **Expectation:** Learns the stack, writes correct code for defined problems, follows team conventions, getting reliably better each cycle.
- **Blast radius:** A bug is caught in review or dev; limited prod exposure.

### Mid Data Engineer — SFIA ~3
- **Autonomy:** Owns a feature end-to-end under broad direction; plans own work; unblocks self.
- **Scope:** A pipeline, a set of models, a component.
- **Expectation:** Reliable independent delivery, sound default choices, tests its own work, knows when to escalate.
- **Blast radius:** Owns a component that runs in prod; failures are recoverable and contained.

### Senior Data Engineer — SFIA ~4–5
- **Autonomy:** Takes ambiguous problems and makes them tractable; sets local technical direction.
- **Scope:** A system or domain; cross-component design.
- **Expectation:** Designs for failure/scale/cost, multiplies the team (review, mentoring, standards), owns hard problems, makes good tradeoffs under uncertainty.
- **Blast radius:** Decisions shape a system many people depend on.

### Staff Engineer — SFIA ~5–6  (breadth axis)
- **Autonomy:** Operates across team boundaries with minimal direction; identifies the problems worth solving.
- **Scope:** Multiple teams / a platform / a cross-cutting concern (e.g. data contracts org-wide).
- **Expectation:** Force-multiplier through influence not authority; drives technical strategy, builds consensus, raises the bar broadly, prevents whole classes of problems.
- **Blast radius:** Technical direction affects many teams.

### Principal Engineer — SFIA ~6–7  (altitude axis)
- **Autonomy:** Sets direction in genuine ambiguity; trusted with the org's hardest, highest-stakes bets.
- **Scope:** A function or the whole org's data technical strategy.
- **Expectation:** Owns the multi-year technical vision, aligns leadership, makes the calls others can't, develops other senior+ engineers.
- **Blast radius:** Strategic; shapes where the org invests for years.

## Staff vs Principal

Both sit above Senior. They are **not** a simple "Principal > Staff" ranking — they differ in axis:

- **Staff = breadth.** Leverage *across* teams. "We keep hitting this problem in five places; I'll fix the class of it."
- **Principal = altitude.** Depth and strategic ownership. "Here's the bet the whole data org should make for the next three years, and why."

Some orgs collapse these into one band; confirm the org's actual ladder before holding someone to one definition.

## Calibration cautions

- **Titles inflate.** Validate the level against real scope and autonomy, not the title alone.
- **Years ≠ level.** Someone can have ten years at the Mid bar. Judge current operating level.
- **Spiky profiles are normal.** Most engineers exceed on some skills and lag on others; that's signal for the growth plan, not a reason to average into a meaningless single number.
