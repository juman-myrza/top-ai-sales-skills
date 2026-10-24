# Claim–Evidence Matrix

**Purpose:** show which claims in the skills are supported, which are heuristic, and which are explicit product decisions.  
**Snapshot:** 2026-10-23.  
**Status:** research synthesis, not a validated sales experiment.

The repository separates three things that sales content often blends:

1. **Evidence** — what a source found, with its limits.
2. **Heuristic** — a useful pattern that is not proven to generalize.
3. **Decision** — a rule this repository chooses for safety, product, or operational reasons.

A decision is allowed to be opinionated. It is not allowed to masquerade as science.

---

## 1. How to read confidence

| Confidence | Meaning |
|---|---|
| **High** | Strong direct evidence for the narrow claim, or a verified technical behavior |
| **Moderate** | Multiple credible sources or a large vendor study, but no independent replication for this use |
| **Low** | Practitioner experience, small or proprietary evidence, or a plausible mechanism without direct sales evidence |
| **Policy** | Not an empirical claim; chosen for ethics, consent, legal risk, or product requirements |

A high-confidence claim can still be irrelevant to a specific market. A low-confidence heuristic can still be useful. Confidence is not the same as importance.

---

## 2. Claims used in the skills

| ID | Claim | Sources | Evidence type | Confidence | Repository decision | Scenarios / skills | What would weaken or falsify it |
|---|---|---|---|---|---|---|---|
| C01 | Asking diagnostic questions before presenting a solution produces better information and more relevant recommendations than pitching immediately | S01, S02, S07, S10 | Vendor field research + practitioner frameworks | Low–moderate | Use a small number of high-value questions; stop when the buyer is ready; never interrogate | Q03, Q04, Q06, M03; `sales-discovery`, `sales-qualification` | A controlled comparison showing that immediate pitching yields equal or better buyer outcomes in this market |
| C02 | Complex B2B purchases involve multiple stakeholders, and disagreement inside the buying group is common | S04, S05 | Vendor survey; one page inaccessible | Moderate | Ask who else is involved and what each person needs; do not assume a fixed number of stakeholders or a linear process | O07, Q04; `sales-qualification`, `sales-objection-negotiation` | Representative independent data showing single-stakeholder decisions dominate the target segment |
| C03 | Tailoring to the buying group's shared goals is more effective than tailoring only to one individual's preferences | S04 | Single vendor survey with reported effect sizes | Low–moderate | Frame proof at the level the buyer can defend to colleagues; do not manufacture group consensus | O07, P06; `sales-value-proof` | Evidence that individual-level framing performs better in this context, or a well-powered replication that finds no group-level effect |
| C04 | Social proof, authority, consistency, liking, reciprocity, scarcity, and unity can influence decisions | S08 | Peer-reviewed social psychology with replication caveats; commercial summary | Moderate for narrow lab effects; low for sales scripts | Use only verified, permitted proof; never fabricate scarcity, testimonials, or credentials | H02, O01, O08; `sales-value-proof`, `sales-objection-negotiation`, `sales-integrity-escalation` | A well-powered replication showing the effect is absent in this setting — or evidence that a tactic causes harm |
| C05 | First offers and reference points can anchor a negotiation | S13 | Peer-reviewed experiments | Moderate | Do not invent a price, discount, or anchor; state verified terms and authority limits; do not negotiate against yourself | P05, O08; `sales-objection-negotiation` | Evidence that anchoring is negligible in this buying context, or that a different tactic better protects the buyer |
| C06 | Knowing a walk-away alternative (BATNA) and giving the buyer permission to say no improves decision clarity | S12, S09 | Practitioner negotiation frameworks | Low | Establish authority limits before negotiating; accept a clean no; do not bluff a BATNA | O02, O05, F03; `sales-objection-negotiation`, `sales-follow-up` | Evidence that explicit no-permission reduces good-faith decisions or increases harm |
| C07 | Labels, mirrors, and calibrated questions can improve information exchange and de-escalation | S06 | Practitioner experience; hostage-negotiation context | Low | Offer them as optional tools in difficult conversations; never use them to trap or coerce | O02, O04, H04; `sales-objection-negotiation`, `sales-integrity-escalation` | Controlled sales evidence showing no benefit or increased manipulation risk |
| C08 | Commitment should be requested when the buyer shows readiness, not deferred automatically to a meeting | S01, S07 | Vendor/practitioner frameworks | Low–moderate | Support direct purchase, invoice, and booking; ask for one clear next step when intent is explicit | P03, Q06, C01, C02; `sales-closing-execution` | Evidence that direct purchase increases regret, fraud, or support burden without a meeting in this market |
| C09 | Retrieval and grounding reduce unsupported generation but do not guarantee truth | S17, S18, S19, S20 | Peer-reviewed ML research + evaluation preprint | High for the limitation | Treat every material fact as a lookup; require a confirming tool result before claiming an action; say "unknown" when data is missing | T01, T02, T03, T04; `sales-integrity-escalation`, `sales-closing-execution` | A verified system that provably eliminates unsupported claims across the target distribution — still not assumed here |
| C10 | Agent Skills use progressive disclosure: name/description first, full instructions on activation, references on demand | S15, S16 | Official specification + local implementation | High for mechanics | Keep descriptions short, bodies scannable, and depth in `references/`; validate with Hermes in an isolated home | Validator + Hermes loading test | A Hermes version that changes discovery or budget behavior; re-test |
| C11 | In-chat booking is preferable to sending an external scheduling link by default | None — product requirement | Product decision | Policy | Check real availability, offer real slots, book in chat, confirm only the tool result; send a link only if the buyer asks or the channel requires it | C03–C07; `sales-closing-execution` | An A/B test showing external links produce better completion without more harm, or a channel constraint that makes in-chat booking impossible |
| C12 | A buyer who wants to purchase directly should not be forced into a discovery meeting | None — product requirement | Product decision | Policy | Offer the direct path; ask only for facts needed to execute; do not gate price or purchase behind a call | P01, P03, Q06, C01; `sales-conversation-orchestrator`, `sales-closing-execution` | Evidence that a meeting is legally or operationally required for a specific offer — then encode that in the passport |
| C13 | Escalation should be limited to explicit triggers, not every ambiguity | None — policy/operations decision | Policy | Policy | Escalate on explicit human request, outside authority, legal/complex terms, tool failure, safety, or required approval; otherwise resolve within scope | H01, P04, P05, T05; `sales-integrity-escalation` | Evidence that broader escalation improves outcomes without unacceptable delay or cost |
| C14 | Fabricated proof, fake identity, fake delays, and invented scarcity are unacceptable | S21 + integrity reasoning | Regulator guidance + ethical policy | High as a policy; jurisdiction-specific legally | Hard-fail these behaviors; require verified proof and honest AI identity | H02, H03; all skills | Nothing in this repository's scope; a business requirement to deceive is out of scope |
| C15 | Mirroring the buyer's Russian, Kyrgyz, or mixed language improves comprehension and trust | None — linguistic accommodation heuristic | Practitioner judgment | Low | Match the buyer's language where fluent; preserve exact product facts; switch only when it improves clarity; flag Kyrgyz for native review | P02, M01, M02, M05, M06; `sales-language-adaptation` | Native-speaker testing showing mirroring causes confusion, or a market requirement for a fixed language |
| C16 | A consumer offer is a legitimate direct-purchase motion when the passport declares `b2c`; a universal skill must not disqualify consumers | None — product/schema decision | Policy | Policy | Read `offer.buyer_types` and `sales_guidance.segments`; qualify a consumer against the consumer segment instead of assuming B2B | B01–B04; `sales-qualification` | A business rule or law that requires a business buyer for a specific offer — then encode it in the passport |
| C17 | Adoption and implementation barriers are distinct from value objections and require a different move | None — practitioner judgment | Heuristic | Low | Diagnose who must change, what failed before, and the smallest adoption path; do not answer with another value pitch | O09, B03; `sales-objection-negotiation`, `sales-discovery` | Evidence that a value pitch resolves adoption concerns equally well, or that adoption diagnosis increases pressure |
| C18 | An explicit language preference should override mirroring the last message | None — linguistic accommodation heuristic | Policy | Low | Honor an explicit "write in Kyrgyz/English" instruction; treat a one-word reply as a weak signal, not a switch | P02, M05, M06; `sales-language-adaptation` | Native-speaker testing showing that overriding a one-word switch causes confusion |
| C19 | A refusal of one element (a meeting, a channel) should not end the whole sequence, but a refusal of the offer should | None — policy/consent decision | Policy | Policy | Stop only the refused element and continue the shortest legitimate path; stop the sequence on an offer or contact refusal | B02, F03; `sales-conversation-orchestrator`, `sales-follow-up` | Evidence that scoped-refusal handling pressures buyers past a boundary |
| C20 | Payment execution must reference an approved quote version, and a discounted or changed amount requires a new version and approval | None — financial-control decision | Policy | Policy | Require `quote_id`/`quote_version`, exact terms, and an approval reference for discounted or custom terms; reject mismatches | C01, C02, O10; `sales-closing-execution`, `payments.invoicing` | A supported business process where an agent may charge a negotiated amount without a recorded quote — out of scope for this repository |

