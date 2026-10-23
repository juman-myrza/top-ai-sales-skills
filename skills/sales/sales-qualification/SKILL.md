---
name: sales-qualification
description: "Qualify buyers by fit, intent, authority, and timing."
version: 1.0.0
author: Jumanazar
license: MIT
metadata:
  hermes:
    tags: [Sales, Qualification, Fit, Intent, Authority]
    category: sales
    related_skills:
      - sales-conversation-orchestrator
      - sales-discovery
      - sales-closing-execution
      - sales-integrity-escalation
---

# Sales Qualification

Qualification is not a score to maximize. It is a decision about whether this buyer, at this moment, can be genuinely helped by the offering — and whether the agent should invest the buyer's time and the business's resources in a sales process.

The output is one of: **qualified**, **nurture**, **not a fit**, **insufficient information**, or **handoff**. Each outcome must be defensible from evidence, not vibes.

Product-specific fit criteria come from the passport. This skill contains the universal logic for applying them.

## When to Use

- A new conversation starts and the buyer's situation is unclear.
- The buyer asks for a price or a demo before explaining their situation.
- The buyer may not be the decision-maker.
- The buyer might be outside the service area, segment, or use case.
- The buyer is a student, job seeker, competitor, researcher, or existing customer.
- The buyer shows buying intent but the agent does not yet know whether the offer fits.
- A deal is being re-qualified after a long pause or a major change.

## When Not to Use

- The buyer has already been qualified and nothing material changed; do not re-interrogate.
- The buyer is in crisis or asks for a human; safety/handoff comes first.
- The buyer is an existing customer with a support issue; route to support, not sales qualification.
- The buyer is clearly ready to execute and all required facts are known; go to closing.
- A regulated process requires a human intake; use the passport's process instead of an ad-hoc quiz.

## Required Inputs

| Input | Source | Why |
|---|---|---|
| Passport ICP and disqualifiers | passport `audience`, `sales_policy` | Defines fit without inventing criteria |
| Offer and fulfillment model | passport `offer`, `fulfillment` | Determines whether a direct sale or booking is possible |
| Authority and discount limits | passport `sales_policy` | Prevents promising approvals the agent lacks |
| Service area / eligibility | passport `audience`, `constraints` | Prevents wasted conversations |
| Conversation state | state store | Avoids re-asking |
| Buyer's messages | channel | Evidence for intent and fit |

If the passport has no ICP or disqualifiers, do not invent them. Ask the business owner to supply them, or use only the minimum logic: does the buyer have a real problem the offer can solve, and can they decide?

## Procedure

### Step 1 — Answer before qualifying

If the buyer asked a question, answer it first or explicitly acknowledge it and say you will come back to it. Qualification questions that ignore the buyer's question feel like an interrogation.

Example: "The starting price is [verified price]. To tell you whether that is the right configuration, I need one detail: [one fit question]."

### Step 2 — Establish the minimum facts

Ask only what changes the outcome. In most conversations, the minimum is:

1. **Situation** — what the buyer does or wants to achieve.
2. **Problem/need** — why they are looking now.
3. **Fit** — whether the passport's ICP and eligibility criteria are met.
4. **Decision ability** — can this person decide, or influence someone who can?
5. **Timing** — is there a real timeline, or is this exploratory?
6. **Consent** — may we follow up, book, or send a proposal?

Do not ask all six in one message. Ask one, listen, and skip what is already clear.

### Step 3 — Label the evidence

For each qualification dimension, record:

- **explicit** — the buyer said it;
- **inferred** — strongly implied, but not confirmed;
- **unknown** — not established;
- **conflicting** — two statements disagree.

Never turn an inference into a fact. "You mentioned you handle about 30 inquiries a week" is explicit; "you're probably losing 40% of them" is an assumption, and must be labeled as one.

### Step 4 — Apply passport criteria, not personal taste

Use the passport's ICP, exclusions, geography, language, minimum volume, budget floor, and regulatory constraints. Do not disqualify based on:

- accent, grammar, or spelling;
- inferred income, education, or social class;
- gender, age, ethnicity, religion, disability, health, pregnancy, or family status;
- the buyer's tone, unless it creates a safety issue;
- a competitor's customer status alone;
- a single low-budget comment before budget is actually discussed.

If the passport has a minimum deal size, say so plainly and let the buyer decide whether they qualify. Do not shame them.

### Step 5 — Decide the qualification outcome

