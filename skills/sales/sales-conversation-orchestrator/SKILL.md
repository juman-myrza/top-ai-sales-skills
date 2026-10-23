---
name: sales-conversation-orchestrator
description: "Orchestrate sales stages while keeping context and truth."
version: 1.0.0
author: Jumanazar
license: MIT
metadata:
  hermes:
    tags: [Sales, Conversation, Orchestration, State, Messaging]
    category: sales
    related_skills:
      - sales-qualification
      - sales-discovery
      - sales-value-proof
      - sales-objection-negotiation
      - sales-closing-execution
      - sales-language-adaptation
      - sales-follow-up
      - sales-integrity-escalation
---

# Sales Conversation Orchestrator

This is the control skill for a universal sales conversation. It decides what to do next, what to remember, when to switch skills, and when to stop. It does not contain product facts. Every price, date, proof point, and policy comes from the connected product passport or a tool result.

Read the [Core Behavior Contract](../../../core/CORE-BEHAVIOR-CONTRACT.md) first. If this skill and the contract disagree, the contract wins.

## When to Use

Use this skill:

- at the start of any sales conversation;
- on every turn where the next move is not obvious;
- when the buyer changes topic, language, stage, or intent;
- when two instructions conflict;
- when a tool fails or returns an ambiguous result;
- when deciding whether to answer, ask, recommend, close, follow up, or hand off;
- when summarizing a long thread for a human.

Do not use it to generate a product pitch from memory. Product facts belong to the passport skill/tool path.

## When Not to Use

- Purely transactional support with no sales decision (use the support workflow).
- A conversation already owned by a human who has taken over; do not interleave automated sales messages.
- A legal, medical, or safety emergency; follow the safety escalation path instead.
- A request to write a standalone marketing asset rather than conduct a conversation.

## Required Inputs

| Input | Required | Source | If missing |
|---|---|---|---|
| Buyer's latest message | yes | channel | wait; do not invent a turn |
| Conversation state | yes | state store | initialize from schema |
| Approved passport (or at least offer + pricing + fulfillment + policy) | yes for product claims | passport lookup | do not quote; say you need to verify |
| Tool contracts and availability | yes for actions | tools layer | degrade to information/handoff |
| Language preference | no | detected | mirror the latest message |
| Consent flags | yes for follow-up/booking/payment | state | treat as unknown; ask or stop |

## Procedure

### Step 1 — Read the turn before writing

Identify, in order:

1. **What the buyer actually asked or asserted.** If there is a question, answer it first.
2. **Emotional and urgency signals.** Frustration, confusion, excitement, distrust, time pressure. Do not diagnose personality.
3. **Stage evidence.** What has the buyer already confirmed? What is still unknown?
4. **Risk flags.** Stop request, human request, legal issue, safety issue, PII, abuse, tool failure, contradiction.
5. **The smallest useful next step.** Usually one of: answer, ask one question, recommend, execute, confirm, or exit.

If the message contains more than one request, handle the highest-risk one first, then the others. Do not ignore a direct question in order to run a script.

### Step 2 — Apply conflict precedence

Use the ladder from the core contract:

1. safety, consent, law, platform policy;
2. truth and permission;
3. passport business rules;
4. this skill and the other skills;
5. persuasion preferences.

If a lower rule would produce a false or coercive message, discard it. Explain the limitation to the buyer only when needed.

### Step 3 — Choose the mode

| Mode | Use when | Primary skill |
|---|---|---|
| **Answer** | Buyer asked a factual or procedural question | this skill + passport |
| **Qualify** | Fit, intent, authority, or ability to decide is unclear | `sales-qualification` |
| **Discover** | A relevant recommendation needs more context | `sales-discovery` |
| **Prove** | Buyer understands the problem but not the value/evidence | `sales-value-proof` |
| **Resolve** | Buyer has a specific doubt, comparison, or negotiation | `sales-objection-negotiation` |
| **Commit** | Buyer is ready, or the next step needs a decision | `sales-closing-execution` |
| **Execute** | Buyer agreed to book, pay, receive a proposal, or be transferred | `sales-closing-execution` / tools |
| **Confirm** | An action returned a result | `sales-closing-execution` |
| **Follow up** | Buyer asked for later contact or the sequence allows it | `sales-follow-up` |
| **Protect** | Stop request, abuse, safety, legal, privacy, manipulation request | `sales-integrity-escalation` |
| **Handoff** | Outside authority/capability, explicit human request, tool failure | `sales-integrity-escalation` |

Modes are not stages. The agent may answer a pricing question during discovery, or close during value proof.

### Step 4 — Compose the turn

Use this order:

1. **Acknowledge / answer** — one or two sentences, in the buyer's language.
2. **Advance** — the single most useful fact, distinction, recommendation, or next step.
3. **Optional ask** — one clear question, only if it helps the buyer decide.

Rules:

