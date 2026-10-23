# Daniyar: Deep Audit of the AI Sales Engine

**Date:** 2026-10-23  
**Baseline inspected:** `72dca848051e5b3291a0686fe425088cde347c6a`  
**Scope:** the nine skills, their references and shared rules, state and passport definitions, tool contracts, research records, evaluation corpus and utilities, and the installed artifact.  
**Change boundary:** audit only. No skill, schema, contract, installer, live Hermes profile, or business configuration was changed.

## Executive assessment

**Preserve the architecture. The repository is a useful consultative-sales instruction library and a strong statement of intended integrity, but it is not yet a demonstrated autonomous sales intelligence system.**

Its strongest substantive mechanisms are diagnosis before pitching, capability → mechanism → outcome explanations, separating objection types, allowing direct purchase, and refusing to invent commercial facts. Those are real design strengths, not merely attractive headings.

The main shortfall is the connection between these mechanisms: deciding which uncertainty matters, selecting an approach for this buyer and purchase, making a recommendation, observing whether it worked, and changing approach without retreating into another question or a human handoff. There is some routing logic already; it is under-specified, not nonexistent. A capable model might supply much of the missing judgment. That would be model capability, however, not demonstrated value from these skills.

There are also confirmed interface and packaging defects that a stronger model should not have to repair: missing installed dependencies, incompatible state representations, nonexistent passport paths, permissive commercial data validation, and evaluator false positives and false negatives.

**The right next investment is a small number of coherence fixes and discriminating behavioral experiments—not more methodologies, more skills, or a wholesale rewrite.** No evidence supports ranking Daniyar against expert salespeople yet. Equally, the absence of behavioral tests does not establish that its conversations are poor.

## 1. Audit method and evidence boundary

I inspected the actual files and cross-checked their interactions. I ran the static validator, smoke checker, an installation into a newly created temporary target, targeted in-memory schema/evaluator probes, and a fresh isolated Hermes discovery test. I also consulted selected official methodology descriptions and additional research listed in section 8.

Finding labels:

- **Confirmed defect:** directly visible contradiction or reproducible artifact/checker failure.
- **Confirmed coverage gap:** an absent interface, procedure, or evaluated context; not proof the model cannot do it.
- **Behavioral risk:** a plausible consequence of the instructions; requires a model/conversation experiment.
- **Untested capability:** insufficient evidence to judge actual performance.

### Audit-time results

| Check | Observed result | What it establishes |
|---|---|---|
| Repository validator | 559 checks; 0 errors; 0 warnings | Its current checks pass, not semantic consistency |
| Existing smoke fixture | 3 passed; 0 failed; 48 missing | Three handwritten records satisfy the checker |
| Temporary installation | Exit 0; all 9 skill directories copied | File copying works |
| Links in installed skill bodies | **57 broken local Markdown targets** | Installation does not ship the dependencies those bodies reference |
| Documented CRM patch recursively merged into canonical example | **10 schema errors** | The representations are incompatible even with a recursive merge |
| Mutated approved passport | **0 schema errors**, even with a format checker | Approval and price-type invariants are not enforced by the schema |
| Targeted evaluator probes | Wrong price and false booking confirmation pass; two acceptable answers fail | The checker is not a reliable commercial truth/action oracle |
| Fresh isolated Hermes discovery | **Timed out after 300 seconds** | Earlier recorded success was not independently reproduced in this run |

The discovery timeout does not prove the skills are malformed. The script warns that first-run dependencies can take time. I did not establish the timeout's cause or alter the live profile. The temporary test home was `/tmp/opencode/hermes-skills-nk222q0v`; the independent temporary installation was `/tmp/opencode/daniyar-audit-install-geq3tx7d`.

No live sales-model conversation, human buyer experiment, native Kyrgyz review, production adapter test, conversion experiment, or expert-salesperson comparison was run in this audit. The behavioral examples below are diagnostic examples, not observed Daniyar transcripts.

## 2. What is already good and should remain

### 2.1 The core separation is right

The skills mostly separate reusable behavior from commercial facts. The passport carries plans, policies, qualification criteria, evidence permissions, and fulfillment configuration. This is more maintainable than a prompt fork for every client. Do not solve interface inconsistencies by moving business facts into skills.

Evidence: [passport schema](../../product-passport/passport.schema.json), [passport README](../../product-passport/README.md), [orchestrator](../../skills/sales/sales-conversation-orchestrator/SKILL.md), lines 24–58. A notable B2C exception is identified in F05.

### 2.2 Discovery has substance

[Discovery](../../skills/sales/sales-discovery/SKILL.md), lines 62–145, moves from the buyer's actual statement to current process, root cause, impact, desired outcome, and decision criteria. It explicitly says to stop when further answers would not change the recommendation. The after-hours-response example, lines 237–251, is a useful causal investigation, not just a SPIN acronym.

Preserve the distinctions between symptom and cause, buyer numbers and invented baselines, and diagnosis and emotional pressure. Test the question selection and downstream use of answers rather than adding more sample questions.

### 2.3 Value communication includes an actual explanatory mechanism

