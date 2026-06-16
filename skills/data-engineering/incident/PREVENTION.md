# Preventing Future Incidents

Resolving an incident isn't the end. Per the incident feedback loop: **when an
incident is raised in production, the fix is not the end — the root cause becomes a
permanent test in the layer where it occurred.** Most incidents loop back to
Modelling or Business Rules; an ingestion-layer incident hardens the data contract.
The library of tests grows over time, so the same failure can't recur silently.

## The feedback loop

```
Detect → Triage → Contain → Root Cause → Fix → Regression Test → Close → Add to library
                                                      │
                                                      ▼
                        new permanent test/monitor in the layer the cause lived
```

Every closed incident should leave behind a durable artefact that would catch it
next time. If it wouldn't, the loop isn't closed.

## Turn each root cause into a guardrail

Map the root cause to the right preventative control:

| Root cause type | Preventative control |
|---|---|
| Transformation / SQL edge case (e.g. XML spilling across files) | Add a unit/regression test for that pattern; **roll the fix across all sibling models**, not just the one that failed |
| Field-length / constraint breach | Proactive scan for other records that could trip the same limit; add a validation check upstream |
| Replication / ingestion failure (DMS) | Freshness + row-count monitor; duplicate-file handling in the restart runbook |
| Duplicate / missing records after restart | Idempotency check; document the restart edge case in the runbook |
| Source platform slowdown (e.g. S3) | Timeout/latency alert; SLA on batch windows |
| API timeout (e.g. Canvas) | Retry-with-backoff; alert on repeated timeouts |

## Three classes of preventative action

For each PIR action, decide which lever it pulls:

1. **Detect earlier** — monitors and alerts so EDP finds it before stakeholders
   do. Track toward lower Mean Time To Detect. Cover freshness, volume/row-count
   anomalies, schema drift, and validation failures.
2. **Prevent entirely** — tests, validation, contracts, and constraints that stop
   the bad state from being produced (regression test, schema check, idempotency).
3. **Respond faster** — runbook entries, clear ownership, pre-written reprocessing
   steps so the next occurrence is routine, not a scramble.

## Proactive practices (between incidents)

- **Data observability:** continuous monitoring for freshness, volume, schema, and
  quality across critical feeds — early warning beats stakeholder reports.
- **Targeted remediation on constrained platforms:** where a source is being
  retired or has deliberate cost trade-offs, prefer table-level fixes over broad
  rewrites.
- **Backlog the latent risks:** replay capability, scheduled full catch-ups to
  auto-heal drift, and proactive scans for records that could trip known
  constraints — even when no incident is live.
- **Keep runbooks short and linked** to specific failure types; review after every
  relevant incident so they actually get used.
- **Service/feed ownership:** every critical feed has a documented owner, severity
  default, and linked runbook — nobody should ask "who owns this?" at 11pm.

## Metrics to watch

- **MTTD** (mean time to detect) — are we finding issues before stakeholders?
- **MTTR** (mean time to resolve) — is response getting faster?
- **Recurrence rate** — are closed incidents staying closed?
- **% incidents detected by monitor vs by stakeholder** — should trend toward
  monitors.

If an incident recurs, the loop failed somewhere — re-open the prevention action,
don't just re-fix the symptom.
