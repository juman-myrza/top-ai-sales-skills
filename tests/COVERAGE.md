# Scenario Coverage Map

**Corpus:** 57 scenarios in 9 categories.  
**Status:** structural coverage only. No live model has been evaluated against this corpus.

---

## 1. Category summary

| Category | Count | Primary skills | Main failure modes |
|---|---:|---|---|
| Price and buying intent | 6 | orchestrator, value-proof, closing | invented price, forced meeting, unauthorized discount |
| Qualification and discovery | 6 | qualification, discovery | false fit, interrogation, premature pitch |
| Objections and negotiation | 10 | objection-negotiation, value-proof | discount reflex, competitor fiction, pressure |
| Closing and booking | 7 | closing-execution | false payment/booking confirmation, external link, silent slot substitution |
| Tool failures | 6 | closing-execution, integrity | guessing after timeout, false success, duplicate writes |
| Handoff and safety | 6 | integrity-escalation | fabrication, privacy leak, unsafe sale, late handoff |
| Multilingual and multi-turn | 6 | language-adaptation, orchestrator | language abandonment, stale state, contradiction |
| Follow-up and refusal | 6 | follow-up, integrity | pressure after no, content-free bump, sequence restart |
| Consumer direct purchase | 4 | qualification, closing, objection-negotiation | B2B-only assumption, forced meeting, adoption blind spot |
| **Total** | **57** | | |

---

## 2. Scenario index

### Price and buying intent (6)

| ID | Scenario | Passport | Human review |
|---|---|---|---|
| P01 | Direct price question in Russian | `direct-sale-nimbus-notes` | no |
| P02 | Direct price question in Kyrgyz | `direct-sale-nimbus-notes` | yes |
| P03 | Buying signal: how to pay for the annual plan | `direct-sale-nimbus-notes` | no |
| P04 | Enterprise request outside the approved offer | `direct-sale-nimbus-notes` | yes |
| P05 | 20% discount demand with a walk-away threat | `direct-sale-nimbus-notes` | yes |
| P06 | Competitor price claim | `direct-sale-nimbus-notes` | yes |

### Qualification and discovery (6)

| ID | Scenario | Passport | Human review |
|---|---|---|---|
| Q01 | HIPAA BAA is a disqualifier | `direct-sale-nimbus-notes` | no |
| Q02 | On-premise-only buyer is not a fit | `direct-sale-nimbus-notes` | no |
| Q03 | Vague goal needs one diagnostic question | `direct-sale-nimbus-notes` | no |
| Q04 | Qualified team with a concrete bottleneck | `direct-sale-nimbus-notes` | no |
| Q05 | Buyer refuses budget and team-size questions | `direct-sale-nimbus-notes` | no |
| Q06 | Ready buyer: stop discovery and execute | `direct-sale-nimbus-notes` | no |

### Objections and negotiation (10)

| ID | Scenario | Passport | Human review |
|---|---|---|---|
| O01 | Price objection without an automatic discount | `direct-sale-nimbus-notes` | yes |
| O02 | Need to think: no pressure | `direct-sale-nimbus-notes` | no |
| O03 | Competitor comparison without disparagement | `direct-sale-nimbus-notes` | yes |
| O04 | Trust objection: AI makes mistakes | `direct-sale-nimbus-notes` | no |
| O05 | No budget this quarter | `direct-sale-nimbus-notes` | no |
| O06 | Proposal request with unclear scope | `direct-sale-nimbus-notes` | no |
| O07 | Champion needs director approval | `direct-sale-nimbus-notes` | no |
| O08 | 40% ultimatum | `direct-sale-nimbus-notes` | yes |
| O09 | Adoption risk after a failed rollout | `direct-sale-nimbus-notes` | no |
| O10 | Correction owed to the buyer is not a bargaining chip | `direct-sale-nimbus-notes` | yes |

### Closing and booking (7)

| ID | Scenario | Passport | Human review |
|---|---|---|---|
| C01 | Direct purchase: summarize terms before charging | `direct-sale-nimbus-notes` | no |
| C02 | Invoice creation with a confirming tool result | `direct-sale-nimbus-notes` | no |
| C03 | Appointment booking: check real availability first | `appointment-karkyra-consult` | no |
| C04 | Booking confirmation only after the tool confirms | `appointment-karkyra-consult` | no |
| C05 | Slot taken between offer and booking | `appointment-karkyra-consult` | yes |
| C06 | Calendar unavailable: no invented slots | `appointment-karkyra-consult` | no |
| C07 | Buyer asks for an external scheduling link | `appointment-karkyra-consult` | no |

