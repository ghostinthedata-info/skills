---
name: profile-data
description: Profile a new or unfamiliar dataset BEFORE building on it. Produces row counts, cardinality, null/blank analysis, key-uniqueness checks, distribution/outlier checks, a type/precision audit, and an optional saved baseline for drift detection — the design-time reconnaissance that tells modelling and testing what to watch for. Use whenever the user is about to model, ingest, join, or design a pipeline on a dataset they don't yet fully understand, is partway through a solution or pipeline design and needs the grain, keys, or risks, is deciding what data-quality tests to write, or says "profile this table" / "what's in this data?" / "what should I test for?". Trigger it ahead of data-modelling, solution-design, or test-data work even if the user doesn't say "profile".
---

# Profile Data

You cannot test, model, or trust data you haven't profiled. Profiling is the
sturdy foundation before the skyscraper (Ghost in the Data, "The Art of Data
Profiling"). Do it first; the findings tell downstream design and testing what
to watch for.

Write SQL for the engine named in `docs/agents/platform.md` (if present). The
template is tool-agnostic — swap in your engine's functions.

## Where this sits

This is the **design-time reconnaissance** pass and the **bottom-up** half of
data-quality assessment (DMBOK): inspect the data itself to surface anomalies,
then vet them top-down with the people who own the business context. Run it:

* **before `data-modelling`** — to fix the grain and confirm the business key
  before any DDL;
* **inside `solution-design`** — to ground the source and SLA decisions in
  what the data actually is;
* **ahead of `test-data`** — every finding names a DMBOK data-quality
  dimension so it carries straight through into a test (if those skills are
  installed).

| Section | DQ dimension(s) |
|---|---|
| Cardinality / key uniqueness | **Uniqueness** |
| Completeness | **Completeness** |
| Distribution & outliers | **Reasonableness**, **Accuracy** (flagged) |
| Types, formats, sensitivity | **Validity**, **Privacy** |
| Drift vs baseline | **Consistency**, **Currency/Timeliness** |

(Validity = well-formed for the domain; accuracy = actually correct — profiling
can assert validity but only flags suspected accuracy issues for an SME.)

## The discipline — run every section, in order

### 1. Shape
* Total row count. Row count per partition or load date if partitioned (often
  a load or batch column).
* Column count, names, declared types, and (for strings) max length.
* The "Razzle Dazzle Rose" trap: a type *inferred* from the values seen so far
  (by a loader, a dataframe, or auto-detection) is too narrow for values that
  arrive later — "Red" and "Orange" suggest `varchar(10)`, then a longer
  colour is truncated. Compare the source's declared type with the type at
  every hop the data lands in, never size a column from observed values
  alone, and still flag any column whose real max length approaches its
  declared cap. Some engines give an unsized string a huge default cap, so the
  observed-vs-declared comparison matters more than the declared type alone.

### 2. Cardinality
* `COUNT(DISTINCT col)` and distinct% (`distinct / total * 100`) per column.
* Distinct% ≈ 100 → candidate key. Distinct% ≈ 0 → constant/low-signal.
  Mid-range → categorical (capture the value set for accepted-values tests).
* On large tables use your engine's approximate distinct count to keep the
  scan cheap; confirm exact counts only on the columns that look like keys.

### 3. Key uniqueness — the make-or-break check
* For each candidate business key (and composite), confirm
  `COUNT(*) = COUNT(DISTINCT key)`. **If it fails, stop and surface it** —
  a non-unique "key" silently fans out every downstream join and breaks the
  grain you're about to model.
* Check the key for nulls separately; a nullable key is not a key.
* This is the gate for `data-modelling`: don't agree a grain until it passes.

### 4. Completeness
* Null count AND null% per column. Separately count empty strings,
  whitespace-only, and sentinel values ('N/A', 'NULL', '-', 'UNKNOWN', zero
  dates like '1900-01-01').
* Decide per column: is null expected, or a defect?

### 5. Distribution & outliers
* Numeric: min/max/mean/quartiles (approximate percentiles are fine); flag
  impossible values (negative ages, future dates).
* Use null-safe comparison (`IS DISTINCT FROM` or your dialect's equivalent)
  whenever NULLs are in play.

### 6. Types, formats, sensitivity
* Confirm dates, time-zone semantics (a timestamp without a zone, with one, or
  in session-local time — a frequent source-load gotcha), and numeric
  precision are what you assumed.
* Regex-scan for PII patterns (emails, phone, national IDs, postcodes) and
  classify by sensitivity so the model masks/encrypts/excludes appropriately
  (`data-security-classification` decides the tier, if installed).

### 7. Offer to save the baseline
Ask the user once: "Save this baseline to `docs/profiles/<table>.md`?"
If yes, write the profile (counts, cardinalities, null rates, observed
ranges, value sets, profiled-at date). Rules for what may be persisted:

* **Aggregates only** — counts, percentages, ranges, cardinalities. Never
  sample rows or record-level values.
* **Columns flagged as PII in step 6 get statistics only** — no observed
  value sets, no min/max for free-text identifiers.

This baseline is what data tests turn into volume/variance thresholds and
what drift detection diffs against on the next load (see `test-data` if
installed).

## Output

A short report aimed at the design decision in front of the user:

* **Shape** — rows, columns, partition profile.
* **Candidate keys** — each with pass/fail on uniqueness and the grain it
  implies. This is the headline for `data-modelling`.
* **Columns that need tests** — each tagged with its DMBOK dimension and a
  severity (error/warn), ready for `test-data`.
* **Anomalies found** — with a question for the SME where accuracy is only
  suspected.
* An explicit **"safe to build on / not yet"** verdict.

Don't proceed to modelling until keys pass. Hand the keys and grain to
`data-modelling`, the tagged columns to `test-data`, and the source and SLA
facts back to `solution-design`.

## Template

For pseudo-SQL scaffolds of every section above and the baseline report
shape, see [PROFILE-TEMPLATE.md](./PROFILE-TEMPLATE.md). Keep them
tool-agnostic — swap in your engine's functions (consult
`docs/agents/platform.md` if present).
