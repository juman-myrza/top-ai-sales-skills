# Before/after report: Daniyar sales skills, live-model evaluation

**Goal:** improve Daniyar's real sales, not the skill count. Baseline → fix → verify, same model, same 24 scenarios, no deployment, no change to the active Hermes profile, no change to the product passport.

**Model:** `deepseek/deepseek-v4.1-flash` via OpenRouter, temperature 0.2, `reasoning_effort: none`.
**Scenarios:** `tests/live/scenarios.yaml` — 24 scenarios: 9 Russian, 8 Kyrgyz, 7 Russian-dominant with code-switching. Each names the Daniyar passport version it refers to (`ai-agent-implementation` 1.0.0, `ai-agent-training` 1.0.0).
**Passport:** the only source of prices, terms, proof, and authority limits; both approved passports are included verbatim in the system prompt.

## Provenance (verifiable)

| Arm | Commit | Prompt SHA-256 | Trials |
|---|---|---|---|
| baseline (original skills) | `f9eb812bf771` | `b7871a7bc550` | 3 |
| candidate (fixed skills) | `0692b12e5d83` | `57224ef84d1d` | 3 |

`python3 tests/live/verify_run.py --all` rebuilds each run's prompt from its recorded commit and confirms the hash. Raw responses, transcripts, run metadata, and per-scenario scores are committed under `tests/live/results/`. Baseline was run in a git worktree checked out at the infra commit `f9eb812` (original skills), so the baseline arm is tied to a concrete commit rather than an uncommitted working tree.

## What was fixed

Baseline scoring showed two behaviors that fail in the sample, plus one scenario defect:

1. **Price led in discovery before diagnosis** (`sales-discovery`, new Step 8a + counterexample). When the buyer describes a problem and asks where to start (`L-K01`, `L-M01`), the baseline volunteered `35 000 KGS` / `10 000 KGS` before any diagnosis.
2. **A Kyrgyz greeting inside a Russian message triggered a full-Kyrgyz reply** (`sales-language-adaptation`). A Russian-dominant buyer who opens with `Салам!` (`L-M01`) got a Kyrgyz-dominant reply in all three baseline trials. The root cause was an internal contradiction: the skill's Example 3 showed exactly this wrong behavior. Example 3 was corrected (the Kyrgyz-dominant example now has a Kyrgyz-dominant buyer) and a new Example 3a plus a stronger branch rule were added.
3. **L-K06 scenario defect (not a skill defect).** The original L-K06 sent only "Макул, баштайлы. Эмне кылыш керек?" with no prior context and required the implementation price (35 000 / 10 000), which belongs to the implementation offer, not the paused, estimate-priced course. The scenario now has two turns: the buyer first selects the implementation offer, then asks what to do next.

Skill edits are additive (new sections, counterexamples, one corrected example); no existing instruction removed, no passport fact changed.

## Results (deterministic checks only)

| Arm | Trial 1 | Trial 2 | Trial 3 | Average |
|---|---|---|---|---|
| baseline | 23/24 | 22/24 | 20/24 | 21.7/24 (~90%) |
| candidate | 24/24 | 24/24 | 24/24 | 24/24 (100%) |

Baseline failures: L-M01 in all three trials (price in discovery + Kyrgyz reply), L-K01 in two trials (price in discovery), plus L-R06 and L-K08 in one trial each. Candidate failures: none.

### The targeted behaviors, before vs after

| # | Behavior | Baseline | Candidate | Verdict |
|---|---|---|---|---|
| 1 | Price in discovery (L-K01, L-M01) | Price volunteered before diagnosis in 5 of 6 relevant trials | No price before diagnosis in any trial | **Fixed in this sample** |
| 2 | Terms before next step (L-K06) | Both arms state 35 000/10 000 once the product is unambiguous | Same | **Withdrawn** — was a scenario defect |
| 3 | Language mirroring (L-M01) | Kyrgyz-dominant reply in 3/3 trials | Russian-dominant reply, greeting kept, in 3/3 trials | **Fixed in this sample** |

## Honest conclusion

Two targeted behaviors are fixed across all three candidate trials; the third was a mis-specified scenario and is withdrawn. The candidate arm scores 24/24 in all three trials versus a baseline of 20–23/24. The improvement is consistent across trials in this sample, but three trials per arm at temperature 0.2 is a small sample, the deterministic checks are shallow, and no rubric or native-speaker review has been done. This is evidence of behavior change on 24 scenarios, **not** proof of sales effectiveness.

## Remaining problems (open)

1. No rubric scores: `tests/RUBRIC.md` dimensions are unjudged; Kyrgyz/mixed turns need a native speaker.
2. Baseline-only residuals that may recur on other seeds: L-R06 (no terms to a ready buyer), L-K08 (calling support a "guarantee").
3. Phrase-list checks are a proxy; several were widened here and need Kyrgyz-speaker review.
4. No tool integration: bookings, payments, invoices, handoffs are never confirmed by a tool.
5. Small sample: three trials per arm; re-run with more trials before treating the language/discovery verdicts as stable.

## Evidence in this branch

- `tests/live/scenarios.yaml` — the 24 scenarios (with `expect_reply_language`)
- `tests/live/run_live_eval.py`, `prompt_build.py` — harness and prompt assembly
- `tests/live/score_live_eval.py` — dominant-language classifier + checks
- `tests/live/verify_run.py` — reproduces a run's prompt hash from its commit
- `tests/live/results/baseline/`, `tests/live/results/candidate/` — raw responses (`.jsonl`), transcripts, run metadata, per-scenario scores
- `tests/live/SCORING.md`, `tests/live/README.md` — scoring detail and harness docs

## What was NOT done (per the constraints)

- No changes to `tenants/daniyar/passports/` (product passport untouched).
- No changes to `~/.hermes` or the active Hermes profile; no deployment.
- No external repositories copied.
- No fabricated prices, discounts, guarantees, case studies, or results.
- No claim of improved sales effectiveness — only deterministic check differences on 24 scenarios.
