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
| `offers/ai-agent-implementation/3.0.1.json` | current approved GitHub mirror revision; runtime publication to Daniyar's profile is separate |
| `offers/ai-agent-training/3.0.1.json` | current approved GitHub mirror revision; runtime publication to Daniyar's profile is separate |
| `schema/passport.schema.json` | byte-identical to the repository schema |
| `catalog.json` | points to the current approved 3.0.1 versions |

The v3.0.1 passports align with Business Strategy & Execution Plan v1.1. The implementation passport exposes only the approved Starter, Business and Enterprise starting prices; preliminary Care ranges are not quoteable plans. The Academy passport contains the approved two-month format, 50,000 KGS price, six-month video access and free repeat participation in later cohorts. Automated outbound follow-up is disabled until a separate cadence is approved. Tax/legal/refund terms, cohort-specific dates and prerequisites, and other owner-controlled items remain explicitly listed in `unresolved`; Daniyar must not guess or promise them.

The GitHub mirror is **not** the authoritative runtime store. Tool bindings retain `not_implemented` or `degraded` where no verified runtime integration exists. Daniyar will not read these revisions until the same files are copied into `/opt/data/profiles/daniyar/passports/`, validated and published with the adapter. A passport status of `approved` does not mean the items listed in `unresolved` have been supplied; it means the published facts and safe agent boundaries are owner-approved.

## Sync

The profile is authoritative. The repository mirror currently points to passport version `3.0.1` for both Daniyar offers. From a checked-out repository on the VPS, copy the versioned files and schema into the persistent profile store, then validate and publish each offer:

```bash
cd /path/to/top-ai-sales-skills

export DANIYAR_PASSPORT_ROOT=/opt/data/profiles/daniyar/passports
mkdir -p "$DANIYAR_PASSPORT_ROOT"/{schema,offers}

cp -a tenants/daniyar/passports/offers/. "$DANIYAR_PASSPORT_ROOT/offers/"
cp product-passport/passport.schema.json "$DANIYAR_PASSPORT_ROOT/schema/passport.schema.json"

python3 tools/adapters/passport-lookup/passport_lookup.py \
  --root "$DANIYAR_PASSPORT_ROOT" --tenant-id daniyar \
  validate --offer-id ai-agent-implementation --version 3.0.1

python3 tools/adapters/passport-lookup/passport_lookup.py \
  --root "$DANIYAR_PASSPORT_ROOT" --tenant-id daniyar \
  validate --offer-id ai-agent-training --version 3.0.1

python3 tools/adapters/passport-lookup/passport_lookup.py \
  --root "$DANIYAR_PASSPORT_ROOT" --tenant-id daniyar \
  publish --offer-id ai-agent-implementation --version 3.0.1

python3 tools/adapters/passport-lookup/passport_lookup.py \
  --root "$DANIYAR_PASSPORT_ROOT" --tenant-id daniyar \
  publish --offer-id ai-agent-training --version 3.0.1
```

Before publication, review each passport's `unresolved` list. These entries must not be filled by guessing. The current approved passports already contain fail-closed rules so Daniyar does not quote unsupported terms, claim unavailable integrations, or promise legal/tax/refund details. If an unresolved item becomes necessary for a particular customer's proposal, pause that promise and obtain owner/accountant/technical approval first.

After the runtime profile has published both offers, sync the authoritative files and catalog back into this GitHub mirror and refresh its hashes:

```bash
export STORE=/opt/data/profiles/daniyar/passports
cp -a "$STORE/offers/." tenants/daniyar/passports/offers/
cp -a "$STORE/catalog.json" tenants/daniyar/passports/catalog.json
cp -a "$STORE/schema/passport.schema.json" tenants/daniyar/passports/schema/passport.schema.json

cd tenants/daniyar/passports
{ sha256sum catalog.json; sha256sum offers/*/*.json; sha256sum schema/passport.schema.json; } > MIRROR.sha256
```

> Note on `catalog.json`: the profile's file carries an `updated_at` publish timestamp, so its bytes (and therefore its recorded hash) change on every publish. The copy here is generated in the adapter's shape; after a sync from the profile, refresh `MIRROR.sha256` so it matches the profile's file exactly.

An unapproved (`draft`) passport is not served by the adapter. To release a new offer: resolve the relevant `unresolved` entries, set `status: approved` with `approved_by`, `approved_at`, and `effective_from`, then `validate` and `publish`.
