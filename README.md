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

The script creates a temporary `HERMES_HOME`, installs the nine skills through the real installer, and runs `hermes skills list --source local`. It never reads or writes `~/.hermes`. Hermes may spend a few minutes preparing dependencies the first time it sees a new data root.

### Install

The wrapper is a dry run by default; add `--apply` to write.

**Option A — from a checkout (works for public or private repos).** Clone first, then run the wrapper from inside the repository:

```bash
git clone https://github.com/juman-myrza/top-ai-sales-skills.git
cd top-ai-sales-skills
./install.sh --target ~/.hermes --apply     # or: sh install.sh ... if not executable
```

`./install.sh` finds `scripts/install_skills.py` next to it and installs from this checkout. You must `cd` into the repository (or pass the path); running `./install.sh` from an unrelated directory will not find it.

**Install for one specific agent (Hermes profile).** `--target ~/.hermes` writes to the shared root home. Hermes keeps per-profile skills under `~/.hermes/profiles/<name>/skills/`, so to scope the install to one agent, target that profile home instead:

```bash
ls ~/.hermes/profiles                              # list profiles (agents)
./install.sh --target ~/.hermes/profiles/tom --apply
hermes skills list --source local -p tom           # confirm they load for that agent
```

Use the root target (`~/.hermes`) only if you intend the shared home, and a profile target to install for exactly one agent. To remove them again, use the same `--target` with `./uninstall.sh`.

**Option B — remote one-liner (public repos only).** This downloads *just* the wrapper; the wrapper then clones the repository into a temporary directory. `raw.githubusercontent.com` serves only public repositories, so this does not work for a private repo.

```bash
# review-first (recommended)
curl -fsSLO https://raw.githubusercontent.com/juman-myrza/top-ai-sales-skills/main/install.sh
less install.sh
sh install.sh --target ~/.hermes --apply

# piped (convenient, less review)
curl -fsSL https://raw.githubusercontent.com/juman-myrza/top-ai-sales-skills/main/install.sh \
  | sh -s -- --apply
```

These URLs only resolve once `install.sh` is committed and pushed to `main`, and only if the repository is public. Override the clone source with `SALES_SKILLS_REPO` and `SALES_SKILLS_REF` (or `--ref=BRANCH`).

Or call the Python installer directly from a checkout:

```bash
python3 scripts/install_skills.py            # dry run; nothing is written
python3 scripts/install_skills.py --target ~/.hermes --apply
```

The installer validates the repository, creates `skills/sales/<name>/`, copies the shared `core/`, `tools/`, `product-passport/`, and `research/` documents into each skill under `references/shared/`, and rewrites each skill's links to point there, so an installed skill still resolves its dependencies when the checkout is gone. It writes an `INSTALL-MANIFEST.json` and an `ACTIVATION.md`. It skips existing directories unless `--force` is passed, and backs up replaced directories by default. It installs instructions only — not tool adapters, credentials, cron jobs, or a model.

### Uninstall

The uninstaller is manifest-driven: it removes only the skill directories listed in `INSTALL-MANIFEST.json`, plus the activation files and the manifest. If the manifest is missing, it refuses to guess.

```bash
# From a checkout (dry run by default; add --apply to remove)
git clone https://github.com/juman-myrza/top-ai-sales-skills.git
cd top-ai-sales-skills
./uninstall.sh --target ~/.hermes --apply

# Remote (public repos only; requires uninstall.sh on main)
curl -fsSL https://raw.githubusercontent.com/juman-myrza/top-ai-sales-skills/main/uninstall.sh \
  | sh -s -- --target ~/.hermes --apply
```

The uninstaller needs only the target home, not the repository. Backups created by the installer (`.backup-*`) are left in place unless `--purge-backups` is passed. It never touches other skills in the target home.

### Update

Updating the installed skills is independent of the passports and the plugin. Pull the new version and reinstall with `--force`:

```bash
git pull
./install.sh --target ~/.hermes/profiles/daniyar --apply --force
```

- Without `--force` existing skill directories are skipped, so nothing changes.
- With `--force` each replaced directory is copied to `.backup-<timestamp>` inside `skills/sales/` first (unless `--no-backup`).
- Passports (`passports/`) and the plugin (`plugins/passport-lookup/`) are **outside** the installer's scope and are never overwritten, deleted, or replaced by an update.
- `INSTALL-MANIFEST.json` records the source commit, the core contract version, and file hashes, so you can see what is active after an update.
- Remove accumulated backups with `./uninstall.sh --target <profile> --apply --purge-backups`, or delete them manually.

