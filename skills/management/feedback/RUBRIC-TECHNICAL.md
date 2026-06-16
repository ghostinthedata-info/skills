# Rubric — Technical Craft

Rate each skill against the **Meet** bar for the engineer's *expected* level (from `levels.md`).
- **Underperform** = below their level's Meet bar.
- **Meet** = at it.
- **Exceed** = at/above the *next* level's Meet bar.

Behaviours are illustrative, not a checklist. Pick the description that best matches the evidence.

---

## 1. Data modelling
| Level | Underperform | **Meet** | Exceed |
|---|---|---|---|
| Junior | Copies structures without understanding grain/keys; frequent rework. | Implements a given model correctly; understands PK/FK, grain, basic normalisation. | Spots modelling smells and asks the right questions before coding. |
| Mid | Models work but ignore grain/SCD nuance; awkward joins downstream. | Chooses sound dimensional/normalised designs for a feature; handles SCD2, surrogate keys, late-arriving data. | Designs for evolvability; anticipates downstream consumers. |
| Senior | Designs that don't scale or trap future change; no consumer view. | Owns domain model design; balances normalisation, performance, and consumer ergonomics; sets local modelling conventions. | Defines reusable modelling patterns the team adopts. |
| Staff | Patterns stay local; inconsistency persists across teams. | Drives modelling standards/contracts across teams; resolves cross-domain conflicts. | Shapes org-wide semantic/contract strategy. |
| Principal | Avoids the hardest semantic ambiguity. | Sets the org's modelling/semantic-layer direction for multi-year horizons. | Influences industry practice; org is cited as exemplar. |

## 2. SQL & transformation (incl. dbt)
| Level | Underperform | **Meet** | Exceed |
|---|---|---|---|
| Junior | SQL is correct only for happy path; doesn't handle nulls/dupes. | Writes correct, readable SQL; understands joins, window functions, null/dup handling. | Writes clean, tested transforms with minimal guidance. |
| Mid | Transforms work but are hard to maintain; logic duplicated. | Builds modular, tested transformation layers (staging→marts); DRY via macros/refs. | Introduces patterns that cut duplication team-wide. |
| Senior | Lets complexity sprawl; no layering discipline. | Owns transformation architecture; enforces layering, testing, and lineage discipline. | Designs frameworks that make the right way the easy way. |
| Staff | — | Drives transformation standards and tooling across teams. | Org-wide transformation platform direction. |
| Principal | — | Sets strategic direction for the transformation/semantic stack. | — |

## 3. Pipeline & orchestration
| Level | Underperform | **Meet** | Exceed |
|---|---|---|---|
| Junior | Pipelines are brittle; no idempotency awareness. | Builds/maintains a defined pipeline; understands scheduling, dependencies, retries. | Builds idempotent, restartable pipelines unprompted. |
| Mid | Happy-path orchestration; failures need manual rescue. | Designs idempotent, observable pipelines with sensible retry/backfill; handles partial failure. | Designs for backfill, replay, and graceful degradation by default. |
| Senior | Orchestration choices don't account for scale/coupling. | Owns orchestration design across pipelines; manages coupling, SLAs, backfill strategy. | Introduces orchestration patterns/abstractions adopted broadly. |
| Staff | — | Drives orchestration platform/standards across teams. | Sets org orchestration strategy. |
| Principal | — | Owns the strategic platform direction for data movement. | — |

## 4. IaC & cloud
| Level | Underperform | **Meet** | Exceed |
|---|---|---|---|
| Junior | Manual changes in console; no IaC. | Makes changes via existing IaC (CDK/Terraform) following patterns; understands core cloud primitives. | Extends IaC safely with minimal review friction. |
| Mid | IaC works but copy-paste; weak on least-privilege. | Authors reusable IaC modules; applies least-privilege IAM, env separation. | Improves IaC ergonomics/safety for the team. |
| Senior | Infra design has security/cost/coupling gaps. | Owns infra architecture for a system; secure-by-default, multi-env, cost-aware. | Designs platform abstractions others build on. |
| Staff | — | Drives cloud/IaC standards and guardrails across teams. | Org cloud architecture strategy. |
| Principal | — | Sets multi-year cloud/platform strategy. | — |

## 5. Data quality & testing
| Level | Underperform | **Meet** | Exceed |
|---|---|---|---|
| Junior | Ships untested; "it ran" = done. | Writes basic tests (not-null, unique, refs); validates own output. | Tests edge cases without being asked. |
| Mid | Tests exist but shallow; no failure-mode thinking. | Designs meaningful test coverage incl. business rules; builds quality checks into pipelines. | Introduces quality patterns (contracts, anomaly checks) for the team. |
| Senior | Quality is reactive; no systemic view. | Owns data-quality strategy for a domain; observability, SLAs, contracts. | Builds quality frameworks adopted across the team. |
| Staff | — | Drives data-quality/observability standards across teams. | Org-wide trust/quality strategy. |
| Principal | — | Sets the org's data trust/governance direction. | — |

## 6. Performance & cost
| Level | Underperform | **Meet** | Exceed |
|---|---|---|---|
| Junior | Unaware of cost/performance impact of choices. | Understands basic warehouse cost/perf levers (pruning, clustering, warehouse sizing). | Proactively flags inefficient patterns. |
| Mid | Writes inefficient queries; reacts only when something is slow/expensive. | Diagnoses and fixes perf/cost issues; right-sizes compute; partitions/clusters sensibly. | Optimises proactively; quantifies savings. |
| Senior | No cost/perf ownership at system level. | Owns perf/cost characteristics of a system; sets budgets and optimisation strategy. | Builds tooling/practices that drive efficiency team-wide. |
| Staff | — | Drives FinOps/perf strategy across teams. | Org cost-efficiency strategy. |
| Principal | — | Sets strategic direction for platform efficiency at scale. | — |
