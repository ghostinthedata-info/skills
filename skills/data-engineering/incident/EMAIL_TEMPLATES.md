# Email Templates — Data Incident Communications

Rules that apply to every email:
- Send from the EDP team address or the Communications Lead.
- **Always BCC `edpteam@unimelb.edu.au`.**
- Structure: what happened → impact → root cause → current status → next steps.
- Plain English. No internal jargon for business/faculty audiences.
- **Never include individual user emails or names** as data.
- Match tone to severity: calm for D3/D4, crisp and prompt for D1/D2. Never alarmist.
- Fill every `[bracketed]` placeholder or delete the line.

---

## 6.1 — Initial Notification
*Use for D1, D2, D3. Adapt tone to severity.*

**Subject:** [DATA NOTICE] <Affected Report/System> — Data Delay | <Date>

Hi [First Name / Team],

I'm writing to let you know we're currently experiencing a delay with [affected
report, dashboard, or data feed].

**What's affected:** [Brief, plain-English description — e.g. "The daily financial
summary dashboard isn't reflecting data from today's overnight refresh."]

**Impact:** [What the stakeholder can't do as a result — e.g. "Today's figures may
be understated. We recommend not using the dashboard for decision-making until
resolved."]

**Current status:** Under investigation by the EDP team.

**Expected resolution:** [Estimate if known, or "We'll provide an update by [time]."]

We'll keep you updated as the situation develops. If you have any questions in the
meantime, please don't hesitate to reach out.

Regards,
[Your Name]

---

## 6.2 — Status Update
*Use during prolonged D1 (and D2 if warranted) before resolution.*

**Subject:** [UPDATE] <Affected Report/System> — Data Delay | <Date> — <Time>

Hi [First Name / Team],

A quick update on the ongoing data delay affecting [affected report/system].

**Current status:** [e.g. "We've identified the root cause as a failed ingestion
job and are reprocessing the affected data."]

**Revised ETA:** [Updated estimate, or "We expect further information by [time]."]

**Workaround (if applicable):** [e.g. "In the interim, yesterday's data is still
available and can be used as a reference."]

We appreciate your patience and will notify you as soon as the issue is resolved.

Regards,
[Your Name]

---

## 6.3 — Resolution Notification
*Use for ALL severities on resolution. Always closes the loop.*

**Subject:** [RESOLVED] <Affected Report/System> — Data Delay | <Date>

Hi [First Name / Team],

I'm pleased to let you know the data delay affecting [affected report/system] has
been resolved.

**Resolved at:** [Time and date]

**What happened:** [One or two plain-English sentences — e.g. "An upstream pipeline
job failed during the nightly processing window, which prevented data loading into
the reporting layer. The job has been re-run and data is now current."]

**Current status:** Data is now up to date. [State explicitly whether any historical
gap remains or data has been fully backfilled.]

**Next steps:** [e.g. "We're adding alerting to detect this class of failure
earlier." or "No further action required."]

Please let us know if you notice anything unexpected in your reports.

Regards,
[Your Name]

---

## 6.4 — Executive Post-Incident Summary
*Use for D1/D2, sent to leadership 1–2 business days after resolution.*

**Subject:** [POST-INCIDENT SUMMARY] <Affected Report/System> — <Date of Incident>

Hi [Name],

Following last [day]'s data incident, please find a brief summary for your
awareness.

**Incident:** [One-line description]
**Severity:** [D1 / D2]
**Duration:** [Start time → End time]
**Stakeholders affected:** [Teams/faculties impacted]
**Root cause:** [Plain-English explanation of what went wrong]
**Resolution:** [What was done to fix it]

**Preventative actions:**
- [Action 1 — e.g. alerting threshold lowered to detect failure within 15 minutes]
- [Action 2 — e.g. runbook updated with manual reprocessing steps]
- [Action 3 — e.g. Jira raised for pipeline resilience improvement: LINK]

Please don't hesitate to reach out if you'd like to discuss further.

Regards,
[Your Name]

---

## Tone cheat-sheet

| Severity | Opening posture | Cadence | Exec loop |
|---|---|---|---|
| D1 | Prompt, controlled, confident | T+30min then every 2 hrs | Always |
| D2 | Crisp, reassuring | T+1hr, updates as needed | Lead's discretion |
| D3 | Calm, routine | T+2hrs, then resolution | No |
| D4 | Usually none unless asked | Resolution only if impacted | No |
