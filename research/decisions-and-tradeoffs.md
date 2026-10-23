# Decisions and Tradeoffs

**Status:** architecture decision record for v0.1.0  
**Date:** 2026-10-23  
**Context:** a universal, Hermes-compatible sales skill set that must work for a real business without hardcoded product facts, support Russian/Kyrgyz/mixed conversations, allow direct purchase or booking, and refuse manipulation.

This document records what was chosen, what was rejected, what it costs, and what remains unknown. It is deliberately more opinionated than the source register.

---

## 1. Decision summary

| ID | Decision | Main reason | Cost / risk |
|---|---|---|---|
| D01 | Separate universal skills from a business-specific product passport | Prevents product facts from leaking into reusable instructions; makes facts auditable and revocable | Two artifacts to maintain; the runtime must actually call the passport tool |
| D02 | Nine focused skills plus a core contract, not one giant prompt | Easier routing, review, testing, and replacement | More files; cross-skill conflicts must be resolved explicitly |
| D03 | Fixed precedence: safety/consent/legal > truth/permissions > passport > skill > persuasion | Removes ambiguity in conflicts | Some "good sales" moves are blocked by policy |
| D04 | Tool contracts are specifications, not adapters | Honest about what exists; gives implementers a testable interface | No end-to-end action works until adapters are built |
| D05 | In-chat booking is the default; external links are a fallback | Owner requirement; keeps availability and confirmation verifiable | More integration work; not empirically proven better |
| D06 | Support direct purchase, invoice, and booking without forcing a meeting | Buyer autonomy; some offers do not need a call | Less opportunity for discovery; higher risk of a poorly qualified purchase |
| D07 | Conditional escalation, not escalation on every uncertainty | Preserves human capacity; keeps simple cases resolvable | Requires clear authority limits and reliable tool-failure detection |
| D08 | Russian, Kyrgyz, and mixed language are first-class | Actual market requirement | Kyrgyz copy is unreviewed; mixed-language quality is hard to test |
| D09 | No fake delays, fake identity, fake scarcity, or fabricated proof | Truthfulness and consumer protection | Less "theatrical" persuasion; may feel less human to some buyers |
| D10 | Follow-up requires consent/context and stops after refusal | Autonomy and legal risk | Lower contact volume; some deals will go quiet |
| D11 | Fictional passport examples, `.invalid` domains, synthetic data | Safe to publish; no customer data | Examples cannot prove real integrations or market fit |
| D12 | Structural validation + deterministic response checks, no model claim | Honest testing boundary; catches expensive errors cheaply | Does not measure tone, empathy, or real sales quality |
| D13 | Install only into an isolated or explicitly chosen Hermes home | Avoid damaging a live profile during development | The user must run the install step deliberately |
| D14 | Voice and phone calls are out of scope for v1 | Explicitly deferred by the owner; different latency, consent, and recording risks | The repository cannot be used as a voice agent without new work |
| D15 | "Top 0.1%" is an aspiration, not a claim | No benchmark exists | Marketing language must stay honest |

---

## 2. Detailed decisions

### D01. Universal engine + product passport

**Decision.** All nine skills are product-fact-free. Every company name, price, currency, discount limit, audience definition, proof point, calendar, payment method, and policy lives in a separate product passport. The agent reads the passport through a tool contract.

**Alternatives considered.**

- One monolithic prompt with product facts inline. Fast to start, impossible to audit, stale on every price change.
- A separate skill fork per client. Duplicates logic, drifts, and hides contradictions.
- Pure RAG over documents. Better than an unconstrained prompt, but retrieval does not enforce authority limits, consent, or tool confirmation.

**Why this choice.** The most expensive failures are factual: an invented price, an unauthorized discount, a promised feature, or a booking that does not exist. Separating facts makes those failures testable. It also lets a business update a passport without editing skill logic.

**Tradeoff.** The runtime must implement `passport.lookup` and return fact status. If the runtime injects the whole passport into the prompt instead, the separation is weaker: stale or conflicting fields can still confuse the model. The tool contract is the intended boundary.

**Related:** [`product-passport/README.md`](../product-passport/README.md), [`tools/contracts/passport-lookup.md`](../tools/contracts/passport-lookup.md).

---

### D02. Nine skills, one orchestrator, one core contract

**Decision.** Ship exactly nine skills: orchestrator, qualification, discovery, value/proof, objection/negotiation, closing/execution, language adaptation, follow-up, and integrity/escalation. Put cross-cutting rules in `core/`, not in a tenth skill.

**Why nine.** Each skill maps to a distinct decision the agent makes. The orchestrator handles stage and state; the others handle a specific job. The core contract holds rules that must apply even if no skill is loaded.

