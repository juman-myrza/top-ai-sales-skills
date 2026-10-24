# Changelog

All notable changes to this repository are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-10-23

First research and structural release. This version is installable as instructions, but it is not a production-ready sales system: no model was evaluated and no tool adapter is connected.

### Added

- Hermes-compatible skill format with nine universal sales skills:
  - `sales-conversation-orchestrator`
  - `sales-qualification`
  - `sales-discovery`
  - `sales-value-proof`
  - `sales-objection-negotiation`
  - `sales-closing-execution`
  - `sales-language-adaptation`
  - `sales-follow-up`
  - `sales-integrity-escalation`
- Core behavior contract covering truth classes, consent, refusal, pressure limits, conversation state, stage model, tool verification, privacy, handoff, and change control.
- Conflict-resolution rules with fixed precedence: safety/consent/legal > truth/permission > passport > skill > persuasion.
- Conversation-state schema and a system-prompt snippet.
- Product passport template, JSON Schema (Draft 2020-12), and two clearly fictional examples:
  - direct-sale digital product (`direct-sale-nimbus-notes`);
  - appointment-based consultation (`appointment-karkyra-consult`).
- Seven tool contracts and a shared request/response envelope:
  - `passport.lookup`
  - `calendar.availability`
  - `calendar.booking`
  - `payments.invoicing`
  - `crm.memory`
  - `human.handoff`
  - `messaging.media`
- 51 evaluation scenarios across eight categories, with a scenario-format specification, rubric, coverage map, and hand-written checker fixture.
- Scripts:
  - `validate_repository.py` — structure, schema, scenario, link, and hardcoding checks;
  - `evaluate_responses.py` — deterministic checks for recorded responses;
  - `render_scenarios.py` — Markdown and JSONL rendering;
  - `test_hermes_loading.py` — isolated `HERMES_HOME` discovery test;
  - `install_skills.py` — dry-run-by-default installer with validation gate and backups.
- Research trail:
  - source register with evidence grades and access limitations;
  - claim-evidence matrix with confidence and falsifiers;
  - architecture decisions and tradeoffs;
  - open-source repository audit.
- Language, follow-up cadence, and escalation reference material.
- CI workflow for static validation and the response-checker smoke test.

### Verified in this release

- `python3 scripts/validate_repository.py` passes all structural checks (warnings may be present for review flags).
- Both fictional passports validate against the passport schema.
- All 51 scenario YAML files parse; IDs are unique and category counts match the coverage document.
- Tool envelope examples validate against the envelope schema.
- All nine skills are discovered by Hermes v0.21.5 in an isolated temporary `HERMES_HOME`. The live profile was not read or modified.
- The response checker passes its hand-written smoke fixture under `--allow-partial`.
- The installer completes a dry run and a real `--apply` into a temporary target, creating all nine skill directories without touching the live profile.

### Known limitations

- No behavioral test against a live language model was run. The scenarios and checker are ready, but no response corpus exists.
- No calendar, payment, CRM, messaging, or human-handoff adapter is implemented. Every example binding is `not_implemented`.
- No native Kyrgyz speaker has reviewed the Kyrgyz and mixed-language examples.
- No jurisdiction-specific legal, privacy, or consumer-protection review was completed.
- No conversion, retention, complaint, or opt-out impact was measured.
- Voice and phone calls are out of scope.
- The Gartner "B2B Buying Journey" page returned HTTP 403 during research; only the 2025 press release was read, and it is treated as vendor research.
- "Top 0.1%" is an aspiration, not a claim supported by this repository.

### Not included

- Model weights, prompts for a specific provider, or a hosted service.
- Real company data, customer data, prices, calendars, or case studies.
- Mock adapters that pretend an integration works.
- Credentials, API keys, webhooks, or deployment automation.
- A guarantee of sales performance, legal compliance, or language quality.

## [0.2.0] — 2026-10-23

Remediation release based on the accepted deep audit (`research/audits/2026-10-23-daniyar-deep-audit.md`). It fixes confirmed defects and contradictions. It does **not** claim improved sales effectiveness; no live model has been evaluated.

### Fixed

