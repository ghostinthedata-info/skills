---
name: data-security-classification
description: Classify data by sensitivity and recommend the controls that govern it — a confidentiality tier per column, the metadata to record with the model (dbt docs or a sidecar file), masking or pseudonymisation, retention and deletion, and the RBAC roles that manage access — driven by regulatory and confidentiality requirements. Produces a documented set of recommended actions (classify column X as restricted, mask Y, govern with role Z). Use whenever profiling surfaces columns, whenever you design a pipeline/model/solution, or whenever you handle personal or regulated data, decide who can see what, or design masking/access — even if the user doesn't say "classify". Runs downstream of profile-data (which finds the candidates) and inside solution-design (where access is designed with the model, not bolted on after). Covers the four A's (authentication, authorization, access, auditing), confidentiality levels, PII/PHI/PCI, least privilege, and RBAC.
---

# Data Security Classification

You cannot protect data you haven't classified, and you can't classify it
without knowing what it is — so this follows profiling and runs alongside
design. Data Security Management is the planning and execution of policies
that provide proper **authentication, authorization, access, and auditing**
("the four A's") of data assets. Guiding maxim: design controls so that
**compliance is easier than non-compliance** — the right people can use data
the easy way; inappropriate access takes effort.

## When this runs

This skill isn't a standalone gate — it plugs into two upstream workflows:

* **After `profile-data`** — profiling (if installed) is where PII-shaped
  columns are first found by regex and heuristics. Those are *candidates*.
  This skill decides the **tier**, the **metadata** to record, and the
  **RBAC** to govern them. If profiling flagged columns, classify every one of
  them here.
* **During `solution-design`** — classify and design access **with** the
  model, never as a final gate after it ships. When a design touches a
  source, model, or report, run this skill over its columns so the design doc
  carries the classification and access recommendations.

Either entry point produces the same thing: **a documented set of recommended
actions**, delivered inline — what each column should be classified as, what
goes into its metadata, and which roles govern it.

## Step 1 — Classify by sensitivity

Assign every dataset/column a confidentiality level, driven by what it is and
what regulates it. A workable tiering:

* **Public** — no harm if disclosed.
* **Internal** — default for ordinary business data; staff-only.
* **Confidential** — disclosure harms the business or a partner (contracts,
  pricing, financials).
* **Restricted / Regulated** — legally protected: **PII** (personal
  identifiers), **PHI** (health), payment-card data (**PCI**), and other
  regulator-defined categories.

The classification is **business metadata on the column** — record it with
the model (see *Where to record it* below) and let the steward own it. The PII
regex scan in `profile-data` (if installed) is where the candidates are first
found; this skill decides the tier and the controls.

## Step 2 — Identify the requirements driving it

Controls aren't chosen by taste; they're driven by:

* **Regulatory** — privacy/health/financial law and industry standards for the
  jurisdictions and sectors the data touches.
* **Contractual** — partner/customer confidentiality obligations.
* **Internal policy** — what the business itself requires.

Capture *why* a column is restricted, not just that it is — the requirement
source justifies the control and survives audits. It becomes the
`requirement_source` in the metadata.

## Step 3 — Apply controls to the tier

* **Access control — least privilege + role-based (RBAC).** Grant by role, not
  by person; grant the minimum needed for the job. Restricted data is
  deny-by-default. Authenticate (who you are) then authorize (what you may
  do). Step 4 turns the tier into a concrete role recommendation.
* **Masking / obfuscation** — for restricted columns seen by broad audiences:
  redact, tokenize, hash, or partially mask (last-4). Distinguish
  **production masking** (dynamic, per-role views) from **non-production
  masking** (irreversibly de-identify before data ever reaches dev/test — see
  `test-data` if installed; never copy raw PII into lower environments).
* **Pseudonymised is not anonymised.** Tokenised or hashed output with a
  mapping table — or any other way back to the person — is still personal
  data and keeps its tier. The mapping table is restricted, granted
  separately, and every read of it is audited. Aggregates published as
  anonymous enforce a minimum group size per dimensional cut: suppress or
  roll up small cells, or the aggregate re-identifies people.
* **Encryption** — protect data **at rest** and **in transit**; manage keys
  separately from data. Required for regulated tiers.
* **Auditing** — log access and changes to sensitive data: who saw/changed
  what, when. Monitoring usage is part of the control, not an afterthought —
  it's how you prove compliance and detect misuse.
* **Retention & deletion** — give each dataset a retention period, justified
  by the same requirement source as its tier, and pick the clock on purpose:
  event date for operational data, load date for archives (under an event-date
  clock, history backfilled last week can be purged at once). At expiry,
  delete or anonymise. Legal holds override deletion, so delete jobs check
  for an active hold first.
