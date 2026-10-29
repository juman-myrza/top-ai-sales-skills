# Live sales evaluation harness (Daniyar)

**Purpose:** run 24 realistic, Russian / Kyrgyz / mixed-language sales scenarios against a pinned model on the current core contract, skills, and the two approved Daniyar passports, then compare a baseline arm against a candidate arm. Raw responses, prompts hashes, and deterministic scores are committed so the comparison is auditable.

**This is an evaluation harness, not a production adapter.** It is used for the baseline/fix/verify cycle described in the task. It does not deploy anything, does not touch the active Hermes profile, and does not change the product passport.

## Contents

| File | Purpose |
|---|---|
| `scenarios.yaml` | 24 scenario inputs: 9 Russian, 8 Kyrgyz, 7 Russian-dominant with code-switching (labelled `mixed`). Each has one or two buyer turns, a dominant reply-language expectation, and deterministic checks. |
| `run_live_eval.py` | Runs all 24 scenarios against OpenRouter (`deepseek/deepseek-v4.1-flash`, pinned in `meta` of each run) and writes raw responses + run metadata. |
| `prompt_build.py` | Deterministic prompt assembly, shared by the runner and the verifier. |
| `score_live_eval.py` | Applies deterministic checks (dominant reply language, required/forbidden phrases, regexes, question limits) to a recorded response file. |
| `verify_run.py` | Rebuilds a run's prompt from its recorded commit and checks the SHA-256. |
| `results/` | One subdirectory per arm (`baseline`, `candidate`) with raw JSONL responses, transcripts, run metadata, and scores. |

## The 24 scenarios

| Locale | Count | IDs | Focus |
|---|---|---|---|
| Russian | 9 | L-R01..L-R09 | discovery, exact price, discount refusal, case studies, scope limit, ready buyer, refusal, no-call terms |
| Kyrgyz | 8 | L-K01..L-K08 | same shape as R-scenarios, in Kyrgyz |
| Russian-dominant with code-switching | 7 | L-M01..L-M07 | Kyrgyz greeting in a Russian message, price summary, budget below floor, local proof, scope limit, meeting link, refusal |

`L-K06` is two turns: the buyer first selects the implementation offer, then asks what to do next, so the price expectation is unambiguous. Every scenario asserts `expect_reply_language`, a dominant-language expectation (`ru` fails only on a dominantly Kyrgyz reply, `ky` fails only on a dominantly Russian reply, `mixed` is never failed on language).

Every scenario names the passport version it refers to (`ai-agent-implementation` 1.0.0 or `ai-agent-training` 1.0.0 from `tenants/daniyar/passports/offers/`). The product passport is the only source of prices and terms; the model is given the passports verbatim in the system prompt.

## Focused regression: paused offer / pricing plan

The separate `offer-status-scenarios.yaml` pack checks a gap found in the approved Daniyar passport: the training offer is marked `active`, while its only pricing plan is `paused` and its price is `estimated`. Those states must not be collapsed into a claim that the course is available to buy.

This pack is intentionally separate from the original 24-scenario results. The previously reported 24/24 candidate score does **not** include this new guard.

Run the focused pack against the current candidate prompt:

```bash
python3 tests/live/run_live_eval.py \
  --arm candidate \
  --scenarios tests/live/offer-status-scenarios.yaml \
  --out tests/live/results/offer-status/candidate \
  --trial 1

python3 tests/live/score_live_eval.py \
  --responses tests/live/results/offer-status/candidate/responses-trial1-*.jsonl \
  --scenarios tests/live/offer-status-scenarios.yaml \
  --json-out tests/live/results/offer-status/candidate/checks-trial1.json
```

A passing deterministic score is a necessary guard, not proof of naturalness or sales effectiveness. Have a fluent Kyrgyz reviewer inspect the Kyrgyz answer before accepting that part of the evaluation.

## Runtime disclosure (read before trusting any number)

- **No tool is connected.** The system prompt tells the model that `calendar.availability`, `calendar.booking`, `payments.invoicing`, `human.handoff`, `messaging.media`, and `crm.memory` are not connected in this channel. A claimed booking/payment/handoff/invoice is therefore a truth failure, not a missing integration.
- **Single turn per scenario.** One buyer message, one agent response. Multi-turn behavior is not measured here.
- **Temperature 0.2, `reasoning_effort: none`, seed varied per trial.** Model output is stochastic; three trials per arm are run so a single lucky/unlucky run is not over-interpreted. A single trial is an anecdote, not proof.
- **Model:** `deepseek/deepseek-v4.1-flash` via OpenRouter (credential from `~/.hermes/.env`, `OPENROUTER_API_KEY`). The same model and the same prompt hash are used within an arm.
- **Prompt:** core contract + conflict resolution + conversation state + nine `SKILL.md` files + their references + both approved Daniyar passports. The prompt SHA-256 and the git commit are recorded in every run metadata file; different arms necessarily have different prompt hashes because the skills changed. `verify_run.py` rebuilds each prompt from its recorded commit and checks the hash, so a run cannot be silently attributed to the wrong code.
- **Checks are shallow.** Dominant-language, required/forbidden phrases catch a full-language switch, wrong prices, invented discounts/guarantees, and missing next steps. They do not measure tone, empathy, or strategic quality. The language classifier is a documented heuristic; Kyrgyz and mixed verdicts still require a native reviewer. See `SCORING.md` and `tests/RUBRIC.md` for the human/LLM rubric layer, which is not automated here.

## Running

Prerequisites: Python 3.11+, `PyYAML`, `requests`. An OpenRouter key must be available as `OPENROUTER_API_KEY` env var or in `~/.hermes/.env`.

```bash
# Dry run: prompt size and hash, no model calls
python3 tests/live/run_live_eval.py --arm baseline --dry-run

# Run one arm, three trials (each trial uses a different seed offset)
python3 tests/live/run_live_eval.py --arm baseline --trial 1
python3 tests/live/run_live_eval.py --arm baseline --trial 2
python3 tests/live/run_live_eval.py --arm baseline --trial 3

# Score a responses file against the scenario checks
python3 tests/live/score_live_eval.py \
  --responses tests/live/results/baseline/responses-trial1-*.jsonl \
  --json-out tests/live/results/baseline/checks-trial1.json
```

`--out` defaults to `tests/live/results/<arm>/`; files are named `responses-trial<N>-<timestamp>.jsonl` so trials never overwrite each other.

## Cost notice

Each run sends the full core + skills + passports (~2.0–2.1M prompt tokens) per arm. A full arm of 3 trials × 24 scenarios costs on the order of a few dollars on OpenRouter deepseek-v4.1-flash at current pricing (the baseline arm averaged about $0.10 per trial in this run). Each arm/trial was executed once and is not repeated.

## What is deliberately absent

- Real customer data, real transcripts, real prices outside the passport.
- Mock adapters pretending integrations work.
- A deployment or any write to `~/.hermes` (the active Hermes profile is never read or modified).
- A claim that any scenario pass rate equals sales effectiveness.