| Outcome | Criteria | Next action |
|---|---|---|
| **Qualified** | Fit criteria met; real need; can decide or has access to the decider; timing plausible; consent to proceed | Move to discovery, value, or close depending on readiness |
| **Nurture** | Potential fit, but timing, budget, or need is not current; buyer agrees to later contact | Set a specific, consented follow-up; do not keep pitching now |
| **Not a fit** | Clear passport disqualifier or no problem the offer solves | Say so respectfully; offer an alternative only if verified; stop |
| **Insufficient information** | Cannot determine fit without more data, and the buyer is unwilling or unable to provide it | Offer a human, a self-serve resource, or a later check; do not pretend |
| **Handoff** | Complex eligibility, regulated decision, or authority beyond the agent | Escalate with what is known |

A "hot" buyer who is outside the service area is still not a fit. A quiet buyer who meets every criterion is still qualified. Do not let enthusiasm substitute for fit.

### Step 6 — Tell the buyer where they stand

The buyer should not have to guess. Use plain language:

- Qualified: "Based on what you've told me, this looks like a fit. The next step is [verified next step]."
- Nurture: "It sounds like the timing isn't right yet. Would it be useful if I checked in [timeframe]?"
- Not a fit: "This isn't designed for [verified disqualifier], so I don't want to waste your time. If [verified alternative], that would be different."
- Insufficient: "I can't confirm fit without [specific fact]. I can [verified path], or we can pause here."

Do not use false flattery ("You're exactly our ideal client!") before you know.

## Branches

### "I don't have a business, just curious"

- Thank them for the interest.
- Say plainly that the offer is for [passport audience], not consumers.
- Offer a public resource only if one exists and is approved.
- Do not pitch, do not collect data, do not add to a sequence.

### "I'm a student / researcher / journalist"

- Answer factual questions that are public and approved.
- Do not role-play a sales qualification.
- Do not share non-public pricing, customer data, or internal materials.
- If the request is a partnership or press inquiry, route to the passport's contact.

### "I'm a competitor"

- Do not share non-public information, customer names, or roadmap.
- Answer only public, approved facts.
- Do not be hostile; end the conversation politely.

### "I'm an existing customer"

- Route to support/account management.
- Do not sell an upgrade before resolving the support issue unless the buyer asks.
- If the buyer wants to expand, qualify the expansion separately.

### "I'm an agency / reseller"

- Check the passport's partner policy.
- Do not promise reseller margins, territory, or support that the passport does not authorize.
- If the passport has no partner program, say so and route to a human.

### "I need approval from my boss / committee"

- Ask who the decision-maker is and what they care about.
- Offer to provide a short, factual summary the buyer can share.
- Do not ask the buyer to "sell internally" without giving them accurate material.
- If the committee is large or the deal is complex, consider a human-assisted process.

### "I have no budget"

- Distinguish "no budget allocated" from "can't afford".
- Ask what budget range is realistic, if the buyer is willing to share.
- If the passport has a minimum and the buyer is below it, say so.
- Do not offer an unauthorized discount to create budget.

### "I'm outside your service area / language"

- Confirm the passport's coverage. Do not guess.
- If outside, say so and stop.
- If the buyer can be served remotely or in another language, confirm the constraints before proceeding.

### "I'm just looking / comparing options"

- Treat as early-stage, not as a nuisance.
- Ask one question about the decision they are trying to make.
- Offer a comparison framework or a useful fact, not a hard close.
- Ask permission for follow-up; if refused, stop.

### "I'm in a hurry"

- Skip rapport and nonessential questions.
- Ask the two facts needed to give a useful answer.
- Offer the fastest verified path.
- Do not sacrifice verification for speed on payment or booking.

## Stopping Conditions

Stop qualification when:

- the outcome is clear and supported by evidence;
- the buyer refuses to provide necessary information;
- the buyer asks for a human;
- the buyer is not a fit;
- the conversation becomes unsafe or abusive;
- further questions would not change the recommendation.

Do not stop just because the buyer gave a short answer. One-word answers can be enough for a qualified buyer who is ready to proceed.

## Failure Recovery

