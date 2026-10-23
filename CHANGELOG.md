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

## Unreleased

No changes yet.
