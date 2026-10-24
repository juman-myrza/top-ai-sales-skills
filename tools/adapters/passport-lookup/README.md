# File-backed `passport_lookup` Adapter

**Status:** implemented as a local adapter and Hermes plugin. It has unit tests, but it has **not** been verified against the Daniyar VPS or Hermes v0.21.1. No business passport is bundled here.

This is the smallest reliable way to give Daniyar approved product facts without coupling them to the universal sales skills:

```text
versioned JSON passports on the VPS
        ↓
catalog.json points to the current approved version
        ↓
passport_lookup (read-only)
  checks tenant, schema, approval, effective dates, review cycle, file hash
        ↓
only the requested fields + passport_id + version
        ↓
Daniyar's response and handoff state
```

No database, vector search, external knowledge service, or second memory system is required. Honcho remains conversation memory; Discord handoff is unchanged.

---

## 1. Components

| Component | Location on the Daniyar VPS | Owner |
|---|---|---|
| Authoritative passports | `/opt/data/profiles/daniyar/passports/offers/` | You / business owner |
| Current-version pointer | `/opt/data/profiles/daniyar/passports/catalog.json` | Operator publishing a version |
| Schema | `/opt/data/profiles/daniyar/passports/schema/passport.schema.json` | Copied from this repository |
| Adapter and Hermes plugin | `/opt/data/profiles/daniyar/plugins/passport-lookup/` | This repository |
| Universal sales skills | `/opt/data/profiles/daniyar/skills/sales/` | `install.sh` |

The adapter never writes to `skills/sales/`. The skills installer never writes to `passports/` or `plugins/passport-lookup/`.

---

## 2. One-time setup on the VPS

Run these steps yourself on the VPS. They are documentation, not actions performed by OpenCode.

### 2.1 Clone the repository

```bash
git clone https://github.com/juman-myrza/top-ai-sales-skills.git
cd top-ai-sales-skills
```

### 2.2 Create the persistent store

```bash
export DANIYAR_HOME=/opt/data/profiles/daniyar
export DANIYAR_PASSPORT_ROOT="$DANIYAR_HOME/passports"
export DANIYAR_TENANT_ID=daniyar

mkdir -p "$DANIYAR_PASSPORT_ROOT"/{schema,offers,incoming}
cp product-passport/passport.schema.json \
  "$DANIYAR_PASSPORT_ROOT/schema/passport.schema.json"
```

`catalog.json` is created and updated by `publish`; you do not need to write it by hand. Do **not** copy `product-passport/catalog.example.json` — it contains placeholder offer IDs for illustration only (see the shape below). `incoming/` is optional staging space; the adapter never reads it.

`catalog.json` shape after publishing one offer:

```json
{
  "tenant_id": "daniyar",
  "offers": {
    "ai-agent-training": {
      "passport_id": "ai-agent-training",
      "current_version": "1.0.0",
      "file": "offers/ai-agent-training/1.0.0.json",
      "sha256": "<64-char lowercase sha256>"
    }
  },
  "updated_at": "2026-10-24T12:00:00+00:00"
}
```

### 2.3 Install the plugin files

```bash
mkdir -p "$DANIYAR_HOME/plugins"
cp -a tools/adapters/passport-lookup "$DANIYAR_HOME/plugins/"
```

The plugin declares `jsonschema` in `plugin.yaml`. Hermes may ask for consent before installing it. Do not install dependencies globally just to bypass that review.

### 2.4 Configure the profile

Add these non-secret settings to the Daniyar profile's `.env` (edit the existing file; do not replace it):

```dotenv
DANIYAR_PASSPORT_ROOT=/opt/data/profiles/daniyar/passports
DANIYAR_TENANT_ID=daniyar
```

Then enable the plugin and its toolset only for Daniyar:

```bash
hermes -p daniyar plugins enable passport-lookup
hermes -p daniyar tools
```

In the tool UI, enable `passport` for Discord and for any test chat surface Daniyar uses. If editing `toolsets` in `config.yaml` instead, **add** `passport` to the existing list; do not replace the current toolsets.

### 2.5 Add the operator-level integration note

Add this to Daniyar's operator prompt/config, not to the universal skills:

```text
For product-specific facts, use the passport_lookup tool, which implements the
repository's passport.lookup contract. Use resolve when the offer is unclear,
then lookup only the fields needed for the current answer. Do not read raw
passport files or use conversation memory as a substitute for a fresh lookup.
If the tool returns an error or an unknown field, say you cannot confirm the
fact and offer the documented human path.
```

This note contains no product names, prices, or file locations.

---

## 3. Publishing a passport

For this simple store, `passport_id`, `offer.id`, the catalog key, and the `offers/<offer_id>/` directory name must be the same identifier. The Daniyar drafts in this repository use:

- `ai-agent-implementation` — [`../../../tenants/daniyar/passports/offers/ai-agent-implementation/1.0.0.json`](../../../tenants/daniyar/passports/offers/ai-agent-implementation/1.0.0.json)
- `ai-agent-training` — [`../../../tenants/daniyar/passports/offers/ai-agent-training/1.0.0.json`](../../../tenants/daniyar/passports/offers/ai-agent-training/1.0.0.json)

Both are `draft`, so `publish` refuses them until the owner resolves the open items and sets `status: approved` with `approved_by`, `approved_at`, and `effective_from`.

A version file must be named `offers/<offer_id>/<version>.json`, and its internal `version` must match the filename.

Validate first:

