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

- **Support estimate is not a guarantee.** The core contract now explicitly prohibits turning the passport's estimated support period into a warranty, SLA, or promise. Added Russian/Kyrgyz regression scenarios for support guarantees, including the previously observed wording “Кепилдик катары айта алам”.

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
- Root `install.sh` and `uninstall.sh` wrappers: POSIX `sh`, dry-run by default, `--apply` to write. The installer wrapper works from a checkout or bootstraps from a clone when piped (`curl … | sh -s -- --apply`). The uninstaller is manifest-driven: it removes only the manifested skill directories plus the activation files and manifest, refuses to guess without a manifest, and leaves backups unless `--purge-backups` is passed. A round-trip test (`scripts/test_install_uninstall.sh`) runs in CI.
- `tests/schema-invalid/` with ten deliberately invalid documents the schemas must reject, checked by the validator.
- Checker semantics documentation, new rubric sub-dimensions (`recommendation`, `barrier`, `progression`), and a behavioral-evaluation design document.
- CI steps for the checker regression test and the installed-artifact test.

### Changed

- The passport schema no longer requires `effective_from` on a `draft`; it remains required, with `approved_by`/`approved_at`, only once `status` is `approved`. This lets a draft exist without a fake effective date.
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

### Added

- Adaptive roleplay evaluation for Daniyar in tests/live/roleplay-cases.yaml and run_roleplay_eval.py: five synthetic multi-turn buyer situations covering trust/risk, budget, scope control in Kyrgyz, internal stakeholder alignment, and status-quo resistance. The harness records dialogue, raw calls, model/token metadata, and prompt/case/rubric/passport hashes, then produces a quote-grounded coaching scorecard. It is evaluation-only, does not use production tools or touch the active Hermes profile, and makes no claim that the same-model coach is an independent evaluator.


### Fixed

- **Two sales behaviors found by live-model evaluation** (`tests/live/`, 24 scenarios x 3 trials per arm on `deepseek/deepseek-v4.1-flash`, no tools connected; baseline at `f9eb812`, candidate at `0692b12`):
  - `sales-discovery`: agents must not lead with price, plans, or fees before diagnosis during discovery (new Step 8a with counterexample). Baseline volunteered `35 000 KGS` / `10 000 KGS` before diagnosis in 5 of 6 relevant trials; no candidate trial does.
  - `sales-language-adaptation`: a Kyrgyz greeting (`салам`, `рахмат`) inside an otherwise Russian message is not a language switch; the reply stays in the buyer's dominant language. The root cause was an internal contradiction in the skill's Example 3, which showed a Kyrgyz-dominant reply to a Russian-dominant buyer; Example 3 was corrected and a new Example 3a and a stronger branch rule were added. Baseline replied in Kyrgyz in 3 of 3 trials; all candidate trials reply in Russian while keeping the greeting.
- `sales-closing-execution`: Step 1a (state verified price, currency, and terms before proposing a next step) is retained as correct guidance. The scenario that motivated it (L-K06) was **mis-specified** — it did not say which of the two offers the buyer wanted — and has been corrected to a two-turn scenario; with the correction, both arms state the price, so it is not counted as a fixed deficiency.
- Overall deterministic pass rate: baseline 20–23/24 per trial; candidate 24/24 in all three trials. The improvement is consistent in this sample but three trials per arm is a small sample; effectiveness is not declared proven.
- **CI:** `scripts/test_installed_artifact.py` created its temp dir under `$TMPDIR` or `/tmp/opencode`; `/tmp/opencode` is absent on the GitHub runner, so `tempfile.mkdtemp` failed and the "installed artifact" CI step was red. It now falls back to the system temp dir when the configured base does not exist.

### Added

- `tests/live/` — live-model evaluation harness: 24 scenarios (9 Russian, 8 Kyrgyz, 7 Russian-dominant with code-switching), runner (`run_live_eval.py`), shared prompt assembly (`prompt_build.py`), deterministic scorer with a dominant-language check (`score_live_eval.py`), a provenance checker (`verify_run.py`), raw baseline and candidate responses with run metadata (`results/`), harness documentation (`README.md`), scoring table (`SCORING.md`), and the before/after report (`BEFORE-AFTER.md`). Evaluated against `deepseek/deepseek-v4.1-flash` on OpenRouter; no tool adapters are connected and the live Hermes profile is never touched.