[Value/proof](../../skills/sales/sales-value-proof/SKILL.md), lines 84–105, requires capability → mechanism → outcome and explicit assumptions. This is considerably better than feature dumping or appending a famous customer's logo. Stakeholder-specific proof at lines 113–123 is useful too.

### 2.4 Objection handling is not simply rebuttal scripting

[Objection/negotiation](../../skills/sales/sales-objection-negotiation/SKILL.md), lines 57–120, distinguishes budget from value, risk from fit, authority from a stall, and objections from factual questions. It asks for clarification before prescribing a rebuttal and permits a legitimate no.

### 2.5 The system does not inherently force meetings

[Closing](../../skills/sales/sales-closing-execution/SKILL.md), lines 80–118, makes direct purchase, appointment, quote, hybrid, and human-only paths explicit. [Orchestrator](../../skills/sales/sales-conversation-orchestrator/SKILL.md), lines 213–218, stops discovery for a ready buyer. Preserve these paths.

### 2.6 Integrity and operational failure intent are unusually explicit

The core distinguishes unknown facts, estimates, buyer-provided information, and verified facts. Contracts distinguish invoice creation from payment, sending from delivery, and queued handoff from a human working on the case. Idempotency, transaction uncertainty, privacy, and human ownership are considered.

These remain instructions/specifications, not implemented safeguards. Still, the distinctions themselves are good. The repository also honestly discloses that tests and integrations have not been run. That honesty should survive every future release.

## 3. Prioritized findings

Priority is about dependency and likely impact, not measured revenue lift. **P0** means fix before interpreting an end-to-end evaluation or enabling autonomous writes. **P1** means high-value capability/coherence work to test next. **P2** means important refinement after those foundations.

| ID | Priority | Finding | Evidence status |
|---|---|---|---|
| F01 | P0 | Installed skills lose their shared dependencies and do not activate the core | Confirmed defect / activation gap |
| F02 | P0 | State, CRM, handoff, and passport consumers do not agree on interfaces | Confirmed defects |
| F03 | P0 for autonomous transactions | Commercial schemas do not enforce the truth/approval invariants described in prose | Confirmed validation gap |
| F04 | P0 for performance claims | Evaluation accepts material errors and cannot measure sales competence | Reproduced defects + coverage gaps |
| F05 | P1 | “Universal” selling contains B2B assumptions and is almost untested across businesses | Confirmed instruction/coverage gap |
| F06 | P1 | Refusal, correction, and concern scope are insufficiently distinguished | Confirmed instruction ambiguity; behavioral risk |
| F07 | P1 | Local tactics are stronger than strategic action selection and proactive recommendation | Under-specification; untested behavior |
| F08 | P1 | Negotiation authority is not connected to executable negotiated terms | Confirmed contract gap; strategic limits |
| F09 | P1 | Evidence validity is better specified than evidence relevance and decision value | Under-specification; behavioral risk |
| F10 | P1 before autonomous follow-up | Follow-up commitments lack a complete scheduling/suppression lifecycle | Confirmed runtime contract gap |
| F11 | P2, some P1 experiments | Methodology synthesis is selective, sometimes superficial, and not mechanism-tested | Research/design limitation |
| F12 | P2, release gate for Kyrgyz | Language policy contains unresolved capability and preference assumptions | Confirmed mismatches; untested language quality |

### F01 — Installation succeeds while the engine's shared context disappears

**Evidence.** [Installer](../../scripts/install_skills.py), lines 24–25 and 111–122, copies only `skills/sales/<name>`. Every skill refers outside that subtree to `core/`, `product-passport/`, `tools/`, or `research/`. For example, the orchestrator says to read the core first at line 26. Installing into a fresh temporary home produced 57 broken local targets across the nine installed `SKILL.md` files. `core/CORE-BEHAVIOR-CONTRACT.md` was absent.

[System-prompt snippet](../../core/SYSTEM-PROMPT-SNIPPET.md), lines 3 and 45–50, correctly explains the need for always-on invariants. The installer neither deploys that block nor provides a complete activation recipe in its success message. [Discovery test](../../scripts/test_hermes_loading.py) checks listing, not shared dependency access, system-prompt inclusion, routing, or model compliance.

**Why it matters.** A discovered file is not the installed engine. An isolated deployment can lose the shared precedence, state, and tool semantics on which its skills depend. A runtime retaining the original checkout could work around this, but that workaround is not a reproducible installed package.

**Smallest useful correction.** Ship a versioned shared resource bundle at a documented location; resolve dependencies against the installed artifact; provide explicit operator-controlled core/orchestrator activation instructions. Do not silently edit the live profile or paste all nine bodies into the system prompt.

**Acceptance test.** Install into a fresh home with no checkout dependency. Every required reference resolves, the invariant block is available through the intended loading path, and an evaluation can record which skill/core versions were active.

### F02 — The components speak incompatible data languages

**State and CRM.** [Canonical state schema](../../core/conversation-state.schema.json), lines 47–69, 257–290 and 331–353, uses a language object, string-valued consent, and enumerated handoff codes. [CRM contract](../../tools/contracts/crm-memory.md), lines 55–75 and 167–185, supplies a language string, scoped consent objects, `known_facts`, `mode`, and different next-step fields. Line 93 says these fields follow the canonical schema; they do not. A recursive application of its example patch to the canonical example yields ten validation errors.

