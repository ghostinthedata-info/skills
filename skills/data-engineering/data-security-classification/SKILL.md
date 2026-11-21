---
name: data-security-classification
description: Classify data by sensitivity and apply the right controls — access control, masking/obfuscation, encryption, and auditing — driven by regulatory and confidentiality requirements. Covers the four A's (authentication, authorization, access, auditing), confidentiality levels, PII/PHI, and least privilege. Use when handling personal or regulated data, deciding who can see what, or designing masking/access for a model or pipeline.
---

# Data Security Classification

You cannot protect data you haven't classified, and you can't classify it
without knowing what it is — so this follows profiling. Data Security
Management is the planning and execution of policies that provide proper
**authentication, authorization, access, and auditing** ("the four A's") of
data assets. Guiding maxim: design controls
so that **compliance is easier than non-compliance** — the right people can use
data the easy way; inappropriate access takes effort.

## Step 1 — Classify by sensitivity

Assign every dataset/column a confidentiality level, driven by what it is and
what regulates it. A workable tiering:

* **Public** — no harm if disclosed.
* **Internal** — default for ordinary business data; staff-only.
* **Confidential** — disclosure harms the business or a partner (contracts,
  pricing, financials).
* **Restricted / Regulated** — legally protected: **PII** (personal
  identifiers), **PHI** (health), payment-card data, and other
  regulator-defined categories.

The classification is **business metadata on the column** — record it in the
catalog or the model's own metadata (see *Where to record it* below) and let
the steward own it.
The PII regex scan in `profile-data` (if installed) is where the candidates are
first found; this skill decides the tier and the controls.

## Step 2 — Identify the requirements driving it

Controls aren't chosen by taste; they're driven by:

* **Regulatory** — privacy/health/financial law and industry standards for the
  jurisdictions and sectors the data touches.
* **Contractual** — partner/customer confidentiality obligations.
* **Internal policy** — what the business itself requires.

Capture *why* a column is restricted, not just that it is — the requirement
source justifies the control and survives audits.

## Step 3 — Apply controls to the tier

* **Access control — least privilege + role-based.** Grant by role, not by
  person; grant the minimum needed for the job. Restricted data is deny-by-
  default. Authenticate (who you are) then authorize (what you may do).
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

## Anti-patterns (call these out)

* **Classify-once, never-review** — sensitivity changes as data combines;
  re-classify when models join restricted with innocuous columns (a join can
  re-identify).
* **Person-level grants** — ungovernable; use roles.
* **Calling tokenised data anonymous** — if a mapping exists, it's
  pseudonymised and still regulated.
* **Raw PII in dev/test** — the most common breach path. De-identify on the
  way down.
* **Security as a final gate** — bolt-on access rules after a model ships.
  Classify and design controls *with* the model.

## Deliver

A classification per dataset/column (tier + requirement source + steward), and
the matched controls: roles/grants, which columns are masked and how
(pseudonymised or anonymised), encryption posture, what is audited, retention
and deletion, and every location the data lands. Record the classification as
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