**Tradeoff.** More skills mean more routing ambiguity. The descriptions are short (Hermes truncates past 60 characters), so routing relies on names and trigger conditions. A future version could add an explicit router test.

**Rejected.** A 40-skill taxonomy copied from open-source repositories. It looks comprehensive but creates overlapping triggers and no clear owner for cross-cutting rules.

---

### D03. Conflict precedence

**Order.**

1. Safety, consent, and legal obligations.
2. Truthfulness and permission to use a fact.
3. Approved passport and business authority limits.
4. Skill recommendation.
5. Persuasion or conversion goal.

**Why.** Without an order, a model can "helpfully" override a refusal because a skill says to handle objections. The order makes the correct behavior deterministic in principle, even if the model still errs in practice.

**Tradeoff.** A persuasive move that would be effective but unapproved is forbidden. That is intentional. The cost is some lost conversions; the benefit is fewer misrepresentations and complaints.

**Related:** [`core/CONFLICT-RESOLUTION.md`](../core/CONFLICT-RESOLUTION.md).

---

### D04. Contracts, not adapters

**Decision.** Provide seven tool contracts, a shared envelope schema, example envelopes, and failure matrices. Do not pretend any provider is connected. Both passport examples mark every tool binding `not_implemented`.

**Why.** A polished README that implies a working calendar is worse than an honest contract. Implementers need to know request shape, status vocabulary, idempotency, retry rules, and what the agent may say on failure.

**Tradeoff.** The repository cannot book, charge, send, or hand off out of the box. The user must build or bind adapters and run contract tests. The final report must say this plainly.

**Rejected.** Mock adapters that return success and make the demo look complete. They encourage false confidence and hide the hard part.

**Related:** [`tools/README.md`](../tools/README.md).

---

### D05. In-chat booking, external links only as fallback

**Decision.** The default booking path is: check real availability → offer real slots → get explicit agreement → create the booking → confirm only the tool result. Do not send a Calendly (or similar) link by default.

**Why.** The owner explicitly wants in-chat booking. It also keeps the agent in control of consent, timezone, and confirmation. A link can leak the buyer into a different flow where the agent cannot verify what happened.

**Tradeoff.** Calendar integration is mandatory for this path. If availability fails, the agent must say so rather than invent slots. Some buyers prefer self-service links; the agent should provide one only when the buyer asks and the passport permits it.

**Not proven.** In-chat booking is a product decision, not an empirically superior universal practice. It should be A/B tested per market, measuring completion, no-shows, and complaints.

**Related:** [`tools/contracts/calendar-availability.md`](../tools/contracts/calendar-availability.md), [`tools/contracts/calendar-booking.md`](../tools/contracts/calendar-booking.md), scenario C03–C07.

---

### D06. Direct purchase is a first-class path

**Decision.** If the buyer is ready, the agent summarizes verified terms, obtains confirmation, and creates an invoice/payment request. It does not force a meeting, a demo, or "a quick call" first.

**Why.** Some offers are simple enough to buy directly. Forcing a meeting adds friction and can be manipulative when the buyer has already decided. The owner asked for direct purchase/payment support.

**Tradeoff.** Direct purchase may increase refunds or support load if the buyer misunderstood the offer. Mitigations: a concise term summary, explicit confirmation, and a clear cancellation/refund path from the passport. These mitigations still need real-world measurement.

**Exception.** If the passport says a meeting or human approval is required (for example, regulated advice or enterprise contracting), that requirement wins. It must be encoded as a fact, not improvised by the model.

**Related:** scenario P03, Q06, C01, C02.

---

### D07. Conditional escalation

**Decision.** Escalate only when at least one trigger is present:

- the buyer explicitly asks for a human;
- the request is outside the agent's authority or capability;
- legal, regulated, or complex contractual terms are involved;
- a tool fails in a way that blocks a truthful answer or action;
- there is a genuine safety issue (threat, self-harm, minor, fraud, privacy);
- the passport requires approval (for example, a non-standard discount).

Do not escalate merely because the buyer is hesitant, asks a difficult question, or wants time to think.

**Why.** Over-escalation turns the agent into a router and destroys its value. Under-escalation creates unauthorized promises. The trigger list is a compromise, and it is testable.

**Tradeoff.** Edge cases will sit near the boundary. The agent should state what it can do, then escalate if the boundary is real. The handoff contract must record context so the human does not restart the conversation.

**Related:** [`skills/sales/sales-integrity-escalation/references/escalation-playbook.md`](../skills/sales/sales-integrity-escalation/references/escalation-playbook.md), scenarios H01–H06, T05.

