# Tenant Business Data

This directory holds tenant-specific product passports as a **mirror** of the profile's authoritative store. It is deliberately outside `product-passport/`, because `product-passport/` is bundled into every installed skill while tenant business data must not be.

```text
tenants/<tenant>/passports/
├── schema/passport.schema.json          # byte-identical to product-passport/passport.schema.json
├── offers/<offer_id>/<version>.json     # one versioned passport per offer
├── catalog.json                         # the published-offer pointer the adapter reads
└── MIRROR.sha256                        # recorded SHA-256 for every file above
```

Rules:

- The **profile is authoritative** for `passports/**`. The `catalog.json` and the offer files in the profile's persistent store (for Daniyar: `/opt/data/profiles/daniyar/passports/`) are the source of truth; this directory is a synced mirror.
- No installer step may copy into or overwrite the profile's `passports/**`, `catalog.json`, or `state/`. `install_skills.py` bundles only `core, tools, product-passport, research`; `tenants/` is not in that list, and `test_installed_artifact.py` asserts that an install creates no `passports/`, `state/`, or `tenants/` in the target.

## Drift check (why `MIRROR.sha256` exists)

`scripts/validate_repository.py` (`check_tenant_passports`) enforces two things so the mirror cannot silently describe a different business reality:

1. **Internal consistency.** `catalog.json` must list exactly the offer files present, and each entry's `sha256` must equal the offer file on disk. Editing an offer without updating `catalog.json` fails the check.
2. **Recorded provenance.** Every file listed in `MIRROR.sha256` must match its recorded SHA-256. Editing either an offer or `catalog.json` without refreshing `MIRROR.sha256` fails with a "mirror drifted; re-sync from the profile" error.

`MIRROR.sha256` is a plain `sha256sum` list (`<hash>  <path>`) relative to this `passports/` directory.

## Current mirror

| File | Notes |
|---|---|
| `offers/ai-agent-implementation/1.0.0.json` | approved; matches the profile byte-for-byte |
| `offers/ai-agent-training/1.0.0.json` | approved; matches the profile byte-for-byte |
| `schema/passport.schema.json` | byte-identical to the repository schema |
| `catalog.json` | generated in the adapter's shape from the two offers |

The two offers are the profile's **approved** revision (calendar `juman.kg.agent@gmail.com`, 15-minute meeting length carried in `fulfillment.booking.duration_minutes`, booking tools marked `implemented`). Facts inside them still carry explicit statuses (`verified` / `estimated` / `unknown`) and open decisions stay in `unresolved`.

## Sync

The profile is authoritative. After changing passports or `catalog.json` in the profile (via the adapter's `publish`), mirror them here and refresh the recorded hashes:

```bash
# On the VPS, after publishing in the profile store
export STORE=/opt/data/profiles/daniyar/passports
cp -a "$STORE/offers/."            tenants/daniyar/passports/offers/
cp -a "$STORE/catalog.json"        tenants/daniyar/passports/catalog.json
cp -a "$STORE/schema/passport.schema.json" tenants/daniyar/passports/schema/passport.schema.json

# then refresh the recorded SHA-256 (repo side)
cd tenants/daniyar/passports
{ sha256sum catalog.json; sha256sum offers/*/*.json; sha256sum schema/passport.schema.json; } > MIRROR.sha256
```

> Note on `catalog.json`: the profile's file carries an `updated_at` publish timestamp, so its bytes (and therefore its recorded hash) change on every publish. The copy here is generated in the adapter's shape; after a sync from the profile, refresh `MIRROR.sha256` so it matches the profile's file exactly.

An unapproved (`draft`) passport is not served by the adapter. To release a new offer: resolve the relevant `unresolved` entries, set `status: approved` with `approved_by`, `approved_at`, and `effective_from`, then `validate` and `publish`.
