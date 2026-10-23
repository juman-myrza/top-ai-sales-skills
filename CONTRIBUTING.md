# Contributing

Thanks for improving the repository. The goal is a sales skill set that stays truthful, consent-based, testable, and reusable across businesses. Contributions that make the demo more persuasive by weakening those properties will be rejected.

---

## Before you start

1. Read the [Core Behavior Contract](core/CORE-BEHAVIOR-CONTRACT.md) and [Conflict Resolution](core/CONFLICT-RESOLUTION.md).
2. Read [tests/README.md](tests/README.md) to understand what the tests do and do not prove.
3. Check [research/decisions-and-tradeoffs.md](research/decisions-and-tradeoffs.md) so you do not reopen a settled decision without new evidence.

---

## Hard rules

### No business facts in skills

Skills under `skills/sales/` must not contain:

- a company or product name from a real business;
- a price, currency amount, discount, tax rate, or payment term;
- an audience definition tied to one market;
- inventory, delivery time, calendar availability, or a booking link;
- a customer name, logo, case study, testimonial, award, or certification;
- a guarantee, warranty, or legal claim;
- a hardcoded escalation contact or SLA.

Put facts in a product passport. Put behavior in a skill. The validator rejects fictional example brands and concrete currency amounts in skill files; human review must catch the rest.

### Never weaken these

- truth classes and the ban on fabricated facts;
- consent before booking, charging, data sharing, or follow-up;
- the stop rule after refusal or opt-out;
- tool verification before claiming completion;
- privacy and data minimization;
- the conditional escalation triggers;
- the prohibition on fake identity, fake delays, and manufactured scarcity.

A change that weakens one of these needs an explicit architecture decision, not just a pull request.

### Do not add fake integrations

Contracts and schemas belong in `tools/`. Do not add a mock adapter that returns success and makes the repository look connected. If you implement a real adapter, add contract tests, failure tests, and documentation of credentials and data flow.

---

## Adding or changing a skill

1. Use the directory name as the YAML `name`; use lowercase letters, digits, and hyphens.
2. Keep `description` at **60 characters or fewer**, including spaces. Hermes truncates longer descriptions in its prompt.
3. Include the required sections in order:
   `## When to Use`, `## When Not to Use`, `## Required Inputs`, `## Procedure`, `## Branches`, `## Stopping Conditions`, `## Failure Recovery`, `## Examples`, `## Counterexamples`, `## Dependencies`, `## Sources`.
4. Keep the body under the 24,000-character soft budget.
5. Put long reference material in `references/` and link it from the skill.
6. Add at least one counterexample for every new tactic.
7. Trace every non-obvious claim to `research/source-register.md` or label it as a repository decision.

Run:

```bash
python3 scripts/validate_repository.py
python3 scripts/test_hermes_loading.py
```

---

## Adding a scenario

Scenarios live in [`tests/scenarios/`](tests/scenarios/). Follow [`tests/SCENARIO-FORMAT.md`](tests/SCENARIO-FORMAT.md).

A useful scenario:

- tests one decision, not five at once;
- has a realistic buyer turn and a clear stage;
- states exactly what the agent must and must not do;
- includes a tool fixture when a tool result matters;
- uses `human_review: true` for Kyrgyz or mixed-language cases;
- can fail. If every plausible response passes, the scenario is decoration.

After adding one:

1. update [`tests/COVERAGE.md`](tests/COVERAGE.md);
2. update the expected category counts in `scripts/validate_repository.py` if the corpus size changes;
3. run the validator and, if you have recorded responses, the checker.

### Response records

Do not commit real customer conversations, personal data, or unredacted model output. Use synthetic or fully redacted records under `tests/responses/` (ignored by Git). Label them with the model, date, prompt version, and whether a human reviewed them.

---

## Adding a source

Add a row to [`research/source-register.md`](research/source-register.md) with:

- a stable ID;
- author, title, publisher, year, edition or URL;
- access date and access limits;
- an evidence grade;
- what it is used for and what it cannot support.

Then update [`research/claim-evidence-matrix.md`](research/claim-evidence-matrix.md) if the source changes a claim. Do not cite a vendor page as independent proof. Do not add a source whose main contribution is a manipulation tactic that conflicts with the contract.

---

## Product passport changes

- Bump the version for any material fact change.
- Keep `verified` fields traceable to an approver and date.
- Use `estimated` for derived numbers and show the assumption.
- Use `unknown` rather than inventing a value.
- Re-run schema validation after editing.
- Never put real customer data in the repository's examples.

---

## Language contributions

Russian, Kyrgyz, and mixed-language improvements are welcome. A language change should include:

- the phrase or pattern;
- the context where it is appropriate;
- a counterexample where it is wrong;
- a note on register (formal/informal, regional);
- for Kyrgyz, confirmation from a native speaker before it is marked production-ready.

Do not machine-translate a phrase and present it as reviewed.

---

## Pull request checklist

- [ ] The change preserves truth, consent, privacy, and tool verification.
- [ ] No business facts were added to a skill.
- [ ] New behavior has a scenario, and the scenario can fail.
- [ ] Skills still pass frontmatter, section, and size checks.
- [ ] Links resolve.
- [ ] No secrets, real customer data, or unredacted personal data.
- [ ] `python3 scripts/validate_repository.py` passes.
- [ ] The change is described in `CHANGELOG.md` under **Unreleased**.
- [ ] Claims are labeled as implemented, tested, or aspirational.

---

## Review standard

Reviewers should ask:

1. Could this instruction cause a false statement about a price, proof point, availability, or completed action?
2. Could it pressure a buyer after a refusal?
3. Does it assume a tool succeeded without evidence?
4. Does it hardcode a fact that belongs in a passport?
5. Is the claimed evidence strong enough for the wording?
6. Would the change survive being screenshotted and shown to the buyer's lawyer or regulator?

If the answer to any of the first four is yes, request changes.