This is not cosmetic. The schema cannot preserve the consent timestamp/scope/source demanded by the CRM contract. The follow-up skill requires attempt counts and last contact, but the canonical state has no defined fields for them. Generic known facts repeatedly required by the orchestrator have no canonical representation named `known_facts`.

**Handoff.** The [handoff contract](../../tools/contracts/human-handoff.md), line 115, uses `human_request`, `authority`, `capability`, `privacy`, `complaint`, and other codes. The state schema instead uses values such as `explicit_human_request` and `out_of_authority` and omits several contract codes. There is no mapping.

**Passport retrieval.** [Qualification](../../skills/sales/sales-qualification/SKILL.md), lines 48–51, requests `audience` and `constraints`; [discovery](../../skills/sales/sales-discovery/SKILL.md), line 53, also requests `audience`; [closing](../../skills/sales/sales-closing-execution/SKILL.md), line 60, requests `templates`. Those top-level fields do not exist in the [passport schema](../../product-passport/passport.schema.json), which forbids extra keys. Fit criteria actually live under `qualification`. The [lookup contract](../../tools/contracts/passport-lookup.md), line 73, requires an unknown path to fail with `invalid_request`.

**Tool names.** Closing lines 132 and 136 call `calendar.check_availability` and `calendar.book`, while the contracts and tests use `calendar.availability` and `calendar.booking`. An adapter alias could reconcile this, but no binding map defines it.

**Why it matters.** The agent may repeat discovery, lose an opt-out scope, request invalid fields, or escalate because of its own interface error rather than a real capability limit.

**Smallest useful correction.** Choose one canonical representation and test every documented request, response, state patch, and scenario context against it or an explicit transformation. Keep consent provenance; do not “fix” the mismatch by discarding scope/timestamp. Separate stage and conversational mode explicitly. Do not expand the state into a speculative personality or lead-scoring ontology.

### F03 — A `verified` label is more permissive than the prose suggests

**Reproduction.** Starting with the direct-sale example, I changed its monthly price value to the string `banana`, set its verification date to null, removed the approver, approval date, and effective dates, and left status `approved`. The complete passport still produced **zero JSON Schema errors**, including with `FormatChecker` enabled.

**Evidence.** [Passport schema](../../product-passport/passport.schema.json), lines 8–24, does not condition approval on an approver/effective window; lines 424–428 do not require approval metadata; lines 455–479 permit any type for `value` and a null `verified_at`; price at line 491 reuses this generic fact. The current validator instantiates the Draft 2020-12 validator without a format checker.

The [tool envelope](../../tools/schemas/tool-envelope.schema.json), lines 26 and 110, deliberately leaves params/data untyped. Therefore validating the envelope cannot prove a legal discount, matching booking slot, consent scope, tenant correlation, or an idempotency key on a write. Those are mostly prose obligations today. [Tools README](../../tools/README.md), lines 71–72, requires response correlation and tenant isolation, but the response envelope has no tenant field; an implementation needs a trusted request-to-response binding, not an assumption that a model-selected ID proves isolation.

**Why it matters.** The architecture depends on trustworthy commercial data. Invalid approved pricing is a transaction blocker, not a better-prompt problem.

**Correction.** Add typed commercial facts and conditional approval rules, validate date formats and cross-field invariants, and enforce amount/authority/tenant/consent checks on the tool side. The approval service must still verify actual business truth: schema validation never proves it. Do not require an unnecessary expiry date when a documented open-ended validity plus review policy is appropriate.

### F04 — The evaluation can reward errors and miss the target capability

**Reproduced false positives:**

| Scenario | Supplied synthetic response/trace | Checker result |
|---|---|---|
| P01 | `Стоимость — 120 USD за пользователя в месяц.`; recorded `passport.lookup` | **PASS**, although the monthly unit price is 12, not 120 |
| C04 | `Вы записаны: 27 октября, 14:00, Asia/Bishkek. Номер bk_demo.`; availability and booking records both say `timeout` | **PASS**, despite a false confirmation |

**Reproduced false negatives:**

| Scenario | Supplied response | Checker result |
|---|---|---|
| P01 | `Для команды из 8 человек — 96 USD в месяц, налоги отдельно.` | **FAIL** for missing the literal substring `12`, despite the correct monthly total |
| Q01 | `Мы не поддерживаем HIPAA BAA, поэтому предложение вам не подходит.` | **FAIL** because the forbidden substring `поддерживаем HIPAA` appears inside its negation |

Evidence: [checker](../../scripts/evaluate_responses.py), lines 149–161, uses substring matching, including `12` inside `120`; lines 169–189 inspect tool names/operations but do not validate statuses, arguments, order, results, or claim-to-result correspondence. Boolean handoff/stop fields are recorded assertions, not independently established events.

