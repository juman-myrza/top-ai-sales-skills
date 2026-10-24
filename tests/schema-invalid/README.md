# Invalid Schema Fixtures

Each file in this directory is a deliberately broken document that the
corresponding schema **must reject**. `scripts/validate_repository.py` validates
every file here and fails if any of them passes.

These fixtures exist because a schema that accepts `"banana"` as an approved
price, a verified fact with a null value, or an approved passport with no
approver does not protect the agent from acting on bad data.

| File | Schema | Defect |
|---|---|---|
| `passport-banana-price.json` | `product-passport/passport.schema.json` | A plan price is a non-numeric string |
| `passport-verified-null.json` | `product-passport/passport.schema.json` | A `verified` fact has a null value |
| `passport-approved-no-approver.json` | `product-passport/passport.schema.json` | `status: approved` with no approver |
| `passport-percent-over-100.json` | `product-passport/passport.schema.json` | A discount percent exceeds 100 |
| `passport-missing-quote-policy.json` | `product-passport/passport.schema.json` | Missing `pricing.quote_policy` |
| `passport-missing-buyer-types.json` | `product-passport/passport.schema.json` | Missing `offer.buyer_types` |
| `state-bare-consent.json` | `core/conversation-state.schema.json` | Consent stored as a bare string |
| `state-bad-handoff-code.json` | `core/conversation-state.schema.json` | A handoff reason code that is not canonical |
| `state-next-step-no-owner.json` | `core/conversation-state.schema.json` | `next_step` without an owner |
| `state-quote-lowercase-currency.json` | `core/conversation-state.schema.json` | A quote currency that is not ISO 4217 uppercase |

Adding a fixture: copy a valid example, introduce one defect, and confirm the
validator reports it. Do not add a fixture that fails for an unrelated reason.
