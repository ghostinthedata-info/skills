---
name: incident-comms
description: The communications workflow for a data incident — who to notify and when, severity classification, update cadence, copy-paste templates, and the post-incident review. Use when data is wrong/late/missing and stakeholders are or will be affected, or when setting up an incident-comms process. This is about communication, not root-cause analysis.
disable-model-invocation: true
---

# Incident Comms

When data breaks, the failure that destroys trust isn't the bug — it's the
**silence**. The data teams with the highest stakeholder trust
over-communicate around incidents (Ghost in the Data, "Don't Go Dark"). The
fix is later and more expensive the further bad data travels (1x at entry,
10x in systems, 100x at the decision). This skill is the comms workflow:
classify, notify, update on a cadence, then review.

## 0. First use in this repo — tailor the matrix

Check for `docs/agents/incident-severity.md`. If it exists, use it as the
severity definition. If not, ask the user once: "Does your org have existing
severity definitions? If yes, point me at them and I'll record them. If no,
here's a sane default — confirm or adjust the triggers, cadences, and notify
lists for your team size." Then write the agreed matrix to
`docs/agents/incident-severity.md` and use it from then on.

## 1. Classify severity (objective — blast radius, not urgency)

Default matrix (cadences per PagerDuty Incident Response and the openstatus
Incident Severity Matrix):

| Sev | Trigger | First response | Update cadence | Notify |
|-----|---------|----------------|----------------|--------|
| **SEV0** Critical | ≥80% of consumers / data loss / regulated report wrong | 15 min | every 15 min | exec + on-call + data lead |
| **SEV1** High | ≥50% consumers / a Tier-1 table wrong | 30 min | every 30 min | affected domain leads + data lead |
| **SEV2** Medium | ≥10% / degraded freshness | 2 hours | every 2 hours | owning team + consumers |
| **SEV3** Low | <10% / cosmetic | 1 business day | daily | ticket only |

Err high during the incident; downgrade in review. Auto-escalate if a SEV2
is unresolved in 4h or spreads to new tables. Watch for severity inflation —
if 30%+ are SEV1, you've lost the signal.

## 2. Notify the right people on one channel

Name an **incident lead** (owns comms) and a **technical lead** (owns the
fix) — in a small team this can be the same person, but name both hats.
Pick ONE canonical source of truth (status doc/page) — everything points to
it; don't let chat and email disagree. Use UTC timestamps.

## 3. Update on cadence (the heartbeat rule)

Never go longer than the cadence without an update on an active SEV0/SEV1 —
even "still investigating, no new info, next update in 30 min." Silence
reads as "they've forgotten / it's worse than they're saying."

### Copy-paste templates

**Investigating:** "We're investigating an issue affecting [dataset/report]:
[what consumers see]. Impact: [scope]. The data team is on it. Next update
by [time UTC]."

**Identified:** "Root cause identified: [one line]. A fix is in progress.
Affected: [tables/reports + time window]. Do not rely on [X] until resolved.
Next update by [time UTC]."

**Resolved:** "Resolved. [Dataset/report] is correct as of [time UTC].
What happened: [1–2 lines]. Window affected: [range]. A post-incident review
will be shared within 48h."

## 4. Post-incident review (blameless, required for SEV0/SEV1)

Capture: timeline (detected → notified → identified → fixed → verified),
business impact (consumers, decisions, duration), root cause, and **action
items with an owner and due date**. Ask "what would have caught this
earlier?" — usually a data test or a freshness check (see `test-data` if
installed). File those as work, and record the decision as an ADR if it
changes the architecture.