```bash
python3 tools/adapters/passport-lookup/passport_lookup.py \
  --root "$DANIYAR_PASSPORT_ROOT" \
  --tenant-id daniyar \
  validate --offer-id ai-agent-training --version 1.0.0
```

Publish only after your business approval:

```bash
python3 tools/adapters/passport-lookup/passport_lookup.py \
  --root "$DANIYAR_PASSPORT_ROOT" \
  --tenant-id daniyar \
  publish --offer-id ai-agent-training --version 1.0.0
```

`publish`:

1. validates JSON Schema and approval/effective-window rules;
2. checks `passport_id`, `offer.id`, and version consistency;
3. computes the file hash;
4. atomically updates `catalog.json`;
5. leaves previous versions untouched.

If validation fails, the catalog is not changed. No Hermes restart is needed because the adapter reads the current files on each call.

---

## 4. Using the lookup

### Resolve available offers

```bash
python3 tools/adapters/passport-lookup/passport_lookup.py \
  --root "$DANIYAR_PASSPORT_ROOT" \
  --tenant-id daniyar lookup <<'JSON'
{"operation": "resolve"}
JSON
```

The response contains offer IDs, names, one-liners, fulfillment modes, and versions. It does not dump pricing or the whole passport.

### Read selected fields

```bash
python3 tools/adapters/passport-lookup/passport_lookup.py \
  --root "$DANIYAR_PASSPORT_ROOT" \
  --tenant-id daniyar lookup <<'JSON'
{
  "operation": "lookup",
  "offer_id": "ai-agent-training",
  "locale": "ru",
  "requested_fields": [
    "pricing.plans",
    "pricing.currency",
    "pricing.tax_behavior",
    "fulfillment.mode"
  ]
}
JSON
```

### Read authority limits

```bash
python3 tools/adapters/passport-lookup/passport_lookup.py \
  --root "$DANIYAR_PASSPORT_ROOT" \
  --tenant-id daniyar lookup <<'JSON'
{"operation": "authority", "offer_id": "ai-agent-implementation"}
JSON
```

The Hermes tool name is `passport_lookup` (underscore). It is the implementation of the repository's logical `passport.lookup` contract.

---

## 5. Changing a price or policy without reinstalling skills

1. Create a new version, for example `offers/ai-agent-training/1.1.0.json`.
2. Update its internal `version`, `metadata.changelog`, and approval metadata.
3. Run `validate`.
4. Run `publish`.
5. Confirm the response reports `version: "1.1.0"`.

Rollback is the same operation against the older file:

```bash
python3 tools/adapters/passport-lookup/passport_lookup.py \
  --root "$DANIYAR_PASSPORT_ROOT" \
  --tenant-id daniyar \
  publish --offer-id ai-agent-training --version 1.0.0
```

This changes only the catalog pointer. It does not delete the newer file and does not reinstall or rebuild any skill.

---

## 6. Skill upgrades and uninstalls

The lifecycles are independent:

```bash
# Skills only
./install.sh --target /opt/data/profiles/daniyar --apply

# Data only
python3 tools/adapters/passport-lookup/passport_lookup.py \
  --root /opt/data/profiles/daniyar/passports \
  publish --offer-id ai-agent-training --version 1.1.0
```

`install.sh` touches `skills/sales/` and its activation files, not `passports/` or `plugins/passport-lookup/`. `uninstall.sh` likewise leaves the persistent store and plugin data alone.

If a real passport was previously edited inside an installed skill's `references/shared/product-passport/`, move it to the persistent store **before** running an upgrade with `--force`.

---

## 7. Failure behavior

| Situation | Adapter result | Required agent behavior |
|---|---|---|
| Offer or file missing | `not_found` | Do not quote; clarify the offer or offer a human |
| Draft | `not_found` | Do not use it |
| Expired/revoked/outside review cycle | `expired` | Do not use it; request re-approval |
| Invalid JSON/schema/approval metadata | `invalid_request` | Do not publish or quote; keep the previous approved version |
| Catalog/file/version/hash mismatch | `conflict` | Do not choose silently; restore or re-publish |
| Unknown field | `invalid_request` | Do not guess |
| `tools`, metadata, or `privacy.legal_basis` requested | `forbidden` | Do not expose restricted data |
| Different tenant or path escape | `forbidden` | Refuse the request |
| Adapter unavailable | `unavailable` | Say the fact cannot be confirmed; offer the human path |

Proof cases and testimonials with `permission: nda` or `unknown` are filtered out. `tools` and internal metadata are never returned as product content.

---

## 8. Tests and checks

Run locally from this repository:

```bash
python3 scripts/test_passport_lookup.py
python3 scripts/validate_repository.py
```

The adapter tests cover: two-offer selection, selected fields, authority-only reads, draft/expired/revoked refusal, missing approver, tenant isolation, path traversal, hash mismatch, atomic publish, and history preservation. Responses are also validated against the shared tool-envelope schema.

Validate the Hermes plugin package in an isolated Hermes home:

```bash
HERMES_HOME=/tmp/opencode/passport-plugin-check \
  hermes plugins validate tools/adapters/passport-lookup
```

On the VPS, repeat that validation against the actual Hermes v0.21.1 installation before enabling the plugin for buyers.

---

## 9. Deliberate limits

- No live VPS integration has been run from this repository.
- No claim is made that Daniyar already reads the passports.
- No cache is used; correctness and simple updates take priority over optimization.
- The adapter does not prove business truth. Your approval process does that.
- A profile-scoped plugin is not an OS security sandbox. Use normal filesystem permissions for the store and keep its commercial data non-secret.
- Conversation memory is never authoritative for current price, availability, refund terms, or policy.
