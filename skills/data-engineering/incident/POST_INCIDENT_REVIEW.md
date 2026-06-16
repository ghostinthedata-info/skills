# Post-Incident Review (PIR / Retro) Template

A blameless review to understand what happened, why, and how to stop it recurring.
Run for **D1/D2 within 2 business days**, and for any **recurring D3**.

**Blameless rule:** describe systems, signals, and decisions made with the
information available at the time — never individuals as the cause. The goal is a
more resilient system, not accountability for a person.

Fill this out, then use it to (a) draft the 6.4 Executive Summary if D1/D2 and
(b) raise prevention actions per `references/prevention.md`.

---

## 1. Summary
- **Incident title:**
- **Severity:** [D1 / D2 / D3]
- **Date:**
- **Affected system(s)/report(s):** [Workday / Salesforce / Canvas / StudentOne /
  Oracle / S3 / Snowflake / dbt model …]
- **One-line description:**

## 2. Impact
- **Who was affected:** [teams / faculties / dashboards]
- **What they couldn't do:**
- **Data integrity:** [delayed / wrong / lost-but-replayable / lost]
- **Was any decision made on bad or missing data?** [Y/N — detail]
- **Historical gap:** [fully backfilled / gap remains — describe]

## 3. Timeline
*Chronological, with timestamps. Detection → resolution.*

| Time | Event |
|---|---|
| T+0 | [Detected — by whom/what: monitor, alert, stakeholder report] |
| | [Confirmed / classified] |
| | [Initial notification sent] |
| | [Root cause identified] |
| | [Fix applied / reprocessing started] |
| | [Data verified current] |
| | [Resolution notification sent] |

**Detection method:** [automated monitor / alert / stakeholder reported]
*(If stakeholder-reported, prevention should include a monitor so we catch it first.)*

## 4. Root cause analysis (5 Whys)
Separate the **trigger** (what set it off) from the **root cause** (why the system
allowed it).

- **Symptom:**
- **Why 1:**
- **Why 2:**
- **Why 3:**
- **Why 4:**
- **Why 5 (root cause):**

- **Trigger:**
- **Root cause:**
- **Why wasn't it caught earlier?** [missing test / no monitor / silent failure]

## 5. Resolution
- **What fixed it:**
- **Reprocess / backfill / replay performed:**
- **Verification:** [how we confirmed data is correct and current]

## 6. Latent / residual risk
- **Could this recur?** [Y/N — under what conditions]
- **How many more records/objects could hit the same cause?**
- **Replayable from upstream?** [Y/N]
- **Constraints on remediation** [e.g. source platform retiring → targeted, not
  broad, remediation]

## 7. What went well / what didn't
- **Went well:** [fast detection, clean comms, good containment …]
- **Didn't:** [slow detection, unclear ownership, manual reprocessing …]
- **Got lucky:** [things that happened to work but aren't reliable]

## 8. Preventative actions
*Concrete, owned, dated. Each becomes a Jira item. See `references/prevention.md`.*

| # | Action | Type (detect/prevent/respond) | Owner | Due | Jira |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

## 9. Sign-off
- **Confirmed resolved & gap closed:** [Y/N — who signed off]
- **PIR shared with:** [EDP team / leadership]
- **Runbook updated:** [Y/N — link]