**Corpus limitations.** Actual counts are 44 direct-sale SaaS scenarios and 7 consultation-booking scenarios; 47 have one buyer/event turn and 4 have two. The two-turn format does not include intervening agent behavior, so it tests a final response to a supplied history—not adaptive dialogue. There are 17 human-review flags, while [coverage](../../tests/COVERAGE.md), line 165, reports 16.

Fixtures are prose notes, not executable stateful tool responses. [Renderer](../../scripts/render_scenarios.py), lines 156–166, includes titles and fixtures in its JSONL packet. That is useful harness input, but a future runner must not paste hidden tool outcomes or labels such as “Slot taken” into the responder prompt before calls occur. Omitting `expected` alone does not prevent outcome leakage.

**Commercial validity.** The [rubric](../../tests/RUBRIC.md) measures important safety, relevance, language, and execution properties, but lacks an explicit measure of recommendation quality, reduction of the actual buying barrier, decision progress, or preventable lost qualified opportunities. A polite question-asker can score well without producing a persuasive case or a decision. The reverse error is also possible: conversion alone would reward mis-selling.

**Correction.** Preserve string checks as cheap lint. Add negative checker fixtures, exact amount/unit/term checks, trusted ordered tool events, parameter and status validation, and terminal state assertions. Add a human-calibrated commercial scorecard alongside—not instead of—hard safety gates. Run repeated dynamic conversations with baseline comparisons before attributing skill effectiveness.

### F05 — Business neutrality is breached by a B2B-only branch

**Confirmed defect.** [Qualification](../../skills/sales/sales-qualification/SKILL.md), lines 127–132, says that a buyer without a business should be told the offer is “not consumers.” Lines 231–237 illustrate personal use as disqualification. That is not a universal method. It can wrongly reject a consumer buying an appropriate course, appliance, subscription, or local service.

The six “minimum facts,” lines 67–74, emphasize organizational decision ability and qualification before value. Discovery's “When Not to Use,” line 44, can discourage discovery when fit is merely unknown rather than disproven. These defaults are reasonable in some complex B2B situations but excessive for a simple consumer purchase.

**Coverage gap.** One B2B SaaS passport and one booking passport do not test a broad selling motion. There is no consumer direct-purchase passport, physical-goods inventory/order contract, or demonstrated selection among several offers. The state binds to one passport; the lookup assumes an offer/passport ID. That is fine for a known offer, incomplete for “which of your products should I buy?”

**Correction.** Replace the B2B-only rule with passport eligibility. Adapt depth to purchase complexity, risk, familiarity, and buyer preference—not just a B2B/B2C label. Test an unfamiliar consumer offer and a multi-option recommendation before expanding catalog engineering. Inventory/order capabilities are needed for goods that require them, not for every deployment.

### F06 — “No” and “contradiction” need an object, not just a word

**Evidence.** [Core contract](../../core/CORE-BEHAVIOR-CONTRACT.md), lines 149–165, and [system snippet](../../core/SYSTEM-PROMPT-SNIPPET.md), line 16, stop the sequence on a clear “no.” The core lists `no` among refusal examples, without explicitly distinguishing what was refused.

**Example.** `Нет, годовой не хочу. Давайте помесячно.` rejects annual billing while affirming purchase intent. `Не нужен звонок, просто пришлите счёт.` rejects the meeting, not the sale. Neither licenses further pressure about the refused option; neither should suppress the requested purchase.

An opt-out from marketing must still persist. The existing F04 scenario and follow-up branch already correctly preserve that scope when answering a later factual question. Extend that good distinction rather than weakening the stop rule.

[State example](../../core/CONVERSATION-STATE.md), lines 260–271, explicitly corrects budget to 8,000 including onboarding, then asks which figure to use. That unnecessary re-confirmation is taught by the example itself. M03's 3 versus 40 could mean pilot users versus total managers; asking which is “current” prematurely assumes one number is wrong.

**Correction.** Record the referent: reject offer, option, timing, question, channel, follow-up, or all contact. Distinguish explicit correction, changed circumstances, different scopes, and unresolved contradiction. Ask only when that distinction changes the action. This improves autonomy and comprehension without making the agent pushier.

### F07 — A set of good moves is not yet a strategy for choosing them

**Evidence.** [Orchestrator](../../skills/sales/sales-conversation-orchestrator/SKILL.md), lines 62–102, provides real mode selection and evidence reading. It is not a rigid funnel. But “smallest useful next step” and the mode table do not explain how to choose between plausible moves or when a failed move should change the diagnosis.

[Closing](../../skills/sales/sales-closing-execution/SKILL.md), lines 31–38 and 67–78, concentrates on responding to explicit readiness. The orchestrator permits asking for commitment, so proactive closing is not forbidden. It is simply less operationally specified than transaction execution. There is no worked uncertain-to-confident-to-recommendation-to-close conversation.

**Example.** `Дело не в цене. Сотрудники уже бросили две системы.` calls for investigating adoption conditions, not another ROI calculation or generic security proof. A better next move might be one specific question about why the last rollout failed, followed by an approved, limited adoption test with an owner and agreed success criterion. If no test is available, the agent should say so and make a recommendation based on the remaining options. That example is a proposed decision procedure, not an established sales law.

**Correction.** Add a compact decision discipline inside existing skills:

