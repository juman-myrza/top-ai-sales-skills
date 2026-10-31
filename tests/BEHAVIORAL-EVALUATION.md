# Behavioral Evaluation Design

**Status:** design only. Nothing in this document has been run in this repository. No live model, no tool adapter, and no sales outcome have been measured here.

The deterministic checker in [`../scripts/evaluate_responses.py`](../scripts/evaluate_responses.py) answers a narrow question: did a recorded turn contain the required facts and avoid the forbidden claims? It cannot tell whether the agent made a good decision. This document describes the run that would be needed before any effectiveness claim.

---

## 1. What must be compared

Do not compare "skills" against "no skills" on a single prompt. Compare the artifacts the repository actually ships:

| Arm | Contents |
|---|---|
| Baseline A | A generic sales system prompt with the same product facts |
| Baseline B | The current published skills plus passport |
| Candidate | The revised skills plus passport |
| Ablation | The passport retrieval only, no skill body |

Run the same scenario corpus and the same tool fixtures against every arm. Report the differences, not a single number.

---

## 2. Trial design

- **Model(s):** at least two named models, pinned to a version. Model behavior changes between releases.
- **Trials:** at least three independent runs per scenario per arm, with a fixed but varied seed.
- **Ordering:** randomize the presentation order to reduce drift.
- **Control for context:** identical passport version, identical fixtures, identical system prompt except for the arm.
- **Record everything:** the full response, the tool calls with statuses, the token usage, and the latency.

A single trial is an anecdote. A model that passes once and fails once is not "safe".

---

## 3. Judging

Use [`RUBRIC.md`](RUBRIC.md) with two independent judges plus adjudication, or one judge (human or model) plus a human review of every hard fail.

- Score the seven weighted dimensions plus the `recommendation`, `barrier`, and `progression` sub-dimensions where they apply.
- Any hard fail makes the whole run fail for that scenario, regardless of the total.
- Record a verbatim evidence quote for every score.
- For Kyrgyz and mixed-language turns, a qualified native speaker must judge. A model judge must not score language quality it cannot verify.
- Measure inter-rater agreement before trusting an average.

Do not let a model judge certify truthfulness or legality. Those require a source and, for legal terms, a qualified reviewer.

---

## 4. What to measure beyond pass rate

| Metric | Why |
|---|---|
| Hard-fail rate by type | Fabrication, false confirmation, unauthorized concession, pressure after refusal |
| Wrong-fact rate | A confident statement that contradicts the passport or a tool result |
| Escalation precision | Correct escalations versus avoidable ones versus missed ones |
| Recommendation rate | How often a sufficient-evidence turn ends in a recommendation instead of another question |
| Barrier-adaptation rate | Whether the move matches the diagnosed barrier |
| Scoped-refusal handling | Whether a "no call" is treated as "no call", not "no offer" and not ignored |
| Tool-claim integrity | Success claims with no confirming result |
| Turn efficiency | Questions asked before an answer; questions after enough evidence |
| Opt-out and complaint handling | Immediate, permanent compliance with a stop |
| Cost and latency | A safe answer that takes two minutes may still be unusable |

---

## 5. What this cannot establish

- **Sales effectiveness.** A rubric pass is not conversion, retention, or revenue. That needs a field experiment with a control, guardrails, and harm monitoring.
- **Legal compliance.** Consent, refund, consumer-cooling-off, and recording rules are jurisdiction-specific and require counsel.
- **Adapter behavior.** The scenarios use test doubles. Only contract tests against a real adapter exercise idempotency, webhooks, and races.
- **Long-horizon stability.** The corpus is mostly one or two turns. A 20-turn conversation can drift even when every single turn passes.
- **Language quality.** Only a native speaker can certify the Russian and Kyrgyz copy.

---

## 6. Minimum run before any public effectiveness claim

1. Implement at least the `passport.lookup` adapter against the contract and run its contract tests.
2. Run all 57 scenarios against two named models, three trials each, on the baseline and candidate arms.
3. Blind-score with two judges; adjudicate disagreements; report hard-fail counts separately from averages.
4. Have a native Russian/Kyrgyz speaker review every non-English turn.
5. Publish the raw responses and the scoring sheet, with the scenario corpus and passport versions.
6. Only then run a bounded field pilot with a control group, an opt-out/complaint guardrail, and a pre-registered primary metric.

Until then, the only honest statement is the one in the [README](../README.md): a carefully constrained design and a structural test suite, with no demonstrated sales superiority or production safety.
