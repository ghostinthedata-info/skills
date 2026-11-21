# Rubric — Delivery & Operations

Rate against the **Meet** bar for the engineer's *expected* level. Underperform = below it; Meet = at it; Exceed = at/above the next level's Meet bar.

---

## 1. Reliability & on-call
| Level | Underperform | **Meet** | Exceed |
|---|---|---|---|
| Junior | Doesn't notice when own work breaks; needs prompting. | Monitors own pipelines; responds to alerts with guidance; escalates appropriately. | Anticipates failure modes before they fire. |
| Mid | Recurring failures in own components; firefights without fixing root cause. | Keeps owned systems healthy; handles routine on-call independently; fixes root causes. | Drives down alert noise/toil for the rotation. |
| Senior | Systemic reliability gaps go unaddressed. | Owns reliability of a system; SLOs, runbooks, proactive hardening. | Designs out whole failure classes; mentors others on reliability. |
| Staff | — | Drives reliability practices/standards across teams. | Org-wide reliability strategy. |
| Principal | — | Sets strategic reliability/resilience direction. | — |

## 2. Incident handling
| Level | Underperform | **Meet** | Exceed |
|---|---|---|---|
| Junior | Freezes or hides issues; no comms. | Follows the incident process; communicates status; helps under direction. | Stays calm, gathers facts, contributes to diagnosis. |
| Mid | Resolves slowly; weak comms; no follow-up. | Diagnoses and resolves incidents in owned area; clear comms; writes the postmortem. | Drives blameless postmortems to real preventive action. |
| Senior | Lets incidents recur; no systemic learning. | Leads incident response across a system; coordinates, communicates up, prevents recurrence. | Builds incident-response capability in others. |
| Staff | — | Improves incident practice across teams. | Org incident/resilience culture. |
| Principal | — | Owns strategic resilience posture. | — |

## 3. Estimation & scoping
| Level | Underperform | **Meet** | Exceed |
|---|---|---|---|
| Junior | Wildly off; doesn't flag slippage. | Estimates small tasks roughly right; flags when slipping early. | Breaks work down well; estimates improve fast. |
| Mid | Optimistic; misses hidden complexity; surprises stakeholders. | Scopes and estimates a feature credibly; surfaces risks and unknowns up front. | Decomposes ambiguous work into a sound plan. |
| Senior | Plans miss cross-system dependencies. | Scopes ambiguous/cross-component work; sequences for risk; sets realistic expectations. | Turns vague asks into clear, de-risked roadmaps. |
| Staff | — | Plans cross-team initiatives; manages dependencies at scale. | Org-level planning/sequencing. |
| Principal | — | Shapes multi-quarter strategic roadmaps. | — |

## 4. Ownership & follow-through
| Level | Underperform | **Meet** | Exceed |
|---|---|---|---|
| Junior | Drops tasks; needs chasing; "not my job". | Finishes what they pick up; flags blockers; closes the loop. | Takes initiative beyond the literal ticket. |
| Mid | Owns the code but not the outcome; leaves loose ends. | Owns a component's full lifecycle incl. the unglamorous parts (docs, cleanup, migration). | Owns outcomes, not just outputs; proactively improves owned area. |
| Senior | Ownership stops at own code boundary. | Owns a system end-to-end incl. its health, debt, and roadmap. | Takes ownership of orphaned/cross-cutting problems nobody else will. |
| Staff | — | Owns cross-team outcomes and the spaces between teams. | Owns the org's hardest unowned problems. |
| Principal | — | Owns function-level outcomes and bets. | — |

## 5. Documentation
| Level | Underperform | **Meet** | Exceed |
|---|---|---|---|
| Junior | Leaves no trace; knowledge in their head. | Documents own work enough for others to use it. | Writes docs others actually reach for. |
| Mid | Docs are stale or absent for owned components. | Maintains useful docs/runbooks for owned components. | Raises the doc bar by example. |
| Senior | System knowledge is tribal/bottlenecked on them. | Ensures systems are documented so the team isn't bottlenecked on them. | Creates durable references/decision records (ADRs). |
| Staff | — | Drives documentation/knowledge standards across teams. | Org knowledge-management practice. |
| Principal | — | Codifies strategic decisions and direction durably. | — |

## 6. Directing and checking AI agents
| Level | Underperform | **Meet** | Exceed |
|---|---|---|---|
| Junior | Pastes the ask into an agent and submits what comes back; can't say what the change does. | Can explain every change they submit without the agent — what it does, what it assumes; runs the tests and a basic reconciliation before asking for review. | Spots generated output that's plausible but wrong before review does. |
| Mid | Ships or approves generated work on a first read; tests the same agent wrote are the only evidence. | Gives the agent the grain, the keys, and the source's known traps; backs generated work with reconciliation evidence (counts, sums, distinct keys tie out); can explain any change they approved. | Fixes the pattern behind an agent's error — the prompt, the template, the checklist — not just the output. |
| Senior | Lets the review burden grow unchecked; no view on where agents mustn't run alone. | Sets the automation level per kind of work in their area (agent drafts, human owns every line where money, compliance, or history is involved); reviews for understanding, not just green tests; feeds corrections back into the team's skills and templates. | Builds the context — skills, pattern bank, pre-mortem — that makes agents right first time. |
| Staff | — | Sets standards across teams: automation levels, the evidence each kind of change needs, and keeping manual skill alive. | Org-wide approach to supervised automation. |
| Principal | — | Owns the strategic stance on AI-assisted delivery and its risks. | — |