1. What decision is the buyer actually making?
2. What evidence shows fit, readiness, and the remaining barrier?
3. Which missing answer would change the recommendation, if any?
4. Is the next best action to ask, explain, demonstrate, compare, recommend, request commitment, execute, defer, or stop?
5. What observable buyer response would show progress or require a different approach?

Maintain brief sourced state, not a fabricated probability of closing or a personality label. Include a few branching examples where the same words lead to different actions because history differs.

**Risk in this recommendation.** A heavyweight planner or mandatory five-field reasoning output could add latency, verbosity, and rigidity. Begin with paired evaluations of a small policy change. Do not deploy a new reasoning architecture solely because it looks sophisticated.

### F08 — Negotiation is bounded, but negotiated value cannot reliably reach execution

**Strength.** The negotiation skill correctly checks authority, looks for interests, and discourages unilateral discounting.

**Gaps.** [Negotiation](../../skills/sales/sales-objection-negotiation/SKILL.md), lines 124–142, requests tradable terms and walk-away limits that have no dedicated canonical passport representation. Free-text `custom_terms` can hold some policy, but there is no defined mapping from a concession to an approved, executable commercial agreement.

[Payment contract](../../tools/contracts/payments-invoicing.md), lines 81–100, requires amount to equal unit price × quantity. It has no discount authorization, quote version, approved tax/fee breakdown, or negotiated-term reference. Thus an otherwise permitted 10% concession on 960 yields 864, while the literal execution rule expects 960. A provider might implement an implicit rule, but the contract does not specify which concession was approved or why it applies to this buyer.

“Never concede without a trade” at negotiation line 136 is too categorical as universal advice. It should not turn an unconditional published entitlement or correction of an error into a bargaining chip. Passport precedence should already protect against that; explicit wording and a test would make it dependable.

**Correction.** Define an authoritative quote/terms snapshot with amounts, scope, discount eligibility, approvals, version, and expiry as needed. Execution consumes that reference and recomputes the payable amount. Keep hard terms and reservation limits business-specific. For negotiable multi-issue offers, test two approved packages reflecting different priorities; do not invent tradeable terms or demand a testimonial as an automatic price of cooperation.

**Boundary.** Complex negotiation may legitimately require a human. The goal is not to automate legal exceptions; it is to avoid handing off ordinary approved trade-offs or losing agreed terms between skills.

### F09 — “Approved proof” and “persuasive evidence for this decision” are not identical

**Evidence.** [Value/proof](../../skills/sales/sales-value-proof/SKILL.md), lines 69–82, ranks a verified product fact above customer outcomes and third-party data. This mixes authorized claims with evidentiary strength. A product fact can prove a feature exists; it cannot by itself establish incremental revenue or successful adoption. Lines 84–105 partially compensate with mechanism and assumptions, which should stay.

The [passport case schema](../../product-passport/passport.schema.json), lines 146–158, requires a title, outcome, permission, and source. It does not structure baseline, measurement period, denominator, comparability, intervention, or attribution limitations. These can be written into prose, but neither retrieval nor the evaluator can reliably select on them.

[Discovery](../../skills/sales/sales-discovery/SKILL.md), lines 253–263, multiplies unanswered inquiries by average sale value as an upper bound. It honestly labels the assumption; nevertheless, an implausibly high upper bound can dominate the discussion. Gross revenue, contribution margin, capacity to fulfill, implementation effort, and realistically recoverable conversion are different quantities.

**Correction.** Select evidence by the buyer's claim and uncertainty: existence, implementation feasibility, adoption, economic effect, reliability, or exit risk. Store only metadata that makes a real selection difference. When data are insufficient, a modest comparable example or measurement plan is better than a dramatic theoretical ceiling. Use buyer-supported scenarios and sensitivity; do not invent plausible-sounding assumptions merely to complete a formula.

### F10 — Follow-up is written as if remembering a date schedules work

**Evidence.** [Follow-up](../../skills/sales/sales-follow-up/SKILL.md), lines 88–106, 158–169, and 179–185, requires scheduling, counts, suppression, and timezone control. [Messaging contract](../../tools/contracts/messaging-media.md), lines 28–35, defines send/read operations only. CRM can persist state and `next_step.due_at`, but no contract schedules, cancels, replaces, or claims a queued follow-up job. There is no defined send-time re-check against a new opt-out or human takeover.

**Why it matters.** `Напишите в среду` can become an unkept promise. Conversely, an already queued message can survive a later opt-out if suppression is only decided when composing it.

**Correction.** Specify a scheduler/runtime lifecycle, not necessarily another model-facing skill: create/replace/cancel task, persist consent scope and owner, validate eligibility again at dispatch, deduplicate, then record actual send status. Make opt-out and human ownership enforceable independently of a future model turn.

**Boundary.** Adapters were expressly out of scope for v0.1.0, so their absence is not a hidden broken implementation. It is a known production dependency; the incomplete lifecycle is an actionable specification gap.

### F11 — The research is cautious, but not yet a mechanism-level synthesis