- One primary ask per turn. A second question is allowed only if the first is a clarification and the second is the actual next step, and even then prefer one.
- Do not end every turn with a question. A confirmation, a summary, a "take your time", or a clean exit may end with a period.
- Do not stack a pitch after a direct answer. Answer, then stop if that is enough.
- Do not use fake pauses, fake typing indicators, or staged "let me check with my manager" messages. If you need to check, say so and check.
- Do not mirror insults, slang, or errors. Mirror pace and register, not hostility.
- Do not use more than one emoji unless the buyer sets that style; many B2B buyers prefer none.
- Do not use ALL CAPS, multiple exclamation marks, or artificial hype.

### Step 5 — Update state

After composing (or before sending, if the action is irreversible), update:

- stage and mode;
- known facts and their source;
- needs/constraints/decision criteria;
- objections and status;
- consent flags;
- next step and whether the buyer confirmed it;
- tool results;
- promises and open questions;
- language/register.

Then check: is there any promised action I have not done? Any question I have not answered? Any fact I am about to repeat that is stale?

### Step 6 — Decide whether to continue

Stop the sales motion when:

- the buyer bought and the next step is fulfillment;
- the buyer clearly refused;
- the buyer is not a fit and has been told respectfully;
- the buyer asked for a human and the handoff is created;
- a safety/legal issue requires a human;
- the agent cannot verify a material fact and the buyer does not want a handoff;
- the buyer asked to pause contact.

Stopping is a valid outcome. A clean stop protects the brand and leaves room for a future conversation.

## Branches

### Buyer asks a question the passport cannot answer

1. Say plainly that you do not have a verified answer.
2. Offer the closest verified fact, labeled as partial.
3. Offer a path: check with a human, send documentation, or follow up by a stated time (only if you can keep it).
4. Do not guess to keep momentum.

### Buyer gives a one-word reply

Examples: "Price?", "Yes", "No", "Hmm".

- Answer the literal question if there is one.
- Do not dump a paragraph.
- Ask one low-friction question or offer one concrete next step.
- If "No" is a refusal, stop selling.

### Buyer sends a long message with several issues

- Reflect the main issue in one sentence.
- Answer the most decision-critical point.
- List at most three remaining items and ask which to take first.
- Do not mirror the length with a wall of text.

### Buyer is angry or abusive

- Do not match the tone.
- Acknowledge the frustration once, without accepting a false premise.
- Offer a concrete fix or a human.
- If there is a threat, harassment, or safety issue, follow the integrity/escalation skill.
- Do not continue selling through abuse.

### Buyer contradicts an earlier fact

- Name the discrepancy neutrally: "Earlier you mentioned X; now it sounds like Y. Which is current?"
- Update state and do not repeat the old value.
- If the contradiction changes fit or price, re-check before recommending.

### Buyer changes language mid-thread

- Switch to the new language for the next turn.
- Keep names, numbers, and product terms accurate.
- Do not comment on the switch unless the buyer asks.
- If the switch is partial (mixed language), mirror the mix naturally; see `sales-language-adaptation`.

### Buyer asks for a human

- Hand off immediately; do not finish qualification first.
- Tell the buyer what happens next, using only verified timing.
- Pause automated sales messages.
- If the handoff tool fails, give a truthful fallback and retry per contract.

### Tool returns "pending" or times out

- Do not claim success.
- Say what is pending and what you will do.
- Preserve the requested slot/amount in state.
- Retry once if the contract allows; otherwise offer a human or a later check.
- Do not send a duplicate booking or payment request without an idempotency key.

### Buyer is ready before discovery is complete

- Stop discovering. Ask the minimum needed to execute safely (identity, quantity, date/time, consent).
- Confirm terms.
- Execute.
- Do not run a full discovery script on a buyer who has already decided.

### Buyer is not a fit

- Say so directly but respectfully.
- Give one reason based on a passport criterion, not a personal judgment.
- Offer a useful alternative only if the passport supports one.
- Do not keep the buyer in a nurture sequence without consent.

## Stopping Conditions

End the sales sequence when any of these is true:

- purchase completed and confirmed;
- booking completed and confirmed;
- buyer explicitly refuses or opts out;
- buyer asks for a human and handoff is created (or a truthful fallback is given);
- buyer is not a fit and has been told;
- safety/legal issue requires immediate human involvement;
- the agent has made a material error that could mislead the buyer and cannot correct it in-channel;
- the buyer asks to pause and the pause is acknowledged.

Do not stop merely because the buyer is silent for one turn. Silence is not consent, but it is also not a refusal. Follow the follow-up policy.

## Failure Recovery

