# Data Vault Template

Tool-agnostic DDL/load skeletons for the three Data Vault 2.0 structures, plus
the business-key checklist. Substitute your engine's syntax and hash function
(consult `docs/agents/platform.md` if present). Use the business-key names
defined in `CONTEXT.md`.

Standard metadata columns on every structure:
- `load_date` — when this row was loaded (audit)
- `record_source` — which source system / feed it came from (audit/lineage)
- hash columns — see each structure below

Replace `{{hash_fn}}` with `MD5` / `SHA2` / `FARM_FINGERPRINT` etc.

---

## Business-key checklist (do this before any DDL)

- [ ] The key is **business-meaningful** and stable over time (customer number,
      VIN, order code) — not a source surrogate/sequence that can be reassigned.
- [ ] It's truly unique for the entity (confirm with `profile-data` if installed).
- [ ] It survives across source systems (or you'll need a same-as link to
      reconcile in the business vault).
- [ ] You've decided the hashing input: trim, upcase, and concatenate
      multi-part keys with a consistent separator so the same key always hashes
      the same.

---

## Hub — the list of unique business keys

No descriptive attributes. Stable forever.

```sql
CREATE TABLE hub_customer (
  customer_hk     CHAR(32)    NOT NULL,   -- hash of the business key (PK)
  customer_bk     VARCHAR     NOT NULL,   -- the business key itself
  load_date       TIMESTAMP   NOT NULL,
  record_source   VARCHAR     NOT NULL
);

-- load: insert only keys not already present
INSERT INTO hub_customer (customer_hk, customer_bk, load_date, record_source)
SELECT DISTINCT
  {{hash_fn}}(UPPER(TRIM(s.customer_number))) AS customer_hk,
  s.customer_number                           AS customer_bk,
  CURRENT_TIMESTAMP,
  'crm'
FROM staging_customer s
LEFT JOIN hub_customer h ON h.customer_hk = {{hash_fn}}(UPPER(TRIM(s.customer_number)))
WHERE h.customer_hk IS NULL;
```

---

## Link — a relationship between hubs

The related hub hash keys + its own hash key. No descriptive attributes. Can
connect more than two hubs.

```sql
CREATE TABLE lnk_customer_order (
  customer_order_hk  CHAR(32)   NOT NULL,  -- hash of the combined business keys (PK)
  customer_hk        CHAR(32)   NOT NULL,  -- FK to hub_customer
  order_hk           CHAR(32)   NOT NULL,  -- FK to hub_order
  load_date          TIMESTAMP  NOT NULL,
  record_source      VARCHAR    NOT NULL
);

-- load: insert only relationships not already present
INSERT INTO lnk_customer_order
SELECT DISTINCT
  {{hash_fn}}(CONCAT_WS('||', UPPER(TRIM(s.customer_number)), UPPER(TRIM(s.order_code)))),
  {{hash_fn}}(UPPER(TRIM(s.customer_number))),
  {{hash_fn}}(UPPER(TRIM(s.order_code))),
  CURRENT_TIMESTAMP,
  'oms'
FROM staging_order s
LEFT JOIN lnk_customer_order l
  ON l.customer_order_hk =
     {{hash_fn}}(CONCAT_WS('||', UPPER(TRIM(s.customer_number)), UPPER(TRIM(s.order_code))))
WHERE l.customer_order_hk IS NULL;
```

---

## Satellite — descriptive, time-variant attributes

Insert-only. A new row when the `hash_diff` of the tracked attributes changes.
This is where history lives. Hang it off a hub OR a link.

```sql
CREATE TABLE sat_customer_details (
  customer_hk     CHAR(32)    NOT NULL,   -- FK to hub_customer
  load_date       TIMESTAMP   NOT NULL,   -- (customer_hk, load_date) = PK
  hash_diff       CHAR(32)    NOT NULL,   -- hash of the descriptive columns
  record_source   VARCHAR     NOT NULL,
  -- descriptive, time-variant attributes --
  customer_name   VARCHAR,
  segment         VARCHAR,
  email           VARCHAR
);

-- load: insert a new version only when the attributes actually changed
INSERT INTO sat_customer_details
SELECT
  {{hash_fn}}(UPPER(TRIM(s.customer_number)))            AS customer_hk,
  CURRENT_TIMESTAMP                                       AS load_date,
  {{hash_fn}}(CONCAT_WS('||',
    COALESCE(s.customer_name,'^^'),
    COALESCE(s.segment,'^^'),
    COALESCE(s.email,'^^')))                             AS hash_diff,
  'crm', s.customer_name, s.segment, s.email
FROM staging_customer s
LEFT JOIN (
  -- newest version currently in the satellite per key
  SELECT customer_hk, hash_diff,
         ROW_NUMBER() OVER (PARTITION BY customer_hk ORDER BY load_date DESC) AS rn
  FROM sat_customer_details
) cur
  ON cur.customer_hk = {{hash_fn}}(UPPER(TRIM(s.customer_number))) AND cur.rn = 1
WHERE cur.customer_hk IS NULL                              -- first load
   OR cur.hash_diff <> {{hash_fn}}(CONCAT_WS('||',
        COALESCE(s.customer_name,'^^'),
        COALESCE(s.segment,'^^'),
        COALESCE(s.email,'^^')));                          -- changed
```

> COALESCE NULLs to a sentinel (`'^^'`) so `NULL` and `''` don't collide in the
> hash_diff. Tip: keep the business key in at least one satellite so you can
> debug a hash.

---

## Raw vault vs business vault

- **Raw Vault** — the hubs/links/satellites above. No business rules; only key
  hashing and change detection. Must be fully reloadable from source at any time.
- **Business Vault** — additive layer on top: same-as links (dedupe a customer
  across sources), computed satellites, and PIT/bridge tables for query
  convenience. Business logic lives here, separate from raw and from the marts.

### PIT (point-in-time) table — query helper in the business vault

```sql
-- snapshot of which satellite version is in effect per key per snapshot date,
-- so downstream queries avoid as-of joins across many satellites
CREATE TABLE pit_customer (
  customer_hk           CHAR(32)   NOT NULL,
  snapshot_date         DATE       NOT NULL,
  sat_details_load_date TIMESTAMP,            -- pointer into sat_customer_details
  sat_address_load_date TIMESTAMP             -- pointer into sat_customer_address
);
```

---

## Then build marts on top

Data Vault is the **integration layer**, not the presentation layer. Build
Kimball stars on top for consumers (see `dimensional-modeling` if installed).

## Anti-patterns to call out

- Descriptive columns on a hub or link — they belong in a satellite.
- Skipping the business vault and smearing business logic across mart views.
- Over-debating hash algorithm choice instead of shipping.
- Hubs built on a source surrogate/sequence instead of a real business key.