### Changed

- Removed the dead always-on snippet: `core/SYSTEM-PROMPT-SNIPPET.md`, its activation copy, and every reference. The always-on layer is the profile's `SOUL.md` + `AGENTS.md`; the full `core/CORE-BEHAVIOR-CONTRACT.md` loads with the skills. This removes a fourth duplicate of the same invariants (task OC-2).
- **OC-1: checked per-skill bundle (documented fallback).** Each installed skill keeps its own copy of `core/`, `tools/`, `product-passport/`, and `research/` under `references/shared/` — the single-bundle layout cannot be served to the model because Hermes `skill_view` rejects any `..` path and enforces containment in a skill directory (`tools/skills_tool_plugin.py::_serve_skill_file`). The install manifest now records a sha256 for **every** bundle file (`shared.bundle_files`, `shared.bundle_file_count`, `shared.bundle_sha256`), and `scripts/test_installed_artifact.py` fails if any installed skill's copy is missing, extra, or different from the canonical source, so the nine copies cannot silently drift. The runtime guard enforces the same invariant on its side.
- `ACTIVATION.md` (generated by the installer) documents the minimum toolset for a client-facing agent and states that `terminal`, `code_execution`, `cronjob`, `computer_use`, and `browser` are not required by the skills. `scripts/test_installed_artifact.py` now fails if the skills reference any of them (task OC-6).
- `tools/adapters/passport-lookup/README.md` records the adapter as verified in the installed Daniyar profile (2026-10-28) instead of "not verified"; `product-passport/TEMPLATE.md` states that the passport `tools` section is operator metadata and is not visible to the model (task OC-3).
- **OC-8: tenant passport mirror provenance and drift check.** `tenants/daniyar/passports/` now mirrors the profile's authoritative store as a complete set: `schema/passport.schema.json` (byte-identical to the repository schema), both `offers/*/1.0.0.json` re-serialised to the profile's exact bytes, a generated `catalog.json`, and a `MIRROR.sha256` recording every file's SHA-256. `scripts/validate_repository.py::check_tenant_passports` enforces internal consistency (`catalog.json` entries must match the offer files) and recorded provenance (any edited offer or catalogue fails with "mirror drifted; re-sync from the profile"), and `scripts/test_installed_artifact.py` asserts an install never creates `<target>/{passports,state,tenants}`.

### Added

- File-backed `passport_lookup` reference adapter and Hermes plugin under `tools/adapters/passport-lookup/`. It implements `resolve`, `lookup`, and `authority` over versioned JSON passports with schema validation, approval/effective-window checks, tenant isolation, field allowlisting, proof-permission filtering, file-hash verification, and read-only conversation access.
- Operator `validate` and `publish` commands. Publishing validates first and atomically updates only `catalog.json`, preserving older passport versions and leaving skill directories untouched.
- `product-passport/catalog.example.json` and a deployment runbook for `/opt/data/profiles/daniyar`, covering initial setup, two-offer selection, price/policy updates, rollback, skill upgrades, and failure handling.
- `scripts/test_passport_lookup.py` with temporary fictional-store tests, including atomic publish and response-envelope validation, plus a CI step.
- Two draft tenant passports under `tenants/daniyar/passports/offers/` for the AI agent implementation and the practical AI training offers. They are `draft`, live outside `product-passport/` (so they are never bundled into skills), and encode supplied facts as `verified`, preliminary items as `estimated`, and open decisions as `unknown` or `unresolved`.
- `tenants/README.md` with the authoring, approval, and deploy rules, and a validator check for tenant passports (schema plus `offer.id`/`passport_id`/filename consistency).

### Verified in this change

- `python3 scripts/test_passport_lookup.py` passes without a model or external service.
- `hermes plugins validate tools/adapters/passport-lookup` passes in an isolated local Hermes home.
- The Daniyar VPS, Hermes v0.21.1, and live passport access have **not** been tested here.
