<!--
SOLUTION DESIGN TEMPLATE
Fill every section. Delete bracketed guidance as you go. Keep it to roughly one
page of substance per section — this is a design, not a thesis. The inline SVG
is hand-authored per project; edit the labels and keep the zone colours.
-->

# Solution Design — [Pipeline / Report Name]

**Author:** [name] · **Date:** [YYYY-MM-DD] · **Status:** Draft / Reviewed / Approved

---

## 1. Summary — reason & value

> For **[customer profile]** who **[job-to-be-done]**, this **[pipeline/report]**
> relieves **[pain]** and delivers **[gain]**. It is **[importance level]**
> because **[stakes]**.

[2-4 sentences: what decision this enables, what's broken today, and the grain.]

**Grain:** **[one row represents …]**

---

## 2. Overview

[High-level flow only — tools and patterns, not implementation detail. Edit the
labels below. Zones: source = cyan, ingest = blue, transform = purple,
delivery = green. Reference how the pattern-bank phases flow.]

<svg viewBox="0 0 920 220" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="13">
  <!-- SOURCE -->
  <rect x="20"  y="60" width="180" height="100" rx="10" fill="#e0f7fa" stroke="#00acc1"/>
  <text x="110" y="50" text-anchor="middle" font-weight="bold" fill="#00838f">SOURCE</text>
  <text x="110" y="105" text-anchor="middle">[System / vendor]</text>
  <text x="110" y="125" text-anchor="middle" fill="#555">[API / file / CDC]</text>

  <!-- INGEST -->
  <rect x="250" y="60" width="180" height="100" rx="10" fill="#e3f2fd" stroke="#1e88e5"/>
  <text x="340" y="50" text-anchor="middle" font-weight="bold" fill="#1565c0">INGEST → RAW</text>
  <text x="340" y="105" text-anchor="middle">[Landing + loader]</text>
  <text x="340" y="125" text-anchor="middle" fill="#555">[Pattern]</text>

  <!-- TRANSFORM -->
  <rect x="480" y="60" width="180" height="100" rx="10" fill="#f3e5f5" stroke="#8e24aa"/>
  <text x="570" y="50" text-anchor="middle" font-weight="bold" fill="#6a1b9a">TRANSFORM</text>
  <text x="570" y="105" text-anchor="middle">[Models / WAP / SCD2]</text>
  <text x="570" y="125" text-anchor="middle" fill="#555">[Pattern]</text>

  <!-- DELIVERY -->
  <rect x="710" y="60" width="180" height="100" rx="10" fill="#e8f5e9" stroke="#43a047"/>
  <text x="800" y="50" text-anchor="middle" font-weight="bold" fill="#2e7d32">DELIVERY</text>
  <text x="800" y="105" text-anchor="middle">[View / extract / event]</text>
  <text x="800" y="125" text-anchor="middle" fill="#555">[Consumer]</text>

  <!-- arrows -->
  <defs><marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#555"/></marker></defs>
  <line x1="200" y1="110" x2="248" y2="110" stroke="#555" stroke-width="2" marker-end="url(#a)"/>
  <line x1="430" y1="110" x2="478" y2="110" stroke="#555" stroke-width="2" marker-end="url(#a)"/>
  <line x1="660" y1="110" x2="708" y2="110" stroke="#555" stroke-width="2" marker-end="url(#a)"/>
</svg>

**Recipe:** Ingestion = [pattern] · Transformation = [pattern] · Delivery = [pattern]

---

## 3. Tasks & steps

**Estimate basis:** [N known patterns — sized from actual past timings] ·
[M known with caveats — name each, with its buffer or spike] · [K novel —
time-boxed discovery; re-estimate after the proof of concept]

[Group into themed stories of about one effort-day each, at most five per
slice. Each story has subtasks, a definition of done, and a handover. Effort
isn't calendar time — the waiting happens at the seams below.]

### Story 1 · [title — e.g. Environment & Access Setup] · effort ≈1d
- [ ] [Subtask]
- [ ] [Subtask]
**Done when:** [definition of done — another engineer could pick it up
tomorrow with no conversation] · **Hands to:** [next story / person]

### Story 2 · [title — e.g. Ingest Build & Ship to Production] · effort ≈1d
- [ ] [Subtask]
**Done when:** [real batches land where production builds can see them] ·
**Hands to:** […]

### Story 3 · [title — e.g. Transformation & Data Quality] · effort ≈1d
- [ ] [Subtask]
**Done when:** […]

[Add stories as needed — heavier ingestion (CDC/replication) may warrant a
5th. Never bundle more than 5 stories into one slice.]

### Seams — where elapsed time accumulates

| From → To | Handover (what crosses) | Waiting on | Elapsed estimate | Owner |
|---|---|---|---|---|
| [Ingest → Transformation] | [staging table, its contract, known quirks] | [first real batches in production] | [e.g. 3 days] | [name] |

**Estimate:** effort (sum of stories) + elapsed time at the seams, estimated
separately.

---

## 4. Decisions register

[Official format. Log every material decision so it isn't silently re-litigated.
Scope changes mid-slice get added here rather than absorbed.]

| # | Date | Decision | Why | Alternatives considered | Owner | Status |
|---|------|----------|-----|------------------------|-------|--------|
| D1 | [YYYY-MM-DD] | [e.g. System X is the source of truth] | [rationale] | [what was rejected] | [name] | Agreed / Superseded |
| D2 | | | | | | |

---

## 5. Dependencies & risks

**Dependencies** — list what must be ready, who owns it, by when.

| Dependency | Owner | Needed by | Status |
|------------|-------|-----------|--------|
| [e.g. Vendor API access provisioned] | [name] | [date] | Open / Done |

**Risks** — pull relevant ones from `COMMON-RISKS.md`; add project-specific risks.

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|
| [e.g. Silent deletes in delta feed] | Med | High | [reconcile vs snapshot weekly] | [name] |

---

## 6. Acceptance criteria

[Explicit, testable. The pipeline is accepted when all hold.]

- [ ] Grain holds: one row per [grain], uniqueness tested.
- [ ] Freshness SLA met: data available by [time].
- [ ] Definitions match: [metric] computed per the agreed definition.
- [ ] Idempotent: running the load twice on the same input leaves row counts
      and checksums unchanged.
- [ ] Rebuildable: the table rebuilds from raw in one command, and the
      incremental result matches a full rebuild.
- [ ] Business validation ran on real production history (fabricated rows
      only in unit tests).
- [ ] [Historization, reliability, latency criteria as applicable.]