* **Every copy** — controls follow the data, not the warehouse. List each
  place a classified dataset lands (landing zone, archive, cache, serving
  store, extracts, backups) and apply the tier's controls and retention in
  each.

Match the control to the tier: don't encrypt-and-audit public data, and never
leave restricted data on access alone.

## Step 4 — Recommend the RBAC to manage it

Classification is inert until access is governed. For each model or table,
turn the tier into a **role recommendation** — keep it light: name the role
and the access level, recommend the masking approach, and leave the actual
grant statements to the implementer (they're engine- and naming-specific).

For each model, recommend:

* **Which roles may read it, and at what fidelity.** Map tiers to a small set
  of functional roles (e.g. `ANALYST`, `ENGINEER`, a privileged `STEWARD`).
  Restricted columns are deny-by-default — broad roles see the *masked* form;
  only a named privileged role sees them unmasked.
* **The masking approach per restricted column** — taken straight from the
  `masking` value in the metadata. Generate the per-role views, grants, or
  masking policies from the metadata rather than hand-writing them, so there's
  one source of truth.
* **Deny-by-default** — say explicitly that no role gets restricted data
  unless it's named.

Express the recommendation as a small grid, e.g.:

| Role | dim_customer (general columns) | email (restricted) | ssn (restricted) |
| --- | --- | --- | --- |
| ANALYST | read | masked (partial-last4) | denied |
| ENGINEER | read | masked | masked (hash) |
| PII_STEWARD | read | unmasked | unmasked |

Then note the implementation hook without writing the DDL: "Generate grants
and masking from the column metadata; broad roles get the masked view,
`PII_STEWARD` the base table." Leave the exact grant and masking-policy
statements to the user — they differ by engine.

## Anti-patterns (call these out)

* **Classify-once, never-review** — sensitivity changes as data combines;
  re-classify when models join restricted with innocuous columns (a join can
  re-identify). Give every classification a `review_by` date.
* **Person-level grants** — ungovernable; use roles.
* **Calling tokenised data anonymous** — if a mapping exists, it's
  pseudonymised and still regulated.
* **Raw PII in dev/test** — the most common breach path. De-identify on the
  way down.
* **Security as a final gate** — bolt-on access rules after a model ships.
  Classify and design controls *with* the model — which is why this skill
  runs inside `solution-design`, not after it.
* **Classification with no access governance** — a tier in the metadata that
  no grant or masking policy enforces is decoration. Every restricted column
  must trace to a role recommendation (Step 4).

## Deliver

Deliver, inline in the conversation, a **recommended-actions** set covering:

1. **Classification per dataset/column** — tier, `requirement_source`, and
   steward, ready to drop into the metadata.
2. **The metadata to add** — the block(s) per the template below, so the
   classification ships with the model and stays in sync.
3. **The RBAC recommendation** — the role/access grid from Step 4 (roles,
   tier, masking approach), plus the implementation hook; grants left to the
   user.
4. **Masking, encryption, and audit posture** — which columns are masked and
   how (pseudonymised or anonymised), the encryption requirement for regulated
   tiers, and what is audited.
5. **Retention and every copy** — the retention period and its clock, the
   expiry action, legal-hold handling, and every location the data lands.

Frame these as concrete actions ("Classify `email` as restricted, add
`pii: true` and `masking: partial-last4` to its metadata, grant unmasked read
to `PII_STEWARD` only"), not abstract advice. Record the classification as
metadata so downstream models inherit it.

## Where to record it (templates)

Don't leave the classification in a side spreadsheet — bake it into the model
so it ships and stays in sync. See
[CLASSIFICATION-METADATA-TEMPLATE.md](./CLASSIFICATION-METADATA-TEMPLATE.md)
for three ready patterns, chosen by the repo's tooling (the
`setup-ghost-skills` answer tells you which):

* **dbt** — column-level `meta` (`classification`, `pii`, `requirement_source`,
  `masking`) in `schema.yml`, made enforceable by a test that fails the build
  on any unclassified column.
* **No dbt** — a `<model>.meta.yml` sidecar next to the `.sql`, with a CI check
  that the sidecar exists and covers every column.
* **Opt out** — record a deliberate "not tracked" decision in
  `docs/agents/security-classification.md` (valid for repos with no regulated
  data) so it's a choice, not an oversight.

Decide the approach once and write it to `docs/agents/security-classification.md`
so the agent applies it the same way every time.