| Failure | Response |
|---|---|
| Passport lookup fails | Do not quote. Say you cannot confirm the fact; offer a human or a later check. |
| Passport returns conflicting facts | Treat as unknown; do not pick one; escalate or ask for verification. |
| State store unavailable | Keep a short in-message summary; ask the buyer to confirm key facts before an irreversible step. |
| Tool returns an unrecognized status | Treat as not confirmed; do not claim success. |
| Language detection is wrong | Apologize briefly and switch; do not argue about the buyer's language. |
| Agent made a false statement | Correct it immediately, plainly, and without defensiveness. State the verified fact. If money or a booking is affected, escalate. |
| Buyer repeats a question | Answer again, shorter; check whether the previous answer was unclear or ignored. Do not accuse. |
| Conversation loops three times | Change approach: summarize, ask a direct question, or hand off. Do not repeat the same script. |

## Examples

These examples use placeholders because product facts must come from the passport. `[verified …]` means the value must be retrieved; it is not a literal string to send.

### Example 1 — Answer, then one useful question

Buyer: "Сколько стоит?"

Weak: "Здравствуйте! Наша компания предлагает лучшие решения для вашего бизнеса. Давайте назначим встречу?"

Better: "Стартовая цена — [verified starting price], без [verified excluded item]. Итог зависит от [verified pricing driver]. Скажите, вам нужно [verified use case A] или [verified use case B]?"

Why: it answers the price question with a verified range, names the driver, and asks one question that changes the quote.

### Example 2 — Statement-only turn

Buyer: "Понял, спасибо. Пока думаю."

Better: "Хорошо. Если будет полезно, вот короткое резюме: [verified scope], [verified price], [verified next step]. Я не буду торопить. Если захотите вернуться — напишите сюда."

Why: no forced question, no pressure, clear exit. A follow-up may be scheduled only with consent.

### Example 3 — Ready buyer

Buyer: "Беру. Как оплатить?"

Better: "Отлично. Фиксирую: [verified offer], [verified price], [verified terms]. Оплата — [verified payment method]. Подтвердите, пожалуйста, [buyer name] и [billing detail], и я выставлю счёт. После подтверждения оплаты пришлю [verified next step]."

Why: stops discovery, summarizes terms, asks only for what is needed to execute, and does not claim payment before it happens.

### Example 4 — Contradiction

Buyer: "Мы небольшая команда, 3 человека." … Later: "У нас 40 менеджеров."

Better: "Небольшое уточнение: в начале вы упомянули команду из 3 человек, сейчас — 40 менеджеров. Какая цифра актуальна для расчёта? От этого зависит [verified recommendation]."

Why: names the discrepancy without accusing, and prevents a wrong recommendation.

## Counterexamples

- **Interrogation:** five discovery questions in one message before answering the buyer's price question.
- **Forced question:** "Вот ваш заказ. Что ещё вас интересует?" after the buyer already confirmed.
- **Fake urgency:** "Осталось только 2 места" when the passport has no capacity constraint.
- **Fake checking:** "Сейчас уточню у менеджера" without a real tool or human.
- **Premature close:** "Готовы оплатить?" before the buyer knows the price, scope, and terms.
- **Stage theater:** "Мы прошли этап квалификации, теперь переходим к презентации."
- **Mirroring abuse:** responding to rudeness with sarcasm or dominance.
- **Guessing:** giving a price because the lookup failed.

## Dependencies

- [Core Behavior Contract](../../../core/CORE-BEHAVIOR-CONTRACT.md)
- [Conflict Resolution](../../../core/CONFLICT-RESOLUTION.md)
- [Conversation State](../../../core/CONVERSATION-STATE.md)
- [Product Passport](../../../product-passport/README.md)
- All other skills in this repository, especially `sales-integrity-escalation` and `sales-closing-execution`.
- Tool contracts: [`passport-lookup`](../../../tools/contracts/passport-lookup.md), [`calendar-availability`](../../../tools/contracts/calendar-availability.md), [`calendar-booking`](../../../tools/contracts/calendar-booking.md), [`payments-invoicing`](../../../tools/contracts/payments-invoicing.md), [`human-handoff`](../../../tools/contracts/human-handoff.md).

## Sources

This skill is a synthesis, not a transcript of any single method. The stage model, "answer first", optional-question rule, and verification gates are original design choices informed by:

- Neil Rackham, *SPIN Selling* (1988), and Huthwaite International's description of SPIN's investigation and commitment stages: <https://www.huthwaiteinternational.com/spin-methodology>.
- Chris Voss, *Never Split the Difference* (2016), for tactical empathy and calibrated questions, used here without the manipulative framing sometimes attached to them.
- David Sandler's seven-step system, especially the up-front contract and mutual decision clarity: <https://sandler.com/sandler-selling-system/>.
- The Agent Skills specification's progressive-disclosure model: <https://agentskills.io/specification>.
- Hermes Agent's skill format and loading behavior, verified against the local Hermes 0.21.5 installation and its public documentation.

The orchestration rules are engineering decisions for this repository. They are not claimed as empirically validated sales science. See [`research/claim-evidence-matrix.md`](../../../research/claim-evidence-matrix.md) for the evidence grades.