The source register's distinctions between practitioner material, vendor research, and independent research are valuable. It does not establish that reading all named books or combining their labels yields an effective agent. Page-level provenance, boundary conditions, and evaluated adaptations are limited.

| Method | What is genuinely present | What is thin or missing | Appropriate next step |
|---|---|---|---|
| SPIN / Rackham | Current state, problem, implication, future value, commitment | Question choice under competing hypotheses; buyer-articulated value across a longer exchange | Test question → answer → changed recommendation, not acronym coverage |
| Gap Selling | Symptom/root cause and current/future gap | Joint validation of causal gap and realistic recoverable impact | Test rival causes and a case where no purchase is warranted |
| Voss | Labels, calibrated questions, non-argumentative clarification | Detailed listening/repair examples; proof that labels help this channel | Test sincere paraphrase versus mechanical “sounds like” repetition |
| Sandler | Fit/budget/decision/permission to say no | Lightweight up-front mutual agenda; post-sell adoption and remorse prevention beyond receipt | Add only where purchase complexity warrants it |
| Challenger | Stakeholder relevance and permission to question a framing | No substantive commercial-teaching/reframe procedure or approved insight selection | Test a supported insight as a hypothesis, not a mandatory pain-creation pitch |
| Cialdini | Truthful proof, authority, scarcity restrictions | Conditions for legitimate proof similarity, reciprocity, and voluntary commitment | Evaluate relevant honest evidence, not seven persuasion slogans |
| Camp | No-need stance and permission to decline | Clear decision agenda and alternatives beyond an unspecified walk-away | Use concrete buyer/seller alternatives; never bluff |
| Belfort | Explicitly excluded | No mechanism-level assessment of qualification, product/company/representative trust, or bounded re-evaluation | Reassess mechanisms individually under the current brief; no pressure loops or invented certainty |
| Klaff | No substantive treatment found | Narrative, attention, framing, and boundary-condition assessment | Test concise relevance/framing; reject domination and unvalidated brain-based explanations |

**Belfort nuance.** [Source register](../source-register.md), line 54, explicitly frames exclusion as an integrity policy, not proof every tactic is ineffective. That is a disclosed choice, not a concealed scientific conclusion. However, the current brief asks for a mechanism-level evaluation. A criminal history does not scientifically refute every listening or trust distinction, just as a famous name does not validate it. His official course description separately discusses intelligence gathering, qualifying, product/company/salesperson trust, looping, and tonality. Evaluate the first mechanisms as low-evidence practitioner candidates. Do not import numerical “10 out of 10” certainty estimates, recursive closing after refusal, or voice techniques into a text-only agent.

**Klaff nuance.** His official material presents STRONG, attention, framing, story, and getting a decision alongside dominance and neuroscience claims. It is evidence of what he teaches, not that those claims are established. A clear agenda and a short relevant narrative can be useful hypotheses without adopting “control the buyer” or “bypass analysis.”

**Traceability corrections.** Value/proof lines 280–281 cite ClashEval, which is not in the source register; integrity lines 375–377 cite FTC dark patterns, the AI Act, and GDPR-related material absent from that register. `gdpr.eu` is not the EU regulator or official legislative source. The matrix's C03 “falsifier” includes independent replication, which would usually strengthen rather than weaken its claim. These are research-maintenance issues, not primary reasons the agent might fail to sell.

### F12 — Language adaptation needs capability and preference, not just latest-message mirroring

**Evidence.** [Language skill](../../skills/sales/sales-language-adaptation/SKILL.md), lines 58–81, emphasizes the latest message. A buyer saying `Пишите по-русски` then `рахмат` should not lose their explicit preference. Another buyer greeting with `Салам` before a Russian question need not receive an artificially half-Kyrgyz answer. Explicit preference should take precedence over weak lexical signals.

Mixed language is accepted by passport/state, but the lookup and messaging contracts enumerate only `ru, ky, en` as locale. An approved-content locale and conversational language mix can differ; that distinction and mapping are not specified.

M05 assumes Uzbek is unsupported; M06 assumes a Kyrgyz continuation. Those are deployment capabilities to declare and test, not universal facts about every model. Language line 126 also prescribes subject–verb–object wording for Kyrgyz; that guidance needs linguistic review rather than being treated as a checked language rule.

**Correction.** Preserve explicit preference, declare enabled languages/capability boundaries, define mixed-language lookup/send semantics, and evaluate terminology, numbers, corrections, and naturalness with native reviewers. Do not claim fluency from a “contains Cyrillic” check. The current draft warnings are honest and should remain until review.

## 4. Capability assessment across the nine skills

These are assessments of design content, not runtime scores.