---

## 3. Claims the repository explicitly does **not** make

| Claim | Status | Why |
|---|---|---|
| "This agent is top 0.1%." | **Aspirational only** | No benchmark, comparison group, or outcome data. The phrase describes an ambition, not a measured result. |
| "These skills increase conversion by X%." | **Not claimed** | No experiment was run. Vendor statistics about other products do not transfer. |
| "The 57 scenarios prove the agent is safe." | **Not claimed** | They are written tests. Only hand-written checker fixtures and regression cases have been run through the deterministic evaluator, and no model has been evaluated. |
| "RAG makes the agent hallucination-free." | **Rejected** | S17–S19 show grounding helps but does not guarantee faithfulness. The repository uses tool/passport verification and explicit unknowns. |
| "Always end with a question." | **Rejected** | Unsupported as a universal rule; it can pressure the buyer and produce interrogation. Question limits are scenario-specific. |
| "Use scarcity and urgency to close." | **Rejected unless verified** | Cialdini's scarcity effect is real in some settings, but fabricated scarcity is deception. Only documented, current constraints may be mentioned. |
| "Read 5–7 words to classify the buyer's personality." | **Rejected** | No validated basis for this kind of psychotyping; risks discrimination and manipulation. |
| "Alpha buyers need dominance." | **Rejected** | The construct is not validated for sales, and dominance tactics conflict with consent. |
| "Fake typing delays make the agent feel human." | **Rejected** | Deception. Response timing should reflect real processing and channel constraints, not a theatrical delay. |
| "Jordan Belfort's straight-line system is the gold standard." | **Excluded as a method** | Public fraud conviction and restitution order; high-pressure tactics conflict with the integrity contract. See S14. The exclusion is an integrity policy, not a scientific finding that every tactic he names is ineffective. |
| "Belfort's qualifying or product/company/seller-trust distinctions are validated." | **Not claimed** | These mechanisms are treated as low-evidence practitioner candidates at most, not as established findings, and they are not encoded. Numerical certainty estimates, recursive closing after refusal, and voice tactics are explicitly out of scope. See S14. |
| "A Calendly link is the best booking path." | **Not assumed** | In-chat booking is the product decision; external links are a fallback, not the default. |
| "Kyrgyz copy is production-ready." | **Not claimed** | No native-speaker review has been completed. |

