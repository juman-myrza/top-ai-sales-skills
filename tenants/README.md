# Tenant Business Data (Source Drafts)

This directory holds **tenant-specific product passports as source drafts**. It is deliberately outside `product-passport/`, because `product-passport/` is bundled into every installed skill while tenant business data must not be.

```text
tenants/<tenant>/passports/
├── offers/<offer_id>/<version>.json     # one versioned passport per offer
└── (schema/ and catalog.json are added by the deployment step)
```

Rules:

- The **authoritative** copy lives in the Hermes profile's persistent store (for Daniyar: `/opt/data/profiles/daniyar/passports/`), not in this repository.
- This directory is for authoring and review. Deploying it is a copy, then `publish`, on the host.
- Passports here stay `draft` until the owner approves the open commercial decisions. The adapter refuses to serve a `draft`.
- The installer never touches this directory, and this directory is never bundled into a skill.

## Daniyar draft passports

| Offer | File | Status |
|---|---|---|
| AI Agent Development & Business Process Automation | [`daniyar/passports/offers/ai-agent-implementation/1.0.0.json`](daniyar/passports/offers/ai-agent-implementation/1.0.0.json) | draft |
| Practical AI Agents & Automation Training | [`daniyar/passports/offers/ai-agent-training/1.0.0.json`](daniyar/passports/offers/ai-agent-training/1.0.0.json) | draft |

Both drafts distinguish three fact states:

- `verified` — supplied by the business owner in the brief (for example the 35,000 KGS implementation fee and the 10,000 KGS monthly support);
- `estimated` — preliminary or intended, not approved (for example the ~100,000 KGS course price and the up-to-three-month support);
- `unknown` — not decided or not supplied (for example tax treatment, payment methods, refunds, and service hours).

Open decisions are listed in each passport's `unresolved` array. The introductory 25,000 KGS price is recorded but flagged: the source brief was internally inconsistent (one section said its conditions were unapproved, another resolved it to the first three customers).

## Deploy to the running agent

```bash
# On the VPS
export DANIYAR_HOME=/opt/data/profiles/daniyar
export DANIYAR_PASSPORT_ROOT="$DANIYAR_HOME/passports"
export DANIYAR_TENANT_ID=daniyar

mkdir -p "$DANIYAR_PASSPORT_ROOT/offers"
cp -a tenants/daniyar/passports/offers/. "$DANIYAR_PASSPORT_ROOT/offers/"
```

Then follow [`../tools/adapters/passport-lookup/README.md`](../tools/adapters/passport-lookup/README.md) to copy the schema, configure the plugin, and `validate`/`publish` once the owner approves.

A draft cannot be published. To release an offer, the owner must:

1. resolve the relevant `unresolved` entries;
2. set the passport `status` to `approved`, and set `approved_by`, `approved_at`, and `effective_from`;
3. re-run `validate` and then `publish`.