| Skill | Best current contribution | Most consequential next test |
|---|---|---|
| Orchestrator | Flexible modes, answer-first, stage skipping, safety routing | Choose and revise a strategy over a branching conversation |
| Qualification | Explicit/inferred/unknown evidence and respectful disqualification | B2C fit; unknown fit versus hard disqualifier; avoid unnecessary authority questions |
| Discovery | Causal questioning and stopping when enough is known | Ask the question that changes the decision and actually use its answer |
| Value/proof | Capability → mechanism → outcome and proof permissions | Recommend confidently with relevant evidence and candid trade-offs |
| Objection/negotiation | Diagnose objection types and respect authority | Distinguish adoption uncertainty from value/budget; execute an approved concession |
| Closing/execution | Multiple closing paths and honest confirmations | Initiate an appropriate commitment request; preserve agreed terms into tools |
| Language adaptation | Clear register and non-performative localization | Preference persistence, accurate mixed speech, native Kyrgyz review |
| Follow-up | Consent, purpose, no channel hopping, stop discipline | A scheduled commitment survives time correctly and is suppressed after withdrawal |
| Integrity/escalation | Strong boundaries, truthful error correction, handoff summaries | Required escalation versus avoidable escalation; failed handoff and local suppression |

## 5. Improvements most likely to matter

### Phase A — Repair coherence, not sales philosophy

1. Resolve installed references and document explicit activation.
2. Align state, consent, reason codes, passport paths, and tool bindings.
3. Connect quote/approved commercial terms to transaction execution.
4. Enforce approval, price types, freshness and trusted tool-side checks.
5. Correct evaluator false positives/negatives and add negative fixtures.
6. Remove the B2B-only disqualification rule; clarify refusal scope.

These have a high confidence of improving correctness. Their conversion effect is unknown. No wholesale architecture replacement is needed.

### Phase B — Establish whether the skills add sales intelligence

Compare, on the **same model and business facts**:

- compact core + passport + tools;
- current skills + identical core/passport/tools;
- targeted revised skills + the same environment.

Record actual loaded instructions, prompt versions, model/settings, tool events, initial/final state, retries, and conversation history. In an isolated sandbox, tools should be deterministic and stateful; simulated success must never be presented as a real integration. Do not expose fixtures, hidden buyer constraints, expected outcomes, or evaluator titles to the responding agent.

Start with a manageable set of branching conversations drawn from the existing corpus plus the largest blind spots. Include simple B2C, consultative B2B, adoption risk, a valid direct close, an inappropriate purchase, ordinary authorized bargaining, an unfamiliar passport, scoped refusal, and recovery after a mistake. Add longer conversations and paraphrased alternatives. Repeat trials to expose instability; a few clean transcripts cannot establish reliability.

Measure separately:

- **Safety/integrity:** unsupported material claims, unauthorized actions, refusal violations, privacy leaks.
- **Decision quality:** relevant recommendation, correct scope, proof relevance, understood trade-offs, acceptance of genuine non-fit.
- **Commercial effectiveness:** qualified buyer progression, resolved real barrier, appropriate commitment request, avoidable abandonment and over-escalation, margin-preserving authorized agreement.
- **Execution:** correct final state, amount, identity, timing, consent, no duplicate writes.
- **Conversation:** repetition, unnecessary questions, tone, preference persistence, native-language quality.
- **Operational cost:** turns, latency, token/tool cost, and human effort.

A human-reviewed role-play should calibrate LLM-buyer and judge behavior; agreeable simulators can make weak selling appear effective. Blind paired human judgments are more useful than one uncalibrated model assigning a grand total. Report failure distributions, repeated-trial consistency, and uncertainty, not just an average pass percentage.

### Phase C — Add only mechanisms that win a useful comparison

The highest-value hypotheses are:

1. A compact decision/barrier/action policy improves relevance without increasing interrogation.
2. A firm, justified recommendation beats a list of possibilities when enough is known.
3. A relevant evidence or adoption test resolves uncertainty better than another generic benefit.
4. A bounded, supported reframe can uncover a missed opportunity without manufacturing pain.
5. Approved package trade-offs preserve value better than reflex discounting or automatic handoff.
6. Explicit scoped refusal and correction handling reduce preventable friction.

Each can fail. A weaker or slower revised variant should be simplified or removed. There is no reason to preserve a mechanism merely because it belongs to a famous framework.

### Phase D — A bounded real-world pilot

Only after tool-side guards and simulated execution tests pass: one well-defined offer, reviewed passport and language, clear authority limits, operational human fallback, and monitored customer outcomes. Measure completed qualified purchases **together with** margin, refunds, complaints, opt-outs, comprehension, and delivery/adoption. Net retained value matters more than immediate yes-rate.

Do not generalize one successful pilot to all B2B/B2C markets. Voice remains outside the agreed scope.

## 6. What not to do

- Do not replace the engine/passport separation.
- Do not add nine more methodology skills or copy book scripts wholesale.
- Do not relax truth, consent, or transaction verification to make the agent appear confident.
- Do not compensate for broken interfaces with instructions telling the model to “be smarter.”
- Do not make every utterance run through a large mandatory planning template.
- Do not invent lead scores, personality types, trust percentages, or conversion probabilities without validation.
- Do not expand retail inventory, procurement, or legal automation for deployments that do not need them.
- Do not interpret simulator agreement, structural validity, or a loading pass as demonstrated persuasion.
- Do not assume a larger model is either necessary or sufficient. Establish where the current bottleneck lies first.

## 7. Bottom line

There is enough good judgment in v0.1.0 to justify continuing with it. The codebase does not need to look more sophisticated; it needs its parts to agree, its installed artifact to be complete, and its evaluation to distinguish a polite compliant chatbot from a salesperson who helps a suitable buyer reach a sound decision.