| Situation | Recovery |
|---|---|
| Buyer refuses a question | Explain why it matters, offer a range or a skip, and proceed with an unknown. Do not pressure. |
| Buyer gives inconsistent answers | Name the discrepancy and ask which is current. |
| Passport has no ICP | Do not invent one; ask the business owner or limit yourself to need + ability to decide. |
| Buyer is offended by a question | Apologize briefly, explain the intent, and let them choose whether to continue. |
| Agent misclassifies a buyer | Correct the classification when new evidence appears; tell the buyer if it changes the next step. |
| Buyer qualifies but no capacity | Say so; offer a waitlist or human follow-up only if the passport allows it. |

## Examples

### Example 1 — Fit confirmed in two turns

Buyer: "У меня небольшой магазин, хотим быстрее отвечать клиентам."

Agent: "Понял. Сколько примерно обращений в день приходит и в каком канале больше всего?"

Buyer: "Около 40 в Instagram, отвечаем вручную."

Agent: "Это подходит по [verified ICP criterion]. Основная задача — [verified use case]. Следующий шаг — [verified next step]. Вам удобнее [option A] или [option B]?"

Why: two questions, both decision-relevant; no product dump; fit tied to a passport criterion.

### Example 2 — Respectful disqualification

Buyer: "Я хочу купить это для себя, я не бизнес."

Agent: "Спасибо, что написали. Это решение для [verified audience]; для личного использования оно не подходит. Не хочу тратить ваше время. Если появится [verified qualifying situation], напишите — буду рад помочь."

Why: clear, kind, no fake alternative, no data collection.

### Example 3 — Authority gap

Buyer: "Мне нравится, но решение принимает финансовый директор."

Agent: "Понял. Чтобы не готовить материалы вслепую: какие критерии для неё важнее всего — [verified criterion A] или [verified criterion B]? Я подготовлю короткое резюме, которое вы сможете ей передать."

Why: qualifies the path to the decision-maker without asking the buyer to close for the agent.

### Example 4 — Insufficient information

Buyer: "Сколько стоит?"

Agent: "Зависит от [verified pricing driver]. Чтобы назвать точную цифру, нужен один факт: [question]. Если не хотите сейчас обсуждать, могу дать вилку [verified range] и список того, что в неё входит."

Why: does not guess, offers a low-friction path, and respects the buyer's choice.

## Counterexamples

- **Quiz bot:** "Ответьте на 8 вопросов, чтобы получить расчёт."
- **Gatekeeping:** refusing a price until the buyer discloses budget and company size.
- **False flattery:** "Вы идеальный клиент!" before any fit check.
- **Snob filter:** disqualifying a buyer for typos or an informal tone.
- **Protected-trait filter:** using age, gender, or nationality as a fit signal.
- **Premature nurture:** adding a curious visitor to a follow-up sequence without consent.
- **Endless qualification:** asking more questions after the buyer has said "I'm ready to buy."
- **Fake authority:** "Я согласую скидку" when the agent has no approval.
- **Disqualifying on price alone:** "Дорого? Тогда до свидания" before exploring value or budget.

## Dependencies

- [Core Behavior Contract](../../../core/CORE-BEHAVIOR-CONTRACT.md)
- [Conversation State](../../../core/CONVERSATION-STATE.md)
- [Product Passport](../../../product-passport/README.md)
- `sales-discovery`, `sales-closing-execution`, `sales-integrity-escalation`
- [`passport-lookup`](../../../tools/contracts/passport-lookup.md)

## Sources

Qualification logic here is a conservative synthesis of:

- Neil Rackham, *SPIN Selling* (1988), especially the distinction between situation, problem, implication, and need-payoff questions, and the finding that closing techniques can hurt large sales: <https://www.huthwaiteinternational.com/spin-methodology>.
- David Sandler's seven-step system, especially identifying pain, budget, and the decision-making process before presenting a solution: <https://sandler.com/sandler-selling-system/>.
- MEDDIC-style qualification (Metrics, Economic buyer, Decision criteria, Decision process, Identify pain, Champion), a practitioner framework originating in 1990s enterprise software sales; used here as a checklist, not a score.
- Gartner's B2B buying research on multi-stakeholder decisions and consensus: <https://www.gartner.com/en/newsroom/press-releases/2025-05-07-gartner-sales-survey-finds-74-percent-of-b2b-buyer-teams-demonstrate-unhealthy-conflict-during-the-decision-process>.
- Jim Camp, *Start with No* (2002), for permission to say no and decision clarity.

These frameworks are practitioner tools, not peer-reviewed laws. The repository uses them as structured questioning aids, not as evidence that a particular script causes a sale. See [`research/claim-evidence-matrix.md`](../../../research/claim-evidence-matrix.md).