### Tool failures (6)

| ID | Scenario | Passport | Human review |
|---|---|---|---|
| T01 | Passport lookup timeout: no price guess | `direct-sale-nimbus-notes` | no |
| T02 | Conflicting passport versions: do not pick a number | `direct-sale-nimbus-notes` | yes |
| T03 | Buyer claims payment; tool says pending | `direct-sale-nimbus-notes` | no |
| T04 | Booking timeout: no false confirmation | `appointment-karkyra-consult` | no |
| T05 | Handoff tool failure: no false human presence | `direct-sale-nimbus-notes` | no |
| T06 | CRM write failure: no false persistence | `direct-sale-nimbus-notes` | no |

### Handoff and safety (6)

| ID | Scenario | Passport | Human review |
|---|---|---|---|
| H01 | Explicit human request | `direct-sale-nimbus-notes` | no |
| H02 | Request to fabricate a case study | `direct-sale-nimbus-notes` | no |
| H03 | Request for a fake invoice and cash kickback | `direct-sale-nimbus-notes` | no |
| H04 | Threat after a follow-up | `direct-sale-nimbus-notes` | no |
| H05 | Minor buyer with a parent's card | `direct-sale-nimbus-notes` | no |
| H06 | Request for another customer's contact details | `direct-sale-nimbus-notes` | no |

### Multilingual and multi-turn (6)

| ID | Scenario | Passport | Human review |
|---|---|---|---|
| M01 | Russian to Kyrgyz switch | `direct-sale-nimbus-notes` | yes |
| M02 | Natural Russian-Kyrgyz mix | `direct-sale-nimbus-notes` | yes |
| M03 | Buyer contradicts team size | `direct-sale-nimbus-notes` | yes |
| M04 | Buyer changes the timeline | `direct-sale-nimbus-notes` | yes |
| M05 | Unsupported language: Uzbek | `direct-sale-nimbus-notes` | no |
| M06 | Buyer tests Kyrgyz capability | `direct-sale-nimbus-notes` | yes |

### Follow-up and refusal (6)

| ID | Scenario | Passport | Human review |
|---|---|---|---|
| F01 | Buyer requests a specific follow-up day | `direct-sale-nimbus-notes` | no |
| F02 | Proposal follow-up must add value | `direct-sale-nimbus-notes` | yes |
| F03 | Explicit refusal: stop immediately | `direct-sale-nimbus-notes` | no |
| F04 | Opt-out followed by a factual question | `direct-sale-nimbus-notes` | yes |
| F05 | No-show recovery without blame | `appointment-karkyra-consult` | yes |
| F06 | Cadence exhausted: clean close-out | `direct-sale-nimbus-notes` | no |

### Consumer direct purchase (4)

| ID | Scenario | Passport | Human review |
|---|---|---|---|
| B01 | Consumer price question without a meeting | `consumer-course-example` | no |
| B02 | Scoped refusal — no call, still wants to pay | `consumer-course-example` | no |
| B03 | Consumer adoption concern from a past failed course | `consumer-course-example` | no |
| B04 | Consumer ready to buy directly | `consumer-course-example` | no |

---

## 3. Skill coverage

| Skill | Representative scenarios | What is exercised |
|---|---|---|
| `sales-conversation-orchestrator` | P03, Q06, C01, T05, M03 | stage shifts, turn shape, state, conflict precedence |
| `sales-qualification` | P04, Q01, Q02, Q05, B01–B04 | fit, disqualification, consumer fit, respectful refusal to share data |
| `sales-discovery` | Q03, Q04, Q06, M03, M04 | one-question discovery, contradiction, timeline change |
| `sales-value-proof` | P01, P06, O01, O03, O04, H02 | verified proof, no fabricated cases, no competitor fiction |
| `sales-objection-negotiation` | O01–O10, P05, B03 | price, timing, authority, competitor, ultimatum, adoption |
| `sales-closing-execution` | P03, C01–C07, T03, T04 | direct purchase, invoice, booking, conflict, timeout |
| `sales-language-adaptation` | P02, M01, M02, M05, M06 | Russian, Kyrgyz, mixed, unsupported language, honesty |
| `sales-follow-up` | F01–F06, T06 | consent, value, cadence, opt-out, no-show, close-out |
| `sales-integrity-escalation` | H01–H06, T02, T05, P04, P05 | fabrication, fraud, privacy, minors, threats, handoff failure |

Every skill has at least two scenarios. The corpus does not prove that any skill works in production.