- **Installation packaging.** `install_skills.py` now copies the shared `core/`, `tools/`, `product-passport/`, and `research/` documents into each skill under `references/shared/` and rewrites each skill's links to point there. An installed skill no longer loses its core behavior contract, tool contracts, or passport schema. The installer also writes `INSTALL-MANIFEST.json` and `ACTIVATION.md`. A new `scripts/test_installed_artifact.py` verifies a fresh install.
- **Conversation state.** `conversation-state.schema.json` is now `1.1.0`: consent is a per-purpose object with status, time, scope, and source; `mode`, `known_facts`, `diagnosis`, `follow_up`, and `quote` have canonical representations; handoff reason codes match `human.handoff`; tool-result statuses match the tool envelope. `core/example-state.json` is validated by the repository validator.
- **CRM contract.** The documented patch now validates against the canonical state schema. Consent objects, known facts, next steps, quote, and follow-up lifecycle are aligned; the adapter is required to reject schema-invalid patches.
- **Payment execution.** `payments.invoicing` now requires an approved quote ID/version and an exact terms snapshot; the server recomputes and rejects any mismatch. Discounted or custom quotes require an approval reference. Added quote-expiry and discount-authority failure paths.
- **Follow-up scheduling.** `messaging.media` adds `schedule_text`, `cancel_scheduled`, and `get_scheduled`. A scheduled message is explicitly not "sent", and the adapter re-checks consent and opt-out at dispatch. The follow-up skill adds the `buyer_initiated_inquiry` basis and a scheduling lifecycle.
- **Tool names.** Removed the `calendar.check_availability` and `calendar.book` drift; the closing skill uses `calendar.availability` and `calendar.booking`.
- **External-link contradiction.** The core contract, system prompt, closing skill, and conflict resolution now agree: use an approved external link only when the passport explicitly allows it, the exact link is approved, and the buyer agrees. Closing Example 5 no longer claims the in-chat path is "faster".
- **Response checker.** `evaluate_responses.py` now uses digit boundaries for numeric amounts, treats a negated forbidden phrase as a refusal rather than a violation, supports `must_match_regex_all/any`, `required_tool_statuses`, `required_tool_sequence`, and `expected_final_state`, fails a record whose tool status contradicts the scenario fixture, and fails a success claim with no confirming tool result. The P01 scenario now rejects a monthly price of 120 (the annual figure) while accepting the correct monthly 12/96 and annual 120. `scripts/test_checker.py` pins twelve scenario cases and three synthetic terminal-state cases.
- **Scenario renderer.** `render_scenarios.py` omits hidden tool fixtures and the evaluator title from the default JSONL packet, so a responder cannot see the expected outcome before calling a tool. Opt in with `--include-fixtures` / `--include-title` for offline analysis only.
- **Contract conformance.** The validator now checks every documented tool request against the shared envelope, requires the load-bearing params (`quote_id`/`quote_version`/`terms_snapshot`, booking/payment/messaging `consent.status`), rejects the retired `consent.given` shorthand, and merges the documented CRM update patch into the canonical state to prove it validates. The `example-envelopes.json` payment, booking, messaging, and handoff examples were updated to the canonical consent shape.
- **Activation version record.** The install manifest records `shared.core_contract_version`, the system-prompt snippet hash, and hashes of the core contract, state schema, passport schema, and envelope schema, so an evaluation can pin the active versions.
- **Discovery-test fidelity.** `test_hermes_loading.py` now installs through the real installer (shared references, activation block, manifest) instead of copying bare skill directories.
- **Scenario count consistency.** The `human_review` flag count in `COVERAGE.md` was corrected to 18 after the entitlement scenario was added.
- **Follow-up scheduling.** The messaging contract documents replace/cancel semantics: a new schedule for the same follow-up task supersedes the old one, and `cancel_scheduled` cannot retract a sent message.
- **Tool envelope tenant binding.** The response may carry `tenant_id`; the runtime must bind responses to the request it actually sent rather than trusting a model-selected ID.
- **Quote validity.** An open-ended quote (`valid_until: null`) is allowed when the passport documents a review policy, instead of forcing an artificial expiry.
- **Research traceability.** Added the official EU AI Act, official EU GDPR text, and the FTC dark-patterns report to the source register, and replaced the unofficial `gdpr.eu` link in the skills.
- **B2B-only assumption.** Qualification now reads `offer.buyer_types` and `sales_guidance.segments` instead of disqualifying consumers by default; the `audience`/`constraints` phantom fields are replaced with real passport paths.
- **Scoped refusal and correction.** The core contract, orchestrator, and conflict resolution distinguish a refusal of one element ("no call") from a refusal of the offer, and distinguish a buyer correction from a contradiction.

### Added

- Typed commercial values in the passport schema: `moneyFact`, `percentFact`, `integerFact`, and `currencyFact`. A plan price cannot be a non-numeric string; a verified fact cannot have a null value; an approved passport needs an approver and an effective date.
- `sales_guidance` (segments, objection guidance, alternatives), `sales_policy.negotiation` (tradables, non-negotiables, walk-away), `pricing.quote_policy`, `offer.buyer_types`, and case evidence-quality fields (`segment`, `baseline`, `intervention`, `measurement_period`, `limitations`).
- A third fictional passport example, `consumer-course-example`, for a B2C direct purchase.
- A `consumer-direct` scenario category (B01–B04), an adoption-risk scenario (O09), and an entitlement-correction scenario (O10). The corpus is now 57 scenarios in nine categories.
- `required_tool_sequence` and `expected_final_state` checker fields, with `state` on the response record.
- `tests/schema-invalid/` with ten deliberately invalid documents the schemas must reject, checked by the validator.
- Checker semantics documentation, new rubric sub-dimensions (`recommendation`, `barrier`, `progression`), and a behavioral-evaluation design document.
- CI steps for the checker regression test and the installed-artifact test.

### Changed

- All tool contracts and the example passports move to `contract_version` `1.1.0` for consistency with the changed request shapes.
- The orchestrator adds a buyer-state/deal diagnosis and a concrete action choice (answer, ask, recommend, execute, confirm, exit) instead of relying on stage labels alone.
- The value-proof skill replaces the strict evidence ranking with relevance-based selection and adds a recommendation step.
- The objection skill adds implementation/adoption barriers and an entitlement-versus-concession rule: correcting the business's own error is not a trade.
- The language skill honors an explicit language preference over the last message and removes the oversimplified Kyrgyz word-order rule.

### Verified in this release

- `python3 scripts/validate_repository.py` passes (`0 errors`).
- `python3 scripts/test_checker.py` passes twelve scenario cases and three synthetic terminal-state cases without a model.
- `python3 scripts/test_installed_artifact.py` confirms all nine skills install self-contained.
- All three fictional passports validate; all ten invalid fixtures are rejected.

### Known limitations (unchanged)

- No live-model behavioral test, no tool adapter, no native Kyrgyz review, no jurisdiction review, and no conversion measurement. See `0.1.0` for the full list.

## Unreleased

No changes yet.
