# Pipeline Patterns

A pipeline is **assembled as a recipe**: pick one pattern from each stage —
**Ingestion → Transformation → Delivery** — and combine them. Patterns are
deliberately generic so an engineer can delete what they don't need and drop in
the specifics for their source. Stage colours below match the SVG overview zones
in the solution-design template (source = cyan, ingest = blue, transform =
purple, delivery = green).

Pick the *thinnest* pattern that meets the freshness and historization SLAs.
Complexity is a cost paid forever; only buy it when a consumer need demands it.

---

## Stage 1 — Ingestion (how data lands in raw)

| Pattern | Shape | Use when | Don't use when |
|---|---|---|---|
| **API extract** | Scheduled pull from a REST/GraphQL endpoint, paginated, watermark-driven | Vendor/internal app exposes an API; moderate volume; delta by `modified_at` | The API can't give a reliable watermark or a full extract to reconcile against; volume outgrows rate limits |
| **Flat-file / object drop** | Source lands files (CSV/JSON/Parquet) in a bucket; event-triggered load | Batch exports, SFTP-style handoffs, vendor file feeds | Events need processing in real time (that's streaming); full-file delivery is too slow at the volume |
| **CDC / replication** | Database change-data-capture streamed from a source DB | Source is a transactional DB; need low-latency or row-level deletes captured | Nobody can grant log access or own the replication on the source side; a daily snapshot meets the SLA |
| **Streaming ingest** | Continuous event stream consumed to raw | True real-time events; high volume; append-mostly | The consumer reads daily — "real-time" that's really faster batch |
| **Push / webhook** | Source pushes events to an endpoint you expose | Source controls cadence; bursty; you can't poll | You can't replay missed deliveries, or can't run an always-on endpoint |

Every ingestion pattern shares a **common load block**: landing zone (raw
stays raw — no typing or logic) → completeness check against the source's
manifest or receipt → managed ingest into the raw/warehouse layer, with
archiving and failed-row routing. Types and the data contract are applied
later, in staging. Capture per-source delta cadence, delete semantics, and
replay/backfill behaviour here (see skill Step 1).

## Stage 2 — Transformation (raw → modelled)

| Pattern | Shape | Use when | Don't use when |
|---|---|---|---|
| **ELT in-warehouse (modular SQL)** | Layered models (staging → intermediate → marts) in the warehouse | Default. Transformation logic lives in version-controlled SQL models | The work is a single throwaway extract with no reuse |
| **WAP (write-audit-publish)** | Write to a staging table, run audits, publish only on pass | Correctness-critical data; you must never expose a bad batch | Never skip it for tier 1; for tier 3 exploration it can be overkill |
| **SCD2 historization** | New row per change, validity interval, current flag | Consumers need point-in-time / "as it was when…" answers | Only current state matters, or the need is "what was known at processing time" (that's bi-temporal) |
| **Snapshot / accumulating** | Periodic full snapshots or accumulating fact | History from a source that only gives current state | You need exact change times, or the entity count × periods makes storage the problem |

## Stage 3 — Delivery (modelled → consumer)

| Pattern | Shape | Use when | Don't use when |
|---|---|---|---|
| **Direct query / view** | Consumers read curated views/marts directly | Analysts on SQL; BI tools | The consumer is a system that needs a fixed contract and delivery receipt |
| **Extract / export** | Generate a file or push to a downstream system | Downstream app, vendor, or regulator needs a feed | Consumers could query directly — every extract is a copy to secure and reconcile |
| **Notification / event** | Emit an event/notification on completion or condition | Trigger downstream jobs; alert on landing | Nothing acts on it — an unread notification is noise |
| **Reverse ETL** | Push curated data back into an operational system | Operational consumers (CRM, marketing) need the modelled result | The operational system can't take updates idempotently, or no one owns the sync |

---

## Writing a pattern entry

The tables above are the short form. When a pattern earns a place in your
team's bank, give it a one-page entry with these fields:

* **Name** — short and specific ("SFTP file ingestion").
* **What it solves** — one sentence.
* **Use when / don't use when** — the second is the part most documentation
  skips, and often the most valuable.
* **Basic shape** — three to six stages, not an implementation guide.
* **Known variants** — what changes between situations, without a separate
  entry for each.
* **Hands over / needs to start** — what it produces for the next pattern,
  and what must exist before work on it can start. This is where work stalls.
* **Validated by** — which test closes it out, and with what data:
  fabricated rows in unit tests only, real production history for business
  validation, and any synthetic scenario created through the source's own
  test environment, never hand-inserted into the warehouse.
* **Effort signal** — known (with effort history), known with caveats, or
  novel.

For example, *direct file ingestion*: solves landing scheduled files from an
external source. Use when the source delivers files and transformation runs
once the file is confirmed complete; don't use when events need real-time
processing. Shape: file arrives → trigger fires → completeness check against
the manifest → copied to landing untyped → staging applies types and audit
columns. Hands over a typed staging table, the manifest reconciliation
result, and a note of quarantined rows; needs the drop location, credentials,
a sample file, and a named source contact. Validated by the manifest check,
row counts reconciled to source, and staging types asserted against the
contract. Effort: known — flag it if the source sends no delivery receipt.

## Sequencing into day-sized work

Group the recipe's tasks into themed stories of about one effort-day each, at
most five per slice. Effort isn't calendar time: waiting accumulates at the
seams between stories (reviews, batch windows, other teams, sign-offs), so
estimate it separately. Typical shape for an ingestion-led pipeline (adjust to
the recipe and engineer level):

* **Story 1 · Environment & Access Setup** — IAM/roles, secrets, landing zone.
* **Story 2 · Ingest Build & Ship to Production** — the chosen ingestion
  pattern end to end, deployed. Data ships before code: transformation doesn't
  start until real batches land where production builds can see them. The
  wait for those batches is a seam.
* **Story 3 · Transformation & Data Quality** — models + WAP/DQ checks,
  validated on real production history (fabricated rows belong in unit tests
  only).
* **Story 4 · Delivery & Notification** — the chosen delivery pattern + alerts.
* **Story 5 (heavier patterns) · Hardening & Hypercare** — replication/CDC
  setup and prod cadence, then a hypercare window.

A senior engineer may compress stories 1–2; a newer one may split further.
Heavier ingestion (CDC/replication) genuinely needs extra setup time — say so
in the estimate rather than hiding it. Only break a pattern into day-sized
stories once the team has built it before; a novel one starts as a time-boxed
proof of concept.