---

### D08. Russian, Kyrgyz, and mixed language

**Decision.** Mirror the buyer's language where the agent is fluent. Preserve product facts exactly. Prefer clarity over stylistic flourish. Treat Kyrgyz and mixed-language copy as drafts until a native speaker reviews it.

**Why.** The market requires it. A Russian-only agent will lose trust with Kyrgyz-speaking buyers; a Kyrgyz-only agent will exclude Russian speakers. Code-switching is normal in the target market.

**Tradeoff.** Language quality is the least testable part of the repository. The deterministic checker can verify Cyrillic and some markers, not naturalness, register, or business terminology. Every Kyrgyz/mixed scenario is flagged for human review.

**Rejected.** Claiming "certified translation" or using a machine translation without review. Also rejected: forcing a single language because it is easier to test.

**Related:** [`skills/sales/sales-language-adaptation/references/ru-ky-phrasebook.md`](../skills/sales/sales-language-adaptation/references/ru-ky-phrasebook.md), scenarios P02, M01, M02, M05, M06.

---

### D09. No fake humanness

**Decision.** The agent identifies as an AI assistant when asked or when the context could mislead. It does not use fake typing delays, fake office noise, a fake human name, or a fabricated personal history. It does not invent scarcity, deadlines, testimonials, ROI, or guarantees.

**Why.** Deception is a hard fail in the core contract. It also creates legal and reputational risk. A sales agent that lies once is untrustworthy for the rest of the relationship.

**Tradeoff.** Some buyers respond better to a "human" persona. That is not a sufficient reason to deceive. The agent can be warm, direct, and personable without pretending to be a person.

**Nuance.** A business may give the assistant a disclosed brand persona (for example, "Nimbus Assistant"). That is acceptable if the AI nature is not hidden and the passport says so. The examples do not require a human name.

**Related:** scenarios H02, H03; all skills' counterexamples.

---

### D10. Follow-up with consent and a clean stop

**Decision.** Follow up only with context, a useful reason, and a cadence limit. Stop after an explicit refusal or opt-out. A factual question after an opt-out may be answered, but the sales motion stays stopped.

**Why.** "Persistence" is often just pressure. Consent and usefulness are better constraints than a quota of touches. The owner explicitly asked for no pressure after refusal.

**Tradeoff.** Fewer touches may mean fewer reactivated deals. A business can tune cadence in the passport, but it cannot remove the opt-out or the stop rule.

**Related:** [`skills/sales/sales-follow-up/SKILL.md`](../skills/sales/sales-follow-up/SKILL.md), scenarios F01–F06.

---

### D11. Fictional, safe examples

**Decision.** Use two clearly fictional passports with `.invalid` domains, synthetic names, and `metadata.fictional: true`. Do not include real customer data, real prices, real calendars, or real proof.

**Why.** The repository must be publishable and safe to test. Fictional examples also make it obvious when a model confuses example facts with real ones.

**Tradeoff.** Examples cannot validate market fit or provider behavior. They are format demonstrations, not a sales playbook for a real company.

---

### D12. Test what can be tested honestly

**Decision.** Implement four layers:

1. static structure and schema validation;
2. isolated Hermes discovery;
3. a 57-scenario corpus with deterministic checks, including B2C, scoped-refusal, and adoption coverage;
4. a response checker that reads recorded responses.

Do not claim a live model was evaluated. Flag rubric review as not run. Do not implement fake tool adapters.

**Why.** A test suite that pretends to test behavior is worse than a smaller honest one. The deterministic layer catches invented prices, false confirmations, forbidden tools, question-count violations, and missing handoffs. It cannot catch a plausible lie that avoids the exact forbidden strings.

**Tradeoff.** The repository can pass structural validation while the agent still behaves badly. The final report must keep that distinction visible.

**Related:** [`tests/README.md`](../tests/README.md), [`tests/RUBRIC.md`](../tests/RUBRIC.md), [`tests/COVERAGE.md`](../tests/COVERAGE.md).

---

### D13. Isolated installation

**Decision.** The installer is dry-run by default and writes only with `--apply`. It backs up replaced skill directories. It copies the shared `core/`, `tools/`, `product-passport/`, and `research/` documents into each skill under `references/shared/` and rewrites each skill's links, because Hermes serves only files inside a skill directory. It writes an install manifest and activation notes. The loading test uses a temporary `HERMES_HOME` and never reads or writes the live profile.

**Why.** The owner explicitly said not to install into the active agent during this work. Even outside this task, silently modifying a live profile is unacceptable. The audit found that installing a skill alone dropped its core contract and tool contracts, so the bundle is required for the skill to function as designed.

