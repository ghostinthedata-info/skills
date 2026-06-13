# 1. Skills are purely methodological — no vendor specifics in the core

Status: Accepted

## Context

Vendor and tool knowledge (warehouse features like Snowflake `QUALIFY` or
BigQuery partitioning syntax, package versions, product UIs) changes fast and
dates quickly. Methodology (grain, keys, SCDs, conformed dimensions,
Write-Audit-Publish, incident comms) is durable and portable across clouds
and engines. A softer alternative was considered: small per-skill "dialect
notes" tables mapping each principle to vendor syntax. It was rejected
because those tables are exactly the content that goes stale and bloats
every skill with maintenance burden.

## Decision

Skills in this pack encode durable methodology and design principles only.
Per-repo specialisation is injected at install time: `setup-ghost-skills`
records the consumer repo's warehouse platform & SQL dialect and
transform/orchestration tooling in `docs/agents/platform.md` and
`docs/agents/tooling.md`, and skills direct the agent to consult those files
for dialect specifics. Cloud- or vendor-specific skill content belongs in
**forks** of this repo (see CONTRIBUTING.md), not in the core buckets.

## Consequences

+ Skills stay evergreen as tools churn; one repo serves every stack.
+ Clean fork story: `ghost-skills-snowflake` etc. layer on top without
  touching the core.
- Skills won't emit copy-paste-perfect vendor SQL out of the box; they rely
  on the per-repo `platform.md` (and the agent's own knowledge of the
  dialect) to specialise.
