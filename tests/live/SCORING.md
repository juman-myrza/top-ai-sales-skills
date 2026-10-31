# Deterministic scoring for the 24 live scenarios

Each recorded response is checked against the scenario's `checks:` block in `tests/live/scenarios.yaml`. A scenario passes when all its checks pass.

Checks applied:

| Check | Meaning |
|---|---|
| `expect_reply_language` | Dominant-language expectation on the last turn (`ru` fails only on a dominantly Kyrgyz reply, `ky` fails only on a dominantly Russian reply, `mixed` is never failed). |
| `must_include_all` | Every phrase must appear somewhere in the response(s). |
| `must_include_any` / `must_include_any_2` | At least one of the phrases must appear. |
| `must_not_include` | Phrase must not appear unless negated (sentence-scope, including Kyrgyz negative verb suffixes such as `кылынбайт`). |
| `must_not_regex` | No match allowed. |
| `max_questions` | Question marks per turn must not exceed the limit. |

These checks are **necessary, not sufficient**: they catch a full-language switch, wrong prices, invented discounts/guarantees, and missing next steps. They do not score tone, empathy, or strategic quality (see `tests/RUBRIC.md`). The dominant-language classifier is a documented heuristic; Kyrgyz and mixed verdicts still require a native reviewer.

## Run provenance

Six runs, three trials per arm, same model (`deepseek/deepseek-v4.1-flash`), same temperature (0.2), same 24 scenarios, same scorer. Each arm ties to a concrete commit, and `verify_run.py` rebuilds every prompt from that commit and confirms the recorded hash:

| Arm | Commit | Prompt SHA-256 | Trials |
|---|---|---|---|
| baseline (original skills) | `f9eb812bf771` | `b7871a7bc550` | 3 |
| candidate (fixed skills) | `0692b12e5d83` | `57224ef84d1d` | 3 |

```
$ python3 tests/live/verify_run.py --all
OK   run-trial1-...: OK (f9eb812bf771, b7871a7bc550)
...  (all six runs reproduce)
```

`repo_commit` pins the skill/core/passport prompt that was sent to the model (the only thing `verify_run.py` rebuilds). The scenario file and the scorer were finalized while scoring and are committed in the same commit as the results; **both arms were scored with the final `scenarios.yaml` and `score_live_eval.py`**, so the comparison is like-for-like.

## Results

| Arm | Trial 1 | Trial 2 | Trial 3 | Average |
|---|---|---|---|---|
| baseline | 23/24 | 22/24 | 20/24 | 21.7/24 (~90%) |
| candidate | 24/24 | 24/24 | 24/24 | 24/24 (100%) |

Baseline failures:
- trial 1: L-M01 (price in discovery + Kyrgyz reply to a Russian buyer)
- trial 2: L-K01 (price in discovery), L-M01 (price + Kyrgyz reply)
- trial 3: L-R06 (no terms to a ready buyer), L-K01 (price in discovery), L-K08 (calls support a "guarantee"), L-M01 (price + Kyrgyz reply)

Candidate failures: none.

## The three targeted deficiencies

| # | Deficiency (skill edited) | Baseline | Candidate | Verdict |
|---|---|---|---|---|
| 1 | Price led in discovery before diagnosis (`sales-discovery`, Step 8a). L-K01, L-M01. | Prices volunteered in 2 of 3 trials (L-K01) and 3 of 3 (L-M01). | No price volunteered before diagnosis in any trial. | **Fixed in this sample.** |
| 2 | Ready buyer got a discovery question instead of verified terms (`sales-closing-execution`, Step 1a). L-K06. | Passes: the buyer is asked which path, but both arms state 35 000/10 000. | Passes. | **Not a real deficiency once the scenario is corrected** — see below. |
| 3 | Kyrgyz greeting inside a Russian message triggered a full-Kyrgyz reply (`sales-language-adaptation`, branch + Example 3 fix). L-M01. | Kyrgyz-dominant reply in 3 of 3 trials. | Russian-dominant reply (keeping the greeting) in 3 of 3 trials. | **Fixed in this sample.** |

### Why deficiency 2 was withdrawn

The original L-K06 sent only "Макул, баштайлы. Эмне кылыш керек?" with no prior context. That turn does not say which of the two offers the buyer wants, and the required price (35 000 / 10 000) belongs to the implementation offer, not the paused, estimate-priced course. Requiring that price without an unambiguous product choice was a scenario defect, not a sales error.

L-K06 is now two turns: the buyer first selects the implementation offer ("Бизге бизнес үчүн даяр AI-агент керек — окутуу курсу эмес."), then asks what to do next. With the corrected scenario, **both** arms state the price and terms, so this is no longer a discriminating deficiency. The `sales-closing-execution` Step 1a addition is kept because it is correct guidance and did not harm the other closing scenarios (L-R06 still fails occasionally in baseline; candidate L-R06 passes in all trials).

## Honest conclusion

Deficiencies 1 and 3 are fixed across all three candidate trials; deficiency 2 was a mis-specified scenario and is withdrawn. The candidate arm scores 24/24 in all three trials versus a baseline of 20–23/24. The improvement is consistent across trials in this sample, but three trials per arm at temperature 0.2 is still a small sample, and the deterministic checks are shallow. This is evidence of behavior change, not proof of sales effectiveness. Kyrgyz and mixed turns still need native-speaker rubric review.

## Remaining problems (not fixed)

1. **No rubric scores.** `tests/RUBRIC.md` dimensions (truth, consent, diagnosis, language, integrity, efficiency) are unjudged; Kyrgyz/mixed turns need a native speaker.
2. **Baseline-only residuals** (may recur in candidate on other seeds): L-R06 (no terms to a ready buyer), L-K08 (calling support a "guarantee").
3. **Shallow checks.** Phrase lists remain a proxy; several were widened during this evaluation and need Kyrgyz-speaker review before being treated as quality evidence.
4. **No tool integration.** Bookings, payments, invoices, and handoffs are never confirmed by a tool (all adapters except `passport.lookup` are `not_implemented` in the Daniyar passports).
5. **Small sample.** Three trials per arm; the language and discovery verdicts should be re-run with more trials before they are treated as stable.
