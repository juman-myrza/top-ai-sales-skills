# Universal AI Sales Skills

A researched, Hermes-compatible skill set for text-based sales conversations, plus a separate **product passport** that supplies every business fact the agent is allowed to use.

The repository is designed for a sales assistant that can qualify, discover, handle objections, close, book, invoice, follow up, escalate, and speak Russian, Kyrgyz, or a natural mix — **without hardcoding a company, product, price, or calendar into the skills**. It is not a working sales platform. It contains instructions, contracts, examples, and tests; every external integration is still to be built.

> **Status:** v0.2.0, research and structural validation complete. No live model was evaluated, no tool adapter is connected, and no native Kyrgyz review has been completed. See [What is and is not verified](#what-is-and-is-not-verified).

---

## Why this exists

Most "AI sales agent" prompts fail in predictable ways:

- they invent a price, a discount, a case study, or an available meeting slot;
- they force every buyer toward a call;
- they keep pressuring after a clear no;
- they claim a booking or payment succeeded when the tool failed;
- they mix universal sales advice with one company's facts, so neither can be audited;
- they optimize for a persuasive demo rather than an informed, voluntary decision.

This repository separates the universal behavior from the business facts, makes tool confirmation mandatory, and encodes the failure paths as tests. The ambition is a top-tier sales agent; the repository does **not** claim that "top 0.1%" has been measured or proven.

---

## Architecture

```
core/                       constitutional rules: truth, consent, tools, escalation
skills/sales/               nine universal skills (no product facts)
product-passport/           business-specific facts, schema, fictional examples
tools/                      seven tool contracts and envelope schemas
tests/                      57 scenarios, rubric, coverage, response checker and installed-artifact tests
scripts/                    validation, checker tests, installed-artifact test, rendering, isolated loading, install
research/                   sources, claim-evidence matrix, decisions, repo audit
```

### The two halves

| Layer | Contains | Must not contain |
|---|---|---|
| **Universal skills** | Stage logic, question design, objection handling, integrity rules, language adaptation | Company names, prices, currencies, discounts, audience definitions, inventory, calendars, case studies |
| **Product passport** | Offer facts, prices, policies, proof permissions, authority limits, booking rules, handoff routes | Universal sales doctrine or instructions that override the core contract |

A fact that is not in an approved passport, or returned by an authoritative tool, must not be stated. That single rule is the main defense against a polished bot that invents commercial facts.

### Precedence when instructions conflict

1. Safety, consent, law, and platform policy
2. Truthfulness and permission to use a fact
3. Approved product passport and business authority limits
4. Skill recommendation
5. Persuasion or conversion preference

Read [Core Behavior Contract](core/CORE-BEHAVIOR-CONTRACT.md) and [Conflict Resolution](core/CONFLICT-RESOLUTION.md). The contract wins over any skill.

---

## The nine skills

| Skill | Job | Typical triggers |
|---|---|---|
| [`sales-conversation-orchestrator`](skills/sales/sales-conversation-orchestrator/SKILL.md) | Stage control, state, turn shape, routing | Any new turn; ambiguity; stage transition |
| [`sales-qualification`](skills/sales/sales-qualification/SKILL.md) | Fit, intent, authority, timing, honest disqualification | First contact; "is this for me?"; poor-fit signals |
| [`sales-discovery`](skills/sales/sales-discovery/SKILL.md) | Diagnose situation, problem, impact, decision criteria | Vague need; "we want to improve X"; multi-stakeholder deal |
| [`sales-value-proof`](skills/sales/sales-value-proof/SKILL.md) | Connect verified capabilities to the buyer's problem; evidence and ROI math | "Why you?"; proof requests; ROI questions |
| [`sales-objection-negotiation`](skills/sales/sales-objection-negotiation/SKILL.md) | Resolve doubt, compare options, negotiate within authority | Price, timing, competitor, trust, "send info" |
| [`sales-closing-execution`](skills/sales/sales-closing-execution/SKILL.md) | Ask for commitment, book, invoice, confirm tool results | "How do I pay?"; "Let's meet"; "Send an invoice" |
| [`sales-language-adaptation`](skills/sales/sales-language-adaptation/SKILL.md) | Russian, Kyrgyz, mixed-language register and clarity | Language switch; code-switching; ambiguous term |
| [`sales-follow-up`](skills/sales/sales-follow-up/SKILL.md) | Consent-based cadence, useful reminders, clean stop | No reply; "later"; no-show; opt-out |
| [`sales-integrity-escalation`](skills/sales/sales-integrity-escalation/SKILL.md) | Refuse manipulation, detect safety issues, hand off correctly | Human request; legal/complex terms; tool failure; abuse |

Each skill follows the Hermes `SKILL.md` format: YAML `name` and `description` (≤60 characters for Hermes), then the required sections from *When to Use* through *Sources*. Skills may load `references/` files only when needed.

---

## Quick start

### Requirements

- Python 3.11+
- `pip install -r requirements-dev.txt`
- Hermes Agent only for the isolated loading test and installation; static validation does not need it

### Validate the repository

```bash
python3 scripts/validate_repository.py
```

This checks file structure, skill frontmatter and sections, passport schemas, tool envelopes, 57 scenario definitions, coverage IDs, local links, obvious secrets, and hardcoded fictional facts. It also validates the example state, the three passport examples, and a set of deliberately invalid schema fixtures that the schemas must reject. Passing is **structural** validation, not a behavioral test.

### Check the response-checker contract

```bash
python3 scripts/evaluate_responses.py \
  --responses tests/fixtures/smoke-responses.jsonl \
  --allow-partial
```

The fixture is hand-written to exercise the checker, not model output. Two further test scripts run without a model:

```bash
python3 scripts/test_checker.py           # must-pass / must-fail checker cases
python3 scripts/test_installed_artifact.py  # a skill installed alone resolves its shared docs
```

### Test Hermes discovery without touching the live profile

```bash
python3 scripts/test_hermes_loading.py
```

The script creates a temporary `HERMES_HOME`, copies the nine skills into `skills/sales/`, and runs `hermes skills list --source local`. It never reads or writes `~/.hermes`. Hermes may spend a few minutes preparing dependencies the first time it sees a new data root.

### Install

Shell wrapper (dry run by default; add `--apply` to write):

```bash
# From a checkout
./install.sh --target ~/.hermes --apply

# Remote, review-first (recommended)
curl -fsSLO https://raw.githubusercontent.com/juman-myrza/top-ai-sales-skills/main/install.sh
less install.sh
sh install.sh --target ~/.hermes --apply

# Remote, piped (convenient, less review)
curl -fsSL https://raw.githubusercontent.com/juman-myrza/top-ai-sales-skills/main/install.sh \
  | sh -s -- --apply
```

Or call the Python installer directly:

```bash
python3 scripts/install_skills.py            # dry run; nothing is written
python3 scripts/install_skills.py --target ~/.hermes --apply
```

The installer validates the repository, creates `skills/sales/<name>/`, copies the shared `core/`, `tools/`, `product-passport/`, and `research/` documents into each skill under `references/shared/`, and rewrites each skill's links to point there, so an installed skill still resolves its dependencies when the checkout is gone. It writes an `INSTALL-MANIFEST.json` and an `ACTIVATION.md`. It skips existing directories unless `--force` is passed, and backs up replaced directories by default. It installs instructions only — not tool adapters, credentials, cron jobs, or a model.

When the wrapper is piped, it clones the repository into a temporary directory because the installer needs the whole checkout (the shared bundle is more than one file). Override the source with `SALES_SKILLS_REPO` and `SALES_SKILLS_REF`.

### Uninstall

The uninstaller is manifest-driven: it removes only the skill directories listed in `INSTALL-MANIFEST.json`, plus the activation files and the manifest. If the manifest is missing, it refuses to guess.

```bash
# From a checkout (dry run by default; add --apply to remove)
./uninstall.sh --target ~/.hermes --apply

# Remote
curl -fsSL https://raw.githubusercontent.com/juman-myrza/top-ai-sales-skills/main/uninstall.sh \
  | sh -s -- --target ~/.hermes --apply
```

Backups created by the installer (`.backup-*`) are left in place unless `--purge-backups` is passed. The uninstaller never touches other skills in the target home.

> Do not install into a live production profile until you have reviewed the [tool limitations](tools/README.md) and run the scenarios against your own model and passport.

---

## Product passport workflow

1. Copy [`product-passport/TEMPLATE.md`](product-passport/TEMPLATE.md) and fill one passport per offer.
2. Encode it as JSON matching [`passport.schema.json`](product-passport/passport.schema.json).
3. Mark every material fact `verified`, `estimated`, or `unknown`. Never fill an unknown with a guess.
4. Have finance, legal, operations, and a native Kyrgyz/Russian speaker review the relevant sections.
5. Approve the version; expose it through the `passport.lookup` contract.
6. Re-validate and re-run the scenario corpus after every material change.

Two complete fictional examples show the format:

- [Direct-sale example](product-passport/examples/direct-sale-nimbus-notes.md) — a digital product bought without a meeting.
- [Appointment-booking example](product-passport/examples/appointment-karkyra-consult.md) — a consult booked in chat.
- [Consumer example](product-passport/examples/consumer-course-example.md) — a B2C course bought directly, with no meeting.

All three use `.example.invalid` domains and are explicitly fictional. Do not copy their facts.

---

## Tool contracts, not integrations

The repository specifies seven contracts:

| Contract | Purpose |
|---|---|
| [`passport.lookup`](tools/contracts/passport-lookup.md) | Retrieve approved offer facts and authority limits |
| [`calendar.availability`](tools/contracts/calendar-availability.md) | Read real free/busy slots |
| [`calendar.booking`](tools/contracts/calendar-booking.md) | Create, reschedule, or cancel a booking |
| [`payments.invoicing`](tools/contracts/payments-invoicing.md) | Create payment requests/invoices and read status |
| [`crm.memory`](tools/contracts/crm-memory.md) | Read/write conversation state and deal records |
| [`human.handoff`](tools/contracts/human-handoff.md) | Create a handoff and pause automation |
| [`messaging.media`](tools/contracts/messaging-media.md) | Send messages, templates, and approved media |

Every request and response uses the [shared envelope schema](tools/schemas/tool-envelope.schema.json). The central rule:

> **No claim of completion without a confirming tool result.**

All three passport examples mark every binding `not_implemented`. No adapter, credential, webhook, CRM, calendar, or payment provider is included. Claims that an integration works would be false.

---

## Evaluation

The corpus contains **57 scenarios** in nine categories:

| Category | Count | Focus |
|---|---|---|
| Price and intent | 6 | Price questions, budget, buying signals, direct purchase |
| Qualification and discovery | 6 | Fit, poor fit, authority, discovery quality |
| Objections and negotiation | 10 | Price, timing, competitors, trust, discount limits, adoption risk, entitlement correction |
| Closing and booking | 7 | Direct close, invoice, in-chat booking, confirmation |
| Tool failures | 6 | Timeout, conflict, false success, handoff failure |
| Handoff and safety | 6 | Human request, legal complexity, abuse, privacy |
| Multilingual and multi-turn | 6 | Russian, Kyrgyz, mixed language, contradictions |
| Follow-up and refusal | 6 | Consent, cadence, no-show, opt-out |
| Consumer direct purchase | 4 | B2C price, scoped refusal, adoption, direct buy |

Start with [tests/README.md](tests/README.md), [SCENARIO-FORMAT.md](tests/SCENARIO-FORMAT.md), [RUBRIC.md](tests/RUBRIC.md), and [COVERAGE.md](tests/COVERAGE.md).

What the tests can detect: missing required facts or phrases, forbidden claims, excess questions, missing or forbidden tool calls, a tool status that contradicts the fixture, a required tool order that was violated, a wrong terminal state, a success claim with no confirming result, handoff/stop mismatches, and language-marker misses. What they cannot detect: tone, empathy, naturalness, strategic quality, or whether a true-sounding statement is actually true in a way the scenario did not anticipate.

---

## Repository map

| Path | Contents |
|---|---|
| [`core/`](core/) | Behavior contract, conflict resolution, conversation state, system-prompt snippet |
| [`skills/sales/`](skills/sales/) | Nine skills plus language, cadence, and escalation references |
| [`product-passport/`](product-passport/) | Template, JSON Schema, three fictional examples |
| [`tools/`](tools/) | Contracts, envelope schema, example envelopes |
| [`tests/`](tests/) | Scenario corpus, rubric, coverage, fixtures |
| [`scripts/`](scripts/) | Validation, evaluation, rendering, isolated loading, installation |
| [`research/`](research/) | Source register, claim-evidence matrix, decisions, open-source audit |

Key documents:

- [Core Behavior Contract](core/CORE-BEHAVIOR-CONTRACT.md)
- [System Prompt Snippet](core/SYSTEM-PROMPT-SNIPPET.md)
- [Product Passport README](product-passport/README.md)
- [Tool Contracts](tools/README.md)
- [Research: Source Register](research/source-register.md)
- [Research: Claim-Evidence Matrix](research/claim-evidence-matrix.md)
- [Research: Decisions and Tradeoffs](research/decisions-and-tradeoffs.md)
- [Research: Open-Source Audit](research/open-source-audit.md)

---

## Design commitments

- **Truth before persuasion.** A verified "I don't know" beats a confident invention.
- **Consent before action.** No booking, charge, proposal to a third party, or follow-up without the required permission.
- **In-chat booking by default.** Check real availability, offer real slots, book after agreement, confirm only the tool result. External scheduling links are a fallback, not the default.
- **Direct purchase is first-class.** Do not force a meeting when the buyer is ready and the passport allows direct fulfillment.
- **Conditional escalation.** Hand off for explicit human requests, missing authority or capability, legal/complex terms, tool failure, safety, or required approval — not for every hesitation.
- **No fake humanness.** No fake typing delays, fake identity, invented scarcity, fabricated proof, or pressure after refusal.
- **Questions are optional.** A useful statement, confirmation, or clean exit may end without a question.
- **Multilingual by design.** Russian, Kyrgyz, and code-switching are supported; Kyrgyz copy is flagged for native review.
- **Voice is out of scope.** Calls and voice notes are deferred to a later version.

---

## What is and is not verified

| Claim | Status |
|---|---|
| Repository structure, schemas, scenarios, and links are internally consistent | **Tested** by `scripts/validate_repository.py` |
| The nine skills are discovered by Hermes in an isolated home | **Tested locally** with Hermes v0.21.5 on 2026-10-23 |
| The response checker enforces its documented rules | **Tested** against a hand-written fixture |
| The skills improve sales outcomes, conversion, or retention | **Not tested**; no controlled experiment |
| A model follows the skills in live conversations | **Not tested**; no live model run |
| Calendar, payment, CRM, messaging, or handoff integrations work | **Not implemented** |
| Kyrgyz and mixed-language copy is production-quality | **Not verified**; native review required |
| Legal, tax, privacy, and consumer-protection compliance in any jurisdiction | **Not verified**; counsel required |
| "Top 0.1%" | **Aspiration, not a measured claim** |

The full boundary is documented in [tests/README.md](tests/README.md) and [research/decisions-and-tradeoffs.md](research/decisions-and-tradeoffs.md).

---

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). In short: never add a business fact to a skill, never weaken truth/consent/tool verification, add a scenario for every behavioral change, and run the validator before opening a pull request.

## License

MIT. See [LICENSE](LICENSE) and [ATTRIBUTION.md](ATTRIBUTION.md). The repository paraphrases research and practitioner frameworks; no third-party code was copied.