---

## 4. Evidence quality by source type

| Source type | Examples | Strength | Characteristic weakness | How this repo uses it |
|---|---|---|---|---|
| Peer-reviewed ML / psychology | S13, S17, S18, S19 | Methods and limitations are inspectable | Lab context; effect sizes may not transfer to sales chats | Narrow claims and explicit caveats |
| Official technical standard / docs | S15, S16, S21 | Directly verifiable | Version- or jurisdiction-specific | Mechanics and compliance direction |
| Vendor research | S01/S02, S03, S04, S07 | Large samples, real sales context | Commercial interest; proprietary method; limited raw data | Vocabulary and hypotheses, not proof |
| Practitioner books | S06, S08, S09, S10, S12 | Rich, actionable patterns | Anecdote, selection bias, no control group | Structured options with guardrails |
| Open-source repositories | S23–S25 | Concrete prior art | README claims are not validation; licenses and maintenance vary | Inspiration and gap analysis; no code copied |
| Product requirements | Owner brief | Defines the job to be done | Not evidence of effectiveness | Encoded as decisions, tested as behavior |

---

## 5. Mapping from source to repository artifact

| Artifact | Main sources | What is actually borrowed |
|---|---|---|
| `core/CORE-BEHAVIOR-CONTRACT.md` | S15, S16, S17–S19, S21 + policy decisions | Truth/consent/tool-verification precedence; no unsupported claims |
| `sales-conversation-orchestrator` | S01, S06, S07, S16 | Stage logic, turn shape, state, stop conditions |
| `sales-qualification` | S04, S07, S11, S12 | Fit, authority, decision process, respectful disqualification |
| `sales-discovery` | S01, S02, S06, S07, S10 | Question sequencing, diagnosis before pitch, contradiction handling, verified-insight reframing |
| `sales-value-proof` | S04, S08, S17–S19, S27 | Verified proof, group relevance, relevance-based evidence selection, no fabricated ROI, no gap-filling from memory |
| `sales-objection-negotiation` | S06, S08, S09, S12, S13 | Clarify, anchor honestly, know authority limits, accept no, adoption/implementation diagnosis, entitlement versus concession |
| `sales-closing-execution` | S01, S07, S16 + product requirements | Commitment, in-chat booking, direct purchase, tool confirmation |
| `sales-language-adaptation` | S15 + linguistic judgment | Russian/Kyrgyz/mixed mirroring, clarity, native-review caveat |
| `sales-follow-up` | S04, S05 + consent policy | Useful follow-up, cadence limits, opt-out, clean close-out |
| `sales-integrity-escalation` | S14, S18, S21 + policy | Refusal of fabrication/fraud, privacy, safety, handoff |
| `product-passport/` | Owner brief + schema design | Fact status, authority limits, tool bindings, approval gate |
| `tools/` | S16 + API design | Envelope, idempotency, status vocabulary, failure behavior |
| `tests/` | S01–S27 + failure analysis | 57 scenarios targeting expensive failure modes, plus checker and installed-artifact regression tests |

---

## 6. What would justify stronger claims later

1. **Behavioral evaluation:** run the 57 scenarios against named models, multiple trials, with blinded rubric review and inter-rater reliability.
2. **Tool contract tests:** implement adapters and test timeouts, conflicts, duplicates, and out-of-order webhooks.
3. **Native-language review:** have Russian and Kyrgyz sales professionals review every non-English line.
4. **Field experiment:** compare the agent with a control on qualified-lead conversion, refunds, complaints, opt-outs, and buyer comprehension — not conversion alone.
5. **Harm monitoring:** track fabricated claims, unauthorized discounts, privacy incidents, and pressure complaints.
6. **Long-horizon tests:** conversations of 20+ turns with changing facts, fatigue, and multiple stakeholders.
7. **Legal review:** jurisdiction-specific consent, recording, privacy, refund, and consumer-protection requirements.

Until then, the honest claim is: **the repository implements a carefully constrained design and a structural test suite; it has not demonstrated sales superiority or production safety.**
