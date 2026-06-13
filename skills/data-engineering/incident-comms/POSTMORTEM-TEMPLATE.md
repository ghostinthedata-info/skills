# Incident Comms Templates

Fill-in templates for the comms workflow: the severity matrix written to
`docs/agents/incident-severity.md` on first use, the status-update messages,
and the blameless post-incident review.

---

## 1. Severity matrix (`docs/agents/incident-severity.md`)

Seed this on first use, then confirm/adjust triggers, cadences, and notify
lists for the team's size. Classify on **blast radius, not urgency**.

```markdown
# Incident severity matrix

| Sev  | Trigger (blast radius)                              | First response | Update cadence | Notify                              |
|------|-----------------------------------------------------|----------------|----------------|-------------------------------------|
| SEV0 | ≥80% of consumers / data loss / regulated report wrong | 15 min      | every 15 min   | exec + on-call + data lead          |
| SEV1 | ≥50% consumers / a Tier-1 table wrong               | 30 min         | every 30 min   | affected domain leads + data lead   |
| SEV2 | ≥10% / degraded freshness                           | 2 hours        | every 2 hours  | owning team + consumers             |
| SEV3 | <10% / cosmetic                                     | 1 business day | daily          | ticket only                         |

Rules:
- Err high during the incident; downgrade in review.
- Auto-escalate if a SEV2 is unresolved in 4h or spreads to new tables.
- Watch for severity inflation — if 30%+ are SEV1, the signal is lost.
- One incident lead (owns comms) + one technical lead (owns the fix); in a
  small team, same person, both hats named.
- One canonical source of truth (status doc/page). UTC timestamps everywhere.
```

---

## 2. Status-update messages (the heartbeat)

Never go past the cadence without an update on an active SEV0/SEV1 — even
"no new info." Silence reads as "they've forgotten / it's worse than they're
saying."

```
[INVESTIGATING]
We're investigating an issue affecting <dataset/report>: <what consumers see>.
Impact: <scope>. The data team is on it. Next update by <time UTC>.

[IDENTIFIED]
Root cause identified: <one line>. A fix is in progress.
Affected: <tables/reports + time window>. Do not rely on <X> until resolved.
Next update by <time UTC>.

[MONITORING]
Fix applied; we're monitoring <dataset/report>. No action needed from you yet.
Next update by <time UTC>.

[RESOLVED]
Resolved. <Dataset/report> is correct as of <time UTC>.
What happened: <1–2 lines>. Window affected: <range>.
A post-incident review will be shared within 48h.
```

---

## 2b. Email / broadcast versions (same content, fuller framing)

Chat is for the active heartbeat; email is for stakeholders not in the channel
(execs, downstream consumers, partner teams). Same facts, but lead with a
**consistent subject line** so a thread is easy to follow, and always restate
the dataset, impact, and next-update time (recipients won't have scrollback).

**Subject convention (keep it stable across the whole incident):**
`[DATA SEV1] <dataset/report> — <one-line status>`
Update only the trailing status word as it progresses: `Investigating` →
`Identified` → `Monitoring` → `Resolved`.

```
Subject: [DATA SEV1] Revenue dashboard — Investigating

Team,

We're investigating an issue affecting the <revenue dashboard>. Consumers may
see <understated revenue for EMEA since 09:00 UTC>.

- Impact: <which reports/decisions, rough scope>
- Status: investigating — no confirmed root cause yet
- What to do: <do not rely on EMEA revenue figures until resolved>
- Next update: by <time UTC> (or sooner if it changes)

The data team is actively on this. Reply here or message <incident lead> with
questions.

<incident lead name> — incident lead
```

```
Subject: [DATA SEV1] Revenue dashboard — Resolved

Team,

The <revenue dashboard> is correct as of <time UTC>. No further action needed.

- What happened: <1–2 plain-English lines>
- Window affected: <range, UTC>
- Who was affected: <reports/decisions>
- Follow-up: a blameless post-incident review will be shared within 48h

Thanks for your patience.

<incident lead name> — incident lead
```

Rules for the email channel:
- One thread per incident; never start a new thread for an update.
- Send a `Resolved` email even if the last chat update already said so — the
  email audience may not have seen it.
- Don't blame a person or a vendor in a broadcast email; describe the system.

---

## 3. Post-incident review (blameless — required for SEV0/SEV1)


```markdown
# Post-incident review: <short title>

- **Date of incident:** YYYY-MM-DD
- **Severity:** SEV_
- **Incident lead:** <name>   **Technical lead:** <name>
- **Status:** draft | reviewed | actions-tracked

## Summary
<2–3 sentences a non-engineer can understand: what broke, who it affected,
how long, and that it's now resolved.>

## Impact
- Consumers affected: <who / how many>
- Decisions or reports affected: <which>
- Duration: detected <t> → resolved <t> (UTC)
- Data window affected: <range>

## Timeline (UTC)
| Time  | Event                                          |
|-------|------------------------------------------------|
| 09:14 | First bad rows landed                          |
| 11:02 | Freshness check fired / consumer reported      |
| 11:10 | Incident declared SEV1, leads named            |
| 11:45 | Root cause identified                          |
| 12:30 | Fix applied; monitoring                        |
| 13:05 | Verified correct; resolved                     |

## Root cause
<The technical cause. Blameless — describe the system and process gaps, not
the person. "The merge wasn't guarded on updated_at" not "X forgot to…">

## What went well / what didn't
- Went well: <e.g. freshness check caught it before the exec dashboard>
- Didn't: <e.g. no owner listed for the source table; 40-min detection lag>

## What would have caught this earlier?
<Usually a data test or a freshness check — see `test-data` if installed.>

## Action items
| Action                                   | Owner   | Due        | Tracking          |
|------------------------------------------|---------|------------|-------------------|
| Add updated_at guard to merge            | <name>  | YYYY-MM-DD | <issue link>      |
| Add freshness check at 2× SLA            | <name>  | YYYY-MM-DD | <issue link>      |
| Assign owner to source table             | <name>  | YYYY-MM-DD | <issue link>      |

File each action as work in the issue tracker. If the fix changes the
architecture, record it as an ADR.
```

Every action item has an **owner** and a **due date** — an action without
both is a wish, not a fix (SRE principle). Keep the review blameless so
people surface the real cause instead of hiding it.
