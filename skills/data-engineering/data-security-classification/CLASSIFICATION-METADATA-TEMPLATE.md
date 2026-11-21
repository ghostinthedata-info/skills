# Recording the classification (templates)

A classification only protects data if it lives **with the model** and travels
with it — not in a spreadsheet that goes stale. Pick **one** place to record
it per repo and do it the same way every time. Decide this once at setup (the
`setup-ghost-skills` tooling answer tells you whether you're a dbt shop) and
write the choice into `docs/agents/security-classification.md` so the agent
applies it consistently.

Every classified column carries the same four facts:

- `classification` — the tier: `public` | `internal` | `confidential` | `restricted`
- `pii` (or `phi`, `pci`) — `true`/`false` so scanners can find regulated columns fast
- `requirement_source` — *why* it's restricted (the law/contract/policy), for audits
- `masking` — what broad audiences see: `none` | `hash` | `tokenize` | `partial-last4` | `redact`

Optionally add `steward` (who owns the decision) and `review_by` (a date — see
the "classify-once, never-review" anti-pattern).

Restricted data also carries its **lifecycle** — usually set on the model, and
on a column only when that column has a shorter life than its table:

- `retention` — how long it's kept: `90d`, `7y`, …
- `retention_basis` — the date the clock runs from: `event_date` (operational
  data) or `load_date` (archives — under an event-date clock, history
  backfilled last week can be purged at once)
- `on_expiry` — what happens at the end: `delete` | `anonymise`
- `deidentification` — `none` | `pseudonymised` | `anonymised`. Pseudonymised
  data (a mapping back to the person exists) keeps its tier; only truly
  anonymised data can drop it.
- `min_cell_size` — on aggregates published as anonymous: the smallest group
  a cut may show (e.g. `10`); smaller cells are suppressed or rolled up.

---

## Option A — dbt (`schema.yml` / `models/**/*.yml`)

Preferred when you use dbt: the metadata lives in the model contract, ships in
the manifest, surfaces in docs, and can be tested. Put column-level facts under
`meta`; keep a model-level default for the table's highest tier.

```yaml
version: 2

models:
  - name: dim_customer
    description: "Customer dimension. Contains PII — restricted."
    meta:
      classification: restricted          # table = its most sensitive column
      owner: data-platform
      retention: 7y
      retention_basis: event_date
      on_expiry: anonymise
    columns:
      - name: customer_key
        description: "Surrogate key (PK)."
        meta:
          classification: internal
          pii: false

      - name: email
        description: "Customer email."
        meta:
          classification: restricted
          pii: true
          requirement_source: "GDPR Art.5 / privacy policy v3"
          masking: partial-last4          # broad roles see j***@e***.com
          deidentification: none
          steward: jane.doe

      - name: ssn
        description: "National ID. Restricted — never exposed unmasked."
        meta:
          classification: restricted
          pii: true
          requirement_source: "PCI/PII policy"
          masking: hash
```

Make it enforceable, not just documentation:

- A test/CI check that **every column has a `classification`** (fail the build
  on an unclassified column — see `test-data` if installed).
- A check that any column with `pii: true` also has a non-empty
  `requirement_source` and a `masking` value other than `none`.
- Drive masking from the metadata: generate per-role views/grants from the
  `masking` value rather than hand-writing them (single source of truth).
- A check that every model holding a restricted column has `retention`,
  `retention_basis`, and `on_expiry` — restricted data with no end date is
  kept forever by default.
- A check that every model published as anonymous has `min_cell_size`, and
  that its output has no group smaller than it.

An aggregate published as anonymous:

```yaml
  - name: agg_accounts_by_region
    description: "Account counts by region, age band and product. Published as anonymous."
    meta:
      classification: internal
      deidentification: anonymised
      min_cell_size: 10                   # cells under 10 accounts are suppressed
```

---

## Option B — no dbt: a sidecar `.yml` next to the `.sql`

If you write plain SQL (or use another transformer without column metadata),
keep a `<model>.meta.yml` beside each `<model>.sql`. Same four facts; a small
CI script asserts the sidecar exists and every column is covered.

```
models/marts/
  dim_customer.sql
  dim_customer.meta.yml      <-- this file
```

```yaml
# dim_customer.meta.yml
table: dim_customer
classification: restricted
owner: data-platform
retention: 7y
retention_basis: event_date
on_expiry: anonymise
columns:
  customer_key:
    classification: internal
    pii: false
  email:
    classification: restricted
    pii: true
    requirement_source: "GDPR Art.5 / privacy policy v3"
    masking: partial-last4
  ssn:
    classification: restricted
    pii: true
    requirement_source: "PCI/PII policy"
    masking: hash
```

(If your warehouse supports column comments/tags or object tagging, mirror the
tier there too so it's visible in the catalog — but keep the `.yml` as the
source of truth that lives in version control.)

---

## Option C — opt out (explicit, not silent)

Some teams won't document classification — that's a valid choice for a repo
with no regulated data. If so, record the decision **once** so it's deliberate,
not an oversight, and so the agent stops prompting for it:

```markdown
# docs/agents/security-classification.md
Classification: NOT TRACKED in this repo.
Rationale: <e.g. no PII/PHI/PCI; internal analytics on public data only>.
Decided by: <name>  Date: <YYYY-MM-DD>  Revisit if: regulated data is ingested.
```

The agent should still **flag** if profiling later finds PII-shaped columns
(see `profile-data` if installed) — opting out of documentation is not the same
as opting out of noticing.
