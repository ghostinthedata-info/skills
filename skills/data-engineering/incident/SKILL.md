---
name: data-incident-management
description: >
  Use this skill whenever a data or reporting incident needs to be identified,
  classified, triaged, communicated, resolved, or reviewed. Triggers include:
  a pipeline failure, delayed/late data, a transformation defect, a replication
  or ingestion failure, duplicate or missing records, a dashboard showing wrong
  or stale figures, or any request to draft a stakeholder notification, a
  resolution email, a post-incident review (PIR/retro), or to classify an
  incident's severity. Also use for "we had an incident", "draft a data notice",
  "write a resolution email", "run a retro", or "how severe is this".
  Scoped to reporting & analytics data incidents (typically C4–C5), NOT
  production system outages.
---

# Data Incident Management

This skill turns a raw technical incident into structured, calm, stakeholder-ready
communication and a closed-loop learning process. It encodes the EDP incident
communications playbook plus current SRE / data-observability best practice
(Detect → Triage → Contain → Diagnose → Resolve → Communicate → Learn → Prevent).

## When to use this skill

Use it the moment a data issue is suspected or confirmed. The workflow below is
the spine; the supporting files do the heavy lifting:

| Need | Go to |
|---|---|
| Decide how serious this is | `CLASSIFICATION.md` |
| Work the incident step by step | the **Workflow** section below |
| Send a notification / update / resolution email | `EMAIL_TEMPLATES.md` |
| Run the retro and capture root cause + fixes | `POST_INCIDENT_REVIEW.md` |
| Stop it happening again | `PREVENTION.md` |

## Operating principles (read first)

1. **Reporting data being late is inconvenient, not critical.** Default to calm,
   factual language. Reserve escalation for when a *decision cannot be made*
   because data is unavailable.
2. **Communicate early, even without answers.** A short "we're aware and
   investigating" message prevents stakeholders from escalating or losing trust.
3. **Write for the audience.** Leadership and faculty don't need internals — they
   need to know what they can/can't rely on and when it's fixed.
4. **Be specific about impact.** "Today's dashboard figures are 6 hours out of
   date" beats "data may be delayed".
5. **Always close the loop.** Every initial notification must produce a
   resolution notification. No stakeholder left wondering.
6. **Blameless.** Root cause is about systems and process, not people. Never name
   individuals as the cause in any written artefact.
7. **Omit user-identifiable data** (individual emails, names) from stakeholder
   comms.
8. **Only produce what was asked.** Don't generate a Jira ticket, PIR, or exec
   summary unless it's requested or the severity requires it.

## Workflow

Work the incident in this order. For D3/D4 several steps collapse onto one person;
for D1/D2 they run in parallel with separate owners.

### 1. Detect & confirm
- Confirm the issue is real (not a transient blip or a user-side cache).
- Capture **detected-at timestamp**, the symptom, and who/what surfaced it
  (monitor, alert, stakeholder report).
- Identify the affected report/dashboard/feed and the source system
  (Workday, Salesforce, Canvas, StudentOne, Oracle, S3, Snowflake, DMS, dbt).

### 2. Classify (severity + impact + risk)
- Open `CLASSIFICATION.md` and assign **D1–D4**.
- Apply the **impact × urgency** lens, not just the symptom.
- Note **latent risk**: could this recur or affect more records than currently
  visible? (e.g. a field-length constraint that thousands of records could hit.)
- Classification sets the comms cadence and who gets notified.

### 3. Contain
- Stop the bleed before fixing the root cause: pause the failing job, hold a bad
  load, isolate the duplicate file, or freeze a downstream refresh so wrong data
  doesn't propagate.
- Decide whether a **workaround** exists (e.g. "yesterday's data is still valid")
  — this goes in the comms.

### 4. Communicate — initial
- Use **6.1 Initial Notification** from `EMAIL_TEMPLATES.md`.
- Send per the cadence in `CLASSIFICATION.md`
  (D1: T+30min, D2: T+1hr, D3: T+2hrs, D4: log only).
- **Always BCC** `edpteam@unimelb.edu.au`.
- For D1 (and D2 at the lead's discretion) flag executive awareness.

### 5. Diagnose (root cause)
- Use **5 Whys** to get past the symptom to the systemic cause.
- Distinguish *trigger* (what set it off) from *root cause* (why the system
  allowed it) and *blast radius* (everything affected, including silent/downstream).
- Capture a chronological timeline as you go — it becomes the PIR backbone.

### 6. Resolve & verify
- Apply the fix; **re-run / reprocess / backfill** as needed.
- Verify downstream data is correct and current. Confirm whether any **historical
  gap remains** or has been fully backfilled.
- Record **resolved-at timestamp**.

### 7. Communicate — resolution
- Use **6.3 Resolution Notification**. Close the loop explicitly — never leave a
  resolution estimate open-ended.
- State clearly whether data is fully backfilled or a gap remains.

### 8. Log
- Log in Jira (all severities), label `data-incident`. Include: affected
  system/pipeline/report, detected-at, resolved-at, severity, brief root cause,
  stakeholders-notified (Y/N), link to PIR if applicable.

### 9. Review & learn (D1/D2, or any recurring D3)
- Run the retro using `POST_INCIDENT_REVIEW.md` within 2 business days.
- Blameless. Produce concrete, owned, dated preventative actions.
- For D1/D2 send the **6.4 Executive Post-Incident Summary** to leadership.

### 10. Prevent
- Feed actions back into the system per `PREVENTION.md`: the fixed
  root cause becomes a permanent test/monitor in the layer where it occurred
  (the incident feedback loop). Add the failure mode to the runbook.

## Severity → action quick reference

| | D1 Critical | D2 High | D3 Medium | D4 Low |
|---|---|---|---|---|
| Initial notice | T+30 min | T+1 hr | T+2 hrs | Log only |
| Updates | Every 2 hrs | As needed | — | — |
| Roles separated? | Yes | Yes | Optional | Optional |
| Exec summary | Always (2 bd) | If requested | No | No |
| Business consumers | Init+Upd+Res | Init+Upd+Res | Init+Res | Only if impacted/asked |

## Output discipline

- Produce **plain-text email bodies** ready to paste unless a file is explicitly
  requested.
- Structure every stakeholder email: what happened → impact → root cause →
  current status → next steps.
- Keep it concise and factual. Match severity in tone — calm for D3/D4, crisp and
  prompt for D1/D2, never alarmist.