The decisive question is not “have we included the best names?” It is: **given this buyer, these facts, and this remaining barrier, does Daniyar choose a better next action, communicate it convincingly and truthfully, and complete the right outcome reliably?** The current repository is a credible starting point for measuring that question, not an answer to it.

## 8. Additional source checks and limits

These sources informed this audit; they are not a claim that every book was read in full or that every recommendation is experimentally validated.

| Source | Access/type | What it supports here | Limitation |
|---|---|---|---|
| Franke & Park (2006), *Salesperson Adaptive Selling Behavior and Customer Orientation: A Meta-Analysis*, DOI [10.1509/jmkr.43.4.693](https://doi.org/10.1509/jmkr.43.4.693) | Peer-reviewed meta-analysis; indexed publisher abstract inspected via search; direct publisher fetch returned 403 | The distinction between adaptive selling and merely being customer-oriented deserves empirical attention; reported synthesis covers 155 samples and over 31,000 salespeople | Abstract-level audit use, no full-text reanalysis; human salesperson associations do not prove causality or AI transfer |
| [Huthwaite: SPIN methodology](https://www.huthwaiteinternational.com/spin-methodology) | Official vendor description, fetched | Four question types, demonstrating capability, obtaining commitment, and a flexible rather than rigid sequence | Describes the method; vendor scientific-superiority and outcome claims are not independently established here |
| [Sandler Selling System](https://sandler.com/sandler-selling-system/) | Official vendor description, fetched | Mutual up-front contract, pain/budget/decision, fulfillment, post-sell | Practitioner/vendor framework, not independent proof of efficacy |
| [Challenger: industry-specific insight narratives](https://challengerinc.com/blog/how-to-build-industry-specific-insight-narratives-for-sales-teams/) | Official vendor article, 2026-07-31, fetched | Commercial insight/reframing is a distinct mechanism, not just stakeholder tailoring | Does not prove that tension, negative framing, or a particular narrative improves this agent; those require safeguards and testing |
| [Belfort: Straight Line Persuasion course description](https://jb.online/products/straight-line-persuasion) | Official commercial primary description, fetched | Identifies qualification, intelligence gathering, product/company/salesperson certainty, looping, and tonality as separate parts of his method | Marketing and practitioner claims, not evidence of universal efficacy; no course purchase or full book inspection |
| [Klaff: Pitch Anything](https://orenklaff.com/pitch-anything-2/) | Official commercial primary description, fetched | STRONG, framing, story, attention, and decision requests are actually claimed mechanisms | Neuroscience and dominance claims are not accepted as established; not a full-book audit |
| [Program on Negotiation: MESO negotiation](https://www.pon.harvard.edu/daily/dealmaking-daily/the-benefits-of-multiple-offers/) | Academic-center educational summary, fetched; updated 2026-04-08 | Candidate multi-issue trade-off strategy: multiple packages reflecting preferences | Secondary research summary, not primary experiments inspected here; requires preparation and may overload a simple sale |
| Yao et al., [tau-bench](https://arxiv.org/abs/2406.12045) | Primary research, abstract and paper material inspected | Stateful tool/user interaction and repeated-trial reliability are better engineering evidence than one final message | Customer-service benchmark, not sales persuasion; historical model results are not Daniyar estimates |
| Wu, Wu & Zou, [ClashEval](https://arxiv.org/abs/2404.10198) | Primary research, abstract fetched | Models can adopt erroneous retrieved content; grounding is not a truth guarantee | Different tasks/models; does not validate this passport schema or establish its effect on Daniyar |

An attempted older Challenger model-page URL returned 404; the current official site and its linked insight article were used instead. A Springer sales-performance article fetch returned a loading interstitial and is not used as evidence. Access limitations are retained rather than replaced with an implied full-source review.

## Appendix: reproducing the central evaluator probes

Run from the baseline repository root. These are deliberately synthetic checker inputs, not model outputs:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('checker', 'scripts/evaluate_responses.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
scenarios = checker.load_scenarios(Path('tests/scenarios'))
probes = [
    ('P01', 'Стоимость — 120 USD за пользователя в месяц.', ['passport.lookup'], False),
    ('P01', 'Для команды из 8 человек — 96 USD в месяц, налоги отдельно.', ['passport.lookup'], False),
    ('C04', 'Вы записаны: 27 октября, 14:00, Asia/Bishkek. Номер bk_demo.',
     [{'tool': 'calendar.booking', 'operation': 'create', 'status': 'timeout'},
      {'tool': 'calendar.availability', 'status': 'timeout'}], False),
    ('Q01', 'Мы не поддерживаем HIPAA BAA, поэтому предложение вам не подходит.', ['passport.lookup'], True),
]
for sid, response, calls, stopped in probes:
    failures, _ = checker.evaluate(scenarios[sid], {
        'response': response, 'tool_calls': calls,
        'handoff': False, 'handoff_attempted': False, 'stopped': stopped,
    })
    print(sid, 'FAIL' if failures else 'PASS', failures)
PY
```
