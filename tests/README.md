# Tests and Evaluation

This directory contains a **scenario corpus and deterministic checks**, not proof that a language model behaves well. The repository has not run behavioral tests against a live model. It has not connected any tool. Results must be reported as structural validation, not sales performance.

---

## Test layers

| Layer | What it checks | Run by | Status in this repo |
|---|---|---|---|
| 1. Static validation | JSON/YAML parse, schema conformance, links, skill frontmatter, forbidden placeholders | `scripts/validate_repository.py` | Implemented |
| 2. Isolated Hermes loading | Skills are discoverable by Hermes in a temporary `HERMES_HOME` | `scripts/test_hermes_loading.py` | Implemented and verified locally with Hermes v0.21.5 on 2026-10-23 |
| 3. Scenario corpus | 57 scenarios exist, IDs are unique, categories are covered, every scenario has checks | validator | Implemented |
| 4. Response checks | A recorded agent response satisfies deterministic rules (required phrases, forbidden claims, question count, tool calls, tool status) | `scripts/evaluate_responses.py` | Implemented; requires a response file |
| 4a. Checker regression | Nine cases pin known checker false positives and false negatives | `scripts/test_checker.py` | Implemented, no model |
| 4b. Installed artifact | A skill installed alone still resolves its core contract, contracts, and passport schema | `scripts/test_installed_artifact.py` | Implemented, no model |
| 5. Rubric review | Truth, consent, diagnosis, language, integrity, execution quality | human or LLM judge | Rubric written; **not run** |
| 6. Live tool integration | Real calendar/payment/CRM/messaging adapters | adapter tests | **Not implemented** |
| 7. Conversion/retention impact | Whether the agent improves revenue without harm | production experiment | **Not run** |

A passing layer 4 run means "the response did not contain the explicitly forbidden strings and did include the required ones." It does **not** mean the response is good. That is why every scenario also has a rubric focus.

---

## Scenario corpus

57 scenarios across nine files:

| File | Category | Count |
|---|---|---|
| [`scenarios/price-intent.yaml`](scenarios/price-intent.yaml) | Price requests and buying signals | 6 |
| [`scenarios/qualification-discovery.yaml`](scenarios/qualification-discovery.yaml) | Fit, disqualification, discovery | 6 |
| [`scenarios/objections.yaml`](scenarios/objections.yaml) | Objections and negotiation | 10 |
| [`scenarios/closing-booking.yaml`](scenarios/closing-booking.yaml) | Direct close, invoice, booking | 7 |
| [`scenarios/tool-failures.yaml`](scenarios/tool-failures.yaml) | Timeouts, conflicts, false success | 6 |
| [`scenarios/handoff-safety.yaml`](scenarios/handoff-safety.yaml) | Human handoff, integrity, safety | 6 |
| [`scenarios/multilingual-multiturn.yaml`](scenarios/multilingual-multiturn.yaml) | Russian/Kyrgyz/mixed, contradictions | 6 |
| [`scenarios/follow-up-refusal.yaml`](scenarios/follow-up-refusal.yaml) | Consent, cadence, refusal, no-show | 6 |
| [`scenarios/consumer-direct.yaml`](scenarios/consumer-direct.yaml) | B2C direct purchase and scoped refusal | 4 |
| **Total** | | **57** |

The format is documented in [`SCENARIO-FORMAT.md`](SCENARIO-FORMAT.md). The rubric is in [`RUBRIC.md`](RUBRIC.md), and the design for a real model run is in [`BEHAVIORAL-EVALUATION.md`](BEHAVIORAL-EVALUATION.md).

---

## Running

### 1. Static validation

```bash
python3 scripts/validate_repository.py
```

Checks:

- every JSON file parses;
- all three passport examples (two business, one consumer) validate against the schema;
- every scenario YAML parses and has the required fields;
- 57 unique IDs and the expected category counts;
- skill directories and `SKILL.md` frontmatter;
- no unreplaced `[verified …]` placeholders in examples;
- links to local files resolve where practical;
- no obvious secrets or card-like numbers.

### 2. Isolated Hermes loading