---

## 4. Requirement coverage

| Requirement | Scenarios | Notes |
|---|---|---|
| Price requests | P01, P02, P06, Q05 | Verified starting price, currency, driver; no invented quote |
| Buying intent | P03, Q06, C01, C02 | Stop discovery; summarize; execute only with confirmation |
| Poor fit | Q01, Q02 | HIPAA BAA and on-premise disqualifiers |
| Discovery | Q03, Q04, Q05, M03, M04 | One question, reflect, update state |
| Objections | O01–O10 | Price, timing, trust, budget, competitor, authority, adoption, entitlement |
| Missing facts | P04, T01, T02 | Unknown/conflicting passport data |
| Competitors | P06, O03 | No unverified comparison or disparagement |
| Direct close vs booking | P03, C01, C02, B01, B04 vs C03–C07 | Direct purchase is not forced into a meeting; appointment offer is not priced |
| Consumer motion | B01–B04 | A B2C offer is qualified and bought directly; no B2B assumption |
| Scoped refusal | B02, F03 | "No call" is not "no offer"; a full refusal still stops the sequence |
| Adoption barrier | O09, B03 | Diagnose the prior failure and adoption plan instead of repeating a value pitch |
| Tool failures | T01–T06, C05, C06 | Timeout, conflict, false success, CRM, handoff |
| Human handoff | H01, P04, P05, T05 | Explicit request, authority, failure fallback |
| Follow-up and refusal | F01–F06 | Consent, value, opt-out, no-show, close-out |
| Russian | Most scenarios | Default operational language |
| Kyrgyz | P02, M01, M06 | Draft copy; native review required |
| Mixed language | M02, M04 | Natural code-switching |
| Multi-turn contradictions | M03, M04, F04 | Team size, timeline, opt-out scope |
| Truth vs persuasion | P05, O08, O10, H02, H03 | Authority, integrity, and owed corrections beat pressure |
| Privacy | Q05, H06 | Data minimization and customer privacy |
| Safety | H04, H05 | Threat and minor |

---

## 5. Deterministic vs human review

- **Deterministic:** 57 scenarios. All have required/forbidden phrase checks, question limits, and tool-call expectations.
- **Human review flagged:** 17 scenarios, mainly Kyrgyz language quality, negotiation nuance, contradictions, and integrity tone.
- **Not covered by deterministic checks:** whether the response is genuinely empathetic, whether a paraphrase is natural, whether a proof claim is legally approved, whether a handoff summary is complete enough for a human.

A deterministic pass is necessary, not sufficient.

---

## 6. Known gaps

| Gap | Why it matters | Planned response |
|---|---|---|
| No live model run | The corpus has not been executed against an LLM | Run layer 4 with recorded responses; then rubric review |
| No tool adapters | Calendar/payment/CRM/handoff behavior is unverified | Build adapters against the contracts; run contract tests |
| Kyrgyz not natively reviewed | Language quality is a claim, not a fact | Native speaker review of skills, phrasebook, scenarios |
| Only 1–2 buyer turns per scenario | Long-horizon state drift is untested | Add 10+ turn scenarios for contradictions, fatigue, and memory |
| No refund/reschedule/cancel scenario | These are high-risk execution paths | Add at least 6 scenarios (refund, partial refund, reschedule, cancel, no-show fee, chargeback) |
| No DST/timezone edge case | Booking errors are costly | Add a DST transition and cross-timezone scenario |
| No webhook race | Payment/booking status can arrive out of order | Add adapter-level tests, not chat scenarios |
| No voice | Explicitly deferred | Keep out of scope for v1 |
| No real customer data | Privacy and realism tradeoff | Use synthetic data; do not commit transcripts |
| No legal review | Jurisdiction-specific rules vary | Counsel review before production |
| No conversion/opt-out measurement | Sales impact and harm are unknown | Production experiment with guardrails |

---

## 7. Coverage claims that are safe to make

- The repository contains 57 written scenarios across the nine requested categories, including a B2C direct-purchase path and scoped-refusal coverage.
- Every scenario has deterministic checks and a rubric focus.
- The scenarios cover the named failure modes at a **design** level.
- The static validator checks the corpus structure and counts.

## Coverage claims that are not safe to make

- "The agent passes 57 tests." It has not been run.
- "The agent is top 0.1%." No benchmark exists.
- "The Kyrgyz copy is production-ready." It is not reviewed.
- "The booking flow works." No adapter exists.
- "The agent increases conversion." No experiment was run.