> Do not install into a live production profile until you have reviewed the [tool limitations](tools/README.md) and run the scenarios against your own model and passport.

---

## Product passport workflow

The universal skills contain no business facts. One JSON passport per offer supplies them. A passport has two lives: an **authoring draft** (this repository, or wherever you keep the source) and the **authoritative copy** in the Hermes profile's persistent store.

### 1. Author and approve

1. Copy [`product-passport/TEMPLATE.md`](product-passport/TEMPLATE.md) and fill one passport per offer, then encode it as JSON matching [`passport.schema.json`](product-passport/passport.schema.json).
2. Mark every material fact `verified`, `estimated`, or `unknown`. Never fill an unknown with a guess; list open decisions in `unresolved`.
3. Have the relevant reviewers (finance, legal, operations, native Kyrgyz/Russian speaker) check the relevant sections.
4. Keep it `draft` until the commercial decisions are approved. Ready-made drafts live under [`tenants/<tenant>/passports/`](tenants/) — for Daniyar, [`tenants/daniyar/passports/`](tenants/daniyar/passports/offers/).
5. To release an offer: set `status: approved` plus `approved_by`, `approved_at`, and `effective_from`.

### 2. Put filled passports where the running agent reads them

Authoritative passports live in a **persistent store outside the skills**, so that installing or updating skills never overwrites them. For Daniyar:

```text
/opt/data/profiles/daniyar/              # the Hermes profile home
├── passports/                           # authoritative business data (NOT touched by install.sh)
│   ├── schema/passport.schema.json
│   ├── offers/<offer_id>/<version>.json
│   └── catalog.json                     # created / updated by the publish command
├── plugins/passport-lookup/             # the read-only adapter plugin
└── skills/sales/                        # installer-managed skills
```

Copy the drafts into the store on the VPS:

```bash
export DANIYAR_HOME=/opt/data/profiles/daniyar
export DANIYAR_PASSPORT_ROOT="$DANIYAR_HOME/passports"
mkdir -p "$DANIYAR_PASSPORT_ROOT/offers"
cp -a tenants/daniyar/passports/offers/. "$DANIYAR_PASSPORT_ROOT/offers/"
```

Then configure the `passport_lookup` plugin, `validate`, and `publish` each offer. Full storage layout, deployment, publish, rollback, failure behavior, and the privacy/security notes are in the [passport-lookup runbook](tools/adapters/passport-lookup/README.md). Source-draft and approval rules are in [`tenants/README.md`](tenants/README.md).

Do **not** put authoritative passports inside `product-passport/` or a skill's `references/shared/` — those are bundled into every installed skill and are replaced on update.

### 3. Change a price or policy without reinstalling

Add a new version file, then `validate` and `publish` it (see the runbook). This changes only `catalog.json` and keeps older versions for rollback. No skill reinstall is needed.

Three complete fictional examples show the format:

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

The fictional passport examples mark every binding `not_implemented`. `passport.lookup` now also has a local, file-backed reference adapter ([`tools/adapters/passport-lookup/`](tools/adapters/passport-lookup/)); the other six contracts remain specifications only. No credential, webhook, CRM, calendar, or payment provider is included. Claims that a live integration works would be false.

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
| [`core/`](core/) | Behavior contract, conflict resolution, conversation state |
| [`skills/sales/`](skills/sales/) | Nine skills plus language, cadence, and escalation references |
| [`product-passport/`](product-passport/) | Template, JSON Schema, three fictional examples |
| [`tools/`](tools/) | Contracts, envelope schema, example envelopes, and the file-backed passport lookup adapter |
| [`tools/adapters/passport-lookup/`](tools/adapters/passport-lookup/) | Read-only versioned JSON passport adapter and Hermes plugin |
| [`tenants/`](tenants/) | Tenant business passports as source drafts (outside the bundled skill docs) |
| [`tests/`](tests/) | Scenario corpus, rubric, coverage, fixtures |
| [`scripts/`](scripts/) | Validation, evaluation, rendering, isolated loading, installation |
| [`research/`](research/) | Source register, claim-evidence matrix, decisions, open-source audit |

Key documents:

- [Core Behavior Contract](core/CORE-BEHAVIOR-CONTRACT.md)
- [Product Passport README](product-passport/README.md)
- [Tool Contracts](tools/README.md)
- [Passport Lookup Adapter and Deployment Runbook](tools/adapters/passport-lookup/README.md)
- [Tenant Passport Drafts](tenants/README.md)
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
