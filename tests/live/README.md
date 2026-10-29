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
| roleplay-cases.yaml | Five adaptive, synthetic multi-turn buyer personas; no fixed passport prices. |
| run_roleplay_eval.py | Runs a buyer simulator, Daniyar, and a post-session evidence-based coach; saves transcripts, raw calls, hashes, and scores. |
| test_roleplay_eval.py | No-network structural tests for roleplay cases, transcript-evidence checking, and JSON parsing. |

## The 24 scenarios

| Locale | Count | IDs | Focus |
|---|---|---|---|
| Russian | 9 | L-R01..L-R09 | discovery, exact price, discount refusal, case studies, scope limit, ready buyer, refusal, no-call terms |
| Kyrgyz | 8 | L-K01..L-K08 | same shape as R-scenarios, in Kyrgyz |
| Russian-dominant with code-switching | 7 | L-M01..L-M07 | Kyrgyz greeting in a Russian message, price summary, budget below floor, local proof, scope limit, meeting link, refusal |

`L-K06` is two turns: the buyer first selects the implementation offer, then asks what to do next, so the price expectation is unambiguous. Every scenario asserts `expect_reply_language`, a dominant-language expectation (`ru` fails only on a dominantly Kyrgyz reply, `ky` fails only on a dominantly Russian reply, `mixed` is never failed on language).

Every scenario names the passport version it refers to (`ai-agent-implementation` 1.0.0 or `ai-agent-training` 1.0.0 from `tenants/daniyar/passports/offers/`). The product passport is the only source of prices and terms; the model is given the passports verbatim in the system prompt.

## Focused regression: passport status and support commitments

The separate `offer-status-scenarios.yaml` pack checks two passport-driven risks: the training offer is marked `active`, while its only pricing plan is `paused` and its price is `estimated`; and the intended support period (up to three months) is itself marked `estimated`, with the channel, response time and limits not finalized. The agent must not claim that the course is available to buy or turn estimated support into a guarantee.

The pack has four focused scenarios (Russian/Kyrgyz for paused-plan availability and estimated-support guarantees). It is intentionally separate from the original 24-scenario results. The previously reported 24/24 candidate score does **not** include these new guards.

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

## Focused before/after runs

Use the focused runner to test the two targeted guards without re-running the original 24-scenario corpus. It performs two isolated comparisons, three trials per arm:

- **Paused pricing plan:** PR #5 baseline commit `a52574a872c2d8aaccde47a9fdab239a46bfe467` vs. PR #6 candidate commit `6ceb35caf939af227f533edec861d69b48517bb8`.
- **Estimated support guarantee:** PR #6 baseline commit `6ceb35caf939af227f533edec861d69b48517bb8` vs. the current checked-out commit (PR #7 or a later reviewed commit).

The script copies only the evaluation harness and scenario pack into temporary Git worktrees. The model prompt is assembled from each worktree's pinned core contract, skills, and product passports. It does not write to the active Hermes profile, change passport facts, or deploy anything.

Requirements: Git, Python dependencies from `requirements-dev.txt`, and `OPENROUTER_API_KEY` in the environment or `~/.hermes/.env`. Run from a clean checkout of the candidate branch:

```bash
bash tests/live/run_focused_ab.sh
```

The run creates `tests/live/results/focused-ab/` with raw responses, transcripts, metadata, and deterministic scores. Each metadata file records the prompt SHA-256, full scenario-file SHA-256, selected scenario IDs, harness script hashes, model, trial/seed settings, and source commit. Review the raw transcript alongside the score; a deterministic pass is not a quality or conversion verdict. Calls are made through OpenRouter and may incur API charges.

## Adaptive roleplay practice

The roleplay pack is separate from the passport-specific regression scenarios and the existing 24 single-turn tests. It contains five fictional buyer situations: skepticism about AI mistakes, budget/cash-flow pressure, excessive requested scope in Kyrgyz, an internal champion who needs to convince a director, and a mixed-language buyer unsure that automation is worth changing the current process.

Run the harness without model calls first:

```bash
python3 tests/live/run_roleplay_eval.py --dry-run
```

Run all five synthetic dialogues when ready:

```bash
python3 tests/live/run_roleplay_eval.py --trial 1
```

Or run one focused conversation:

```bash
python3 tests/live/run_roleplay_eval.py --only RP-RU-TRUST --trial 1
```

The run writes a timestamped directory under tests/live/results/roleplay/ with one transcript, raw model calls, coach JSON, and a manifest containing the commit, prompt/case/rubric/passport hashes and token usage. It makes model calls through OpenRouter and may incur charges. No production tools, live Hermes profile, or deployment are involved.

The buyer and coach are simulated with the same model family as the seller; their outputs are useful for practice, not independent truth. The coach must quote the transcript for every score and flags quote mismatches. Do not treat the score as proof of sales conversion. Kyrgyz language naturalness requires fluent human review.

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