**Tradeoff.** Each installed skill carries a copy of the shared documents, so editing one copy would drift; the source repository remains the source of truth and reinstalling refreshes the copies. The installer cannot verify the target profile's model or tool configuration.

**Related:** [`scripts/install_skills.py`](../scripts/install_skills.py), [`scripts/test_installed_artifact.py`](../scripts/test_installed_artifact.py), [`scripts/test_hermes_loading.py`](../scripts/test_hermes_loading.py).

---

### D14. Voice deferred

**Decision.** No phone calls, voice cloning, real-time call coaching, or recording workflow in v1.

**Why.** The owner said to forget voice for now. Voice adds latency, consent, recording, transcription, and jurisdiction-specific legal risk. A text skill set does not transfer cleanly.

**Tradeoff.** The repository cannot serve inbound phone leads. That is a future product, not a hidden feature.

---

### D15. Honest ambition

**Decision.** Describe the goal as "top-tier" or "aspirational," never as a measured "top 0.1%."

**Why.** There is no benchmark, no comparison group, and no outcome data. The phrase can motivate the design, but it cannot appear as a factual claim in the README or sales materials.

---

### D16. Quote as the unit of payment truth

**Decision.** A payment request must reference an approved, unexpired quote version with an exact terms snapshot. A change to quantity, plan, discount, tax treatment, or terms creates a new version. A discounted or custom quote needs an approval reference from the passport's authority owner.

**Why.** The audit found that a documented discount path could produce a payment request with no record of what was approved. A versioned quote makes the amount auditable and gives the payment tool something concrete to verify.

**Tradeoff.** One more artifact to maintain, and a re-quote whenever scope changes. The alternative — trusting the conversation and the client-supplied amount — is what produces billing disputes.

### D17. Scoped refusal is not a stop

**Decision.** A refusal of one element (a meeting, a channel, a plan) stops only that element. A refusal of the offer or of contact stops the sequence. A buyer correction is accepted immediately, not treated as a contradiction to adjudicate.

**Why.** The audit found the earlier wording could either pressure a buyer past a boundary or end a conversation with a ready buyer who only declined a call.

**Tradeoff.** The agent must classify the refusal correctly. A wrong classification in either direction is a real failure, which is why the behavior is covered by scenarios B02 and F03.

### D18. Consumer offers are first-class

**Decision.** Whether a consumer is a fit comes from `offer.buyer_types` and `sales_guidance.segments`, never from a universal "business buyers only" rule. The repository ships a B2C example and four consumer scenarios.

**Why.** The audit found B2B-only assumptions encoded as universal logic and no B2C coverage. The architecture must serve both motions.

