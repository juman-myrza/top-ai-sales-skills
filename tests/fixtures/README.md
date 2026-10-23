# Test Fixtures

The scenarios use two kinds of fixtures:

1. **Fictional passports** in [`../../product-passport/examples/`](../../product-passport/examples/).
2. **Inline tool results** in each scenario's `fixtures:` block.

There are no recorded real customer conversations, credentials, or provider payloads in this directory.

---

## Passport fixtures

| Fixture ID | File | Use |
|---|---|---|
| `direct-sale-nimbus-notes` | [`direct-sale-nimbus-notes.json`](../../product-passport/examples/direct-sale-nimbus-notes.json) | Direct purchase, invoice, discount authority, proof permissions |
| `appointment-karkyra-consult` | [`appointment-karkyra-consult.json`](../../product-passport/examples/appointment-karkyra-consult.json) | In-chat booking, availability, no-show, free consultation |
| `consumer-course-example` | [`consumer-course-example.json`](../../product-passport/examples/consumer-course-example.json) | B2C direct purchase, consumer pricing, scoped refusal, adoption objection |

All are marked `metadata.fictional: true`. Do not treat their prices, proofs, or policies as real.

---

## Inline tool fixtures

A scenario declares what the harness should return:

```yaml
fixtures:
  - tool: calendar.booking
    operation: create
    status: conflict
    note: "The chosen slot was taken."
```

These are **test doubles**, not implementations. A fixture does not prove that a calendar provider exists or that the adapter handles the real error correctly.

---

## Response smoke fixture

[`smoke-responses.jsonl`](smoke-responses.jsonl) contains three hand-written responses used to verify that `scripts/evaluate_responses.py` accepts a correct record and rejects a broken one. It is **not** model output, not a score, and not evidence that any scenario passes in production. Run it with `--allow-partial`; the other 53 scenarios are intentionally absent. `scripts/test_checker.py` adds must-pass and must-fail cases, including the wrong-price, false-confirmation, and negated-refusal defects found in the audit.

### Fixture rules

- Use the envelope status vocabulary from [`../../tools/README.md`](../../tools/README.md).
- Include an `operation` when the contract has more than one.
- Keep notes short and free of PII.
- A fixture with `status: confirmed` must not be used to claim a live integration.
- A failure fixture must specify the failure mode the agent is expected to handle.
- Do not add a fixture for a tool the scenario does not exercise.

---

## Adding a fixture

1. Prefer the existing passports unless the scenario tests a new business rule.
2. If a new passport is needed, copy an example, mark it fictional, and validate it.
3. Keep tool data minimal; the scenario checks behavior, not provider fidelity.
4. Add the scenario to [`../COVERAGE.md`](../COVERAGE.md).
5. Run `python3 scripts/validate_repository.py`.

---

## What is deliberately absent

- Real customer names, phone numbers, emails, or addresses.
- Real card numbers or bank accounts.
- Real calendar IDs or meeting links.
- Provider API keys.
- Recorded production transcripts.
- A live adapter.

The `.example.invalid` domain is reserved and cannot resolve, which makes accidental real contact unlikely.