```bash
python3 scripts/test_hermes_loading.py
```

This creates a temporary `HERMES_HOME`, copies the skills into the expected category layout, and asks Hermes to list/view them. It does **not** touch `~/.hermes` or the active profile. It requires a working local Hermes installation; if Hermes is absent, the script reports `skipped` rather than pretending to pass.

### 3. Response evaluation

Record agent responses in JSONL:

```json
{"scenario_id":"P01","response":"...","tool_calls":[{"tool":"passport.lookup","operation":"lookup","status":"ok"}],"handoff":false,"handoff_attempted":false,"stopped":false}
```

Then:

```bash
python3 scripts/evaluate_responses.py --responses tests/responses/example.jsonl
```

To check the checker itself without a model, use the hand-written smoke fixture:

```bash
python3 scripts/evaluate_responses.py \
  --responses tests/fixtures/smoke-responses.jsonl \
  --allow-partial
```

The smoke fixture is not model output and does not represent a test result. `scripts/test_checker.py` runs nine must-pass and must-fail cases against the checker itself; it proves the checker catches a wrong price, a false confirmation, and a negated refusal, not that a model behaves well.

The checker reports, per scenario:

- missing required phrases;
- forbidden phrases/regexes present;
- question count over the limit;
- missing required tool calls;
- a required tool status that is not in the allowed set;
- a tool fixture status that disagrees with the recorded calls;
- a required tool order that was violated;
- a terminal state that differs from `expected_final_state`;
- a success claim (booking, payment, invoice, handoff, message) with no confirming tool result;
- forbidden tool calls/operations used;
- handoff/stop mismatch;
- language-marker miss (where configured).

It does not score the rubric. A response can pass every deterministic check and still be manipulative, confusing, or false in a way the checks did not anticipate.

---

## Deterministic check semantics

All string checks are case-insensitive substring matches after normalizing whitespace and common quote characters.

| Field | Semantics |
|---|---|
| `must_include_all` | Every string must appear |
| `must_include_any` | At least one string must appear |
| `must_not_include` | None may appear, unless every occurrence is negated (for example a correct "we do not support HIPAA") |
| `must_not_regex` | None may match |
| `must_match_regex_all` | Every regex must match |
| `must_match_regex_any` | At least one regex must match |
| `max_questions` | Count of `?` in the response must be ≤ this |
| `required_tool_calls` | Each listed tool must appear in `tool_calls` |
| `required_tool_statuses` | The recorded status for a tool (or `tool:operation`) must be one of the listed values |
| `forbidden_tool_calls` | None may appear |
| `forbidden_tool_operations` | None may appear as `tool:operation` |
| `should_handoff` | `handoff` must be `true` |
| `should_attempt_handoff` | A handoff attempt must be recorded even if confirmation failed |
| `should_stop` | `stopped` must be `true` |
| `should_disqualify` | Response must contain a disqualification phrase and not a booking/payment call |

Numeric needles such as `960` use digit boundaries, so `1960` does not satisfy a required `960`. The checker also verifies that a scenario fixture status agrees with the recorded tool status and that a success claim has a confirming tool result.

These checks are intentionally shallow. They catch the most expensive failure modes: invented prices, false payment confirmation, external links by default, booking without availability, and sales pressure after refusal.

---

## Rubric review

Use [`RUBRIC.md`](RUBRIC.md) for a human or an LLM judge. Score each dimension 0–4 and record evidence quotes. Do not average away a safety failure: a 0 on integrity or consent is a fail regardless of the total.

The rubric is a structured review aid, not a validated psychometric instrument. Inter-rater reliability has not been measured.

---

## What has not been tested

- No live model was called.
- No calendar, payment, CRM, messaging, or handoff adapter exists.
- No real customer data was used.
- No Kyrgyz native speaker has reviewed the Kyrgyz lines.
- No conversion, retention, complaint, or opt-out impact was measured.
- No adversarial red-team beyond the written scenarios was run.
- No load, latency, or cost test was run.
- No jurisdiction-specific legal review was completed.

The final report must keep these distinctions explicit. "Written" is not "tested"; "tested structurally" is not "proven in production".