**Tradeoff.** More passport surface area and a consumer example that needs its own jurisdiction review (recorded in the passport's `unresolved`).

### D19. Klaff is recorded, not adopted

**Decision.** Oren Klaff's framing vocabulary is recorded in the source register as a known coverage gap, but the repository adopts only the integrity-compatible idea of reducing perceived risk through verified clarity. Frame-control and status tactics are not encoded.

**Why.** The audit noted Klaff's absence and also warned against adopting famous methodology content without evidence that it improves behavior. Recording the source and declining to adopt it is the honest response.

**Tradeoff.** The repository may miss a framing pattern that a controlled test would show helps. That is an accepted gap, not a hidden capability.

---

## 3. Corrections to the original brief

The source brief contained several patterns that are common in sales content but unsafe or unsupported. The repository changes them deliberately:

| Original pattern | Repository decision | Reason |
|---|---|---|
| Send a Calendly link to book | Check real availability and book in chat; use the approved external link only when the passport allows it and the buyer agrees | Owner requirement; verifiable confirmation; the audit found the old wording contradicted passports that allowed a link |
| Every message must end with a question | No such rule; question limits are scenario-specific | Pressure, interrogation, and unnatural conversation |
| Use "alpha" / dominance language | Rejected | Unvalidated construct; conflicts with consent |
| Type slowly to seem human | Rejected | Deception; no evidence of durable trust |
| Create urgency with limited slots | Only verified, current scarcity from the passport | Fabricated scarcity is deceptive |
| Quote impressive ROI or case studies | Only approved proof with source and permission | Misrepresentation risk |
| Escalate every uncertainty to a human | Escalate only on defined triggers | Preserves usefulness and human capacity |
| Force a meeting before purchase | Support direct purchase/invoice | Buyer autonomy; owner requirement |
| Promise "top 0.1%" performance | Aspiration only | No benchmark |
| Use Belfort's straight-line close | Excluded | Fraud conviction/restitution; high-pressure tactics |
| Use a 5–7 word personality read | Rejected | Unsupported psychotyping |
| Treat RAG as truth | Tool/passport verification plus explicit unknowns | Retrieval reduces but does not eliminate hallucination |
| "Never discount; discount destroys value" | The passport's discount and negotiation limits win, with a trade or correction; never above authority | The audit found this generic rule could override approved business policy |
| Reject a consumer because the skill assumes B2B | Read `offer.buyer_types`; qualify against the declared segment | The audit found a B2B-only disqualifier encoded as universal logic |
| Answer a "no call" as if the whole offer was refused | Stop only the refused element; continue on the legitimate path | Scoped refusal protects both the buyer's boundary and their goal |

---

## 4. Unresolved business decisions

These are intentionally **not** invented by the repository. The owner must fill them in an approved passport before production.

| Area | Unresolved question | Why it matters | Where it belongs |
|---|---|---|---|
| Pricing | Exact plans, currencies, taxes, rounding, and whether prices are per user/team/month/year | A wrong number is a hard fail | `pricing` |
| Discounts | Who may discount, by how much, and what approval is required | Unauthorized discount is a hard fail | `sales_policy.discounts` |
| Payment | Provider, methods, invoice vs. instant charge, deposit, refunds, chargebacks | The agent cannot claim payment without a tool result | `pricing`, `fulfillment`, `tools` |
| Booking | Calendar provider, slot duration, buffers, timezone, reschedule/cancel policy, no-show fee | In-chat booking depends on real availability | `fulfillment`, `sales_policy` |
| Qualification | ICP, disqualifiers, minimum team size, regulated exclusions, minors policy | Poor-fit sales create refunds and harm | `qualification` |
| Proof | Which case studies, logos, metrics, and quotes are approved; NDA constraints | Fabricated or unapproved proof is a hard fail | `proof` |
| Handoff | Real queue, hours, SLA, fallback contact, what the human receives | A false "human will contact you" is a failure | `handoff` |
| Follow-up | Cadence, quiet hours, channel, opt-out keywords, retention | Pressure and privacy risk | `follow_up`, `privacy` |
| Languages | Which languages are enabled; who reviews Kyrgyz; whether mixed language is allowed | Quality and trust | `business.languages` |
| Legal | Jurisdiction, consent/recording rules, consumer rights, regulated claims | The repo is not legal advice | `privacy`, `sales_policy` |
| Data | What is stored, where, for how long, and how deletion works | Privacy and compliance | `privacy`, `tools.crm` |
| Brand persona | Is the assistant named? Is AI identity disclosed proactively or on request? | Deception risk | `business`, `sales_policy` |

**Do not wait for every answer to start.** Fill the known fields, mark the rest `unknown`, and let the agent say what it cannot do. An honest unknown is better than an invented answer.

---

## 5. Accepted risks

1. **The model may ignore instructions.** A skill is not an enforcement layer. Tool-side validation, allow-lists, and post-generation checks are still needed.
2. **The deterministic tests are shallow.** They catch specific strings and tool calls, not persuasive tone or subtle omissions.
3. **The passport can be wrong.** A verified label is only as good as the approval process. Re-verification and expiry are required.
4. **The Kyrgyz copy may be awkward.** Native review is a release gate, not a nice-to-have.
5. **In-chat booking may underperform.** It is a product bet that needs measurement.
6. **Direct purchase may increase refunds.** Mitigations are designed but untested.
7. **Tool failures may be misclassified.** The agent needs a clear status vocabulary and a conservative "not confirmed" default.
8. **A human handoff can fail.** The agent must not claim a human is present without a confirmed handoff.
9. **The market may expect a different sales motion.** The passport and scenarios must be localized, not just translated.
10. **The repository name is aspirational.** It does not imply a ranking or certification.

---

## 6. How these decisions should be revisited

- **After 20–50 real conversations:** review transcripts for invented facts, pressure, language quality, and unnecessary escalation.
- **After adapter implementation:** run contract tests for timeout, conflict, duplicate writes, and out-of-order events.
- **After native review:** update the phrasebook and Kyrgyz scenarios; remove the draft warning only when review is documented.
- **After an A/B test:** compare direct purchase vs. meeting-first, and in-chat booking vs. link, on completion, refunds, no-shows, complaints, and comprehension.
- **After a model evaluation:** publish the model, version, prompt, trial count, rubric reliability, and failures. Do not report a single cherry-picked transcript.
- **Before any regulated market:** obtain legal review of consent, privacy, recording, refunds, and claims.

The decisions are not permanent. They are the current best attempt to balance usefulness, truthfulness, and the owner's requirements. The evidence for whether they work is still missing.
