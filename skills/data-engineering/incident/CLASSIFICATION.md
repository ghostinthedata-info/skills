# Data Incident Classification

How to classify a data/reporting incident by **severity**, **impact**, and
**latent risk**. Classification drives comms cadence, who's notified, and how many
people respond. When genuinely torn between two tiers, **pick the higher severity**
and confirm (or downgrade) in the review — over-mobilising briefly is cheaper than
under-reacting to a real one.

These data severities (D1–D4) are deliberately separate from infrastructure /
application severity frameworks. Reporting & analytics incidents are typically low
business criticality (C4–C5) and are not production outages.

## Step 1 — Severity tiers

| Severity | Label | Description | Example | Business criticality |
|---|---|---|---|---|
| **D1** | Data Critical | Data loss or corruption affecting decision-making for a major institutional process | Enrolment reporting data corrupted ahead of board submission | C4 |
| **D2** | Data High | Data significantly delayed or unavailable, affecting time-sensitive reporting | Daily financial dashboard delayed 6+ hrs on a reporting day | C4 |
| **D3** | Data Medium | Data delayed or partially unavailable, affecting routine reporting | Overnight pipeline failed; morning refresh 2–3 hrs late | C5 |
| **D4** | Data Low | Minor delay or cosmetic issue, no meaningful impact on decisions | Non-critical report stale by < 1 business day | C5 |

## Step 2 — Impact × Urgency (sanity-check the tier)

Don't classify on the symptom alone. Severity = **impact** (how bad / how wide) ×
**urgency** (how time-sensitive right now).

**Impact — how wide and how damaging:**
- *Blast radius:* one report, or hundreds of downstream tables/dashboards?
- *Data integrity:* delayed (will self-heal) vs **wrong** (silently misleading) vs
  **lost** (unrecoverable). Wrong data is worse than missing data — people may act
  on it unknowingly.
- *Audience:* internal analysts vs faculty/business vs board/executive.

**Urgency — how time-sensitive:**
- Is a decision or deadline (board pack, payroll, enrolment census, funding
  submission) dependent on this data *today*?
- Reporting day vs quiet period.
- A delay that resolves before anyone needs the data is effectively D4.

**Rule of thumb:**
- Wrong data feeding an imminent decision → escalate toward **D1**.
- Delayed data, no imminent decision → **D3**, even if the pipeline failure looks
  dramatic.

## Step 3 — Latent risk (the part people miss)

Beyond the immediate impact, assess what *could* still go wrong:

- **Recurrence risk:** will this re-fire on the next run if not root-caused?
  (e.g. a SQL parsing edge case that recurs whenever XML spills across files.)
- **Scale risk:** how many more records/objects could hit the same constraint?
  (e.g. a field-length limit one record tripped that thousands could also trip.)
- **Replayability:** is the data lost, or just unprocessed and replayable from
  intact upstream files? Replayable = lower severity, but still log the gap.
- **Platform risk:** is remediation constrained by something larger (e.g. a source
  platform being retired, making broad fixes impractical → favour targeted
  table-level remediation)?

Record latent risk explicitly even when the live incident is minor — it becomes a
backlog item and feeds the prevention loop. A D3 today with high recurrence risk
deserves a review even though the tier alone wouldn't require one.

## Step 4 — What the classification triggers

| | D1 | D2 | D3 | D4 |
|---|---|---|---|---|
| Initial notification | T+30 min, all groups | T+1 hr, business/faculty | T+2 hrs, business/faculty | Log in Jira only |
| Status updates | Every 2 hrs until resolved | As needed | — | — |
| Roles (Lead/Comms/Liaison) | Always separated | Always separated | May be one person | May be one person |
| Executive awareness | Always | At Lead's discretion | No | No |
| Resolution notification | Yes | Yes | Yes | Only if impacted/enquired |
| Post-incident review | Yes, ≤2 business days | If requested by leadership | Only if recurring | No |
| Data Ops & Analytics | Init+Upd+Res | Init+Res | Init+Res | No contact |
| Business data consumers | Init+Upd+Res | Init+Upd+Res | Init+Res | No contact |
| EDP internal (BCC) | Always | Always | Always | Always |

## Quick decision flow

```
Data issue detected & confirmed
        │
        ▼
Is data LOST/CORRUPT and feeding a major decision now? ── yes ──► D1
        │ no
        ▼
Significantly delayed/unavailable AND time-sensitive reporting? ── yes ──► D2
        │ no
        ▼
Delayed / partially unavailable, routine reporting? ── yes ──► D3
        │ no
        ▼
Minor delay / cosmetic, no decision impact ──► D4
```
Always then ask: *what's the latent risk?* and adjust attention (not necessarily
tier) accordingly.
