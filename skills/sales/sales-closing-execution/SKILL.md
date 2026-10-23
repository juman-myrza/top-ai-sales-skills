---
name: sales-closing-execution
description: "Close, book, invoice, and confirm only verified outcomes."
version: 1.0.0
author: Jumanazar
license: MIT
metadata:
  hermes:
    tags: [Sales, Closing, Booking, Payment, Execution]
    category: sales
    related_skills:
      - sales-objection-negotiation
      - sales-value-proof
      - sales-follow-up
      - sales-integrity-escalation
---

# Sales Closing and Execution

Closing is not a magic phrase. It is the point where the buyer makes a decision and the agent executes it accurately.

This skill covers four execution paths:

1. **Direct purchase** — the buyer agrees to buy a fixed offer; the agent issues the approved payment request.
2. **In-chat booking** — the buyer agrees to an appointment; the agent checks real availability, offers real slots, books, and confirms.
3. **Proposal/quote** — the buyer needs a document or approval before deciding; the agent prepares an accurate proposal within policy.
4. **Human close** — the deal exceeds the agent's authority or capability; the agent hands off with a complete summary.

The universal rule: **no claim of completion without a confirming tool result.**

## When to Use

- The buyer signals readiness: asks how to pay, what the next step is, or says yes.
- The buyer asks to book an appointment, demo, consultation, or visit.
- The buyer asks for an invoice, payment link, or proposal.
- The buyer agrees to terms and the agent needs to execute.
- A previously selected slot or amount needs confirmation.
- A payment or booking status needs to be checked.

## When Not to Use

- The buyer has not agreed to the next step; do not execute.
- A material term is unknown or unverified; do not execute.
- The buyer is still comparing options and has not chosen; help them decide first.
- The request exceeds the passport's authority; hand off.
- The buyer asks for a human; hand off before executing.
- The action would require sensitive data the passport does not authorize.

## Required Inputs

| Input | Source | Required for |
|---|---|---|
| Offer, price, currency, fees, taxes | passport `offer`, `pricing` | direct purchase, proposal |
| Payment methods and terms | passport `pricing`, `fulfillment` | direct purchase |
| Cancellation/refund policy | passport `pricing`, `sales_policy` | confirmation |
| Booking policy, duration, timezone, buffer | passport `fulfillment.booking` | booking |
| Real availability | calendar tool | booking |
| Buyer identity and consent | state | all execution |
| Authority limits | passport `sales_policy` | discounts, custom terms |
| Proposal template | passport `templates` or business file | proposal |
| Handoff route | passport `handoff` | human close |

If a required input is missing, do not improvise. Say what is missing and offer a path.

## Procedure

### Step 1 — Confirm readiness

Readiness is evidence, not hope. Signals include:

- "How do I pay?"
- "Let's do it."
- "Book me for [time]."
- "Send the invoice."
- "We're ready to start."
- "What's the next step?"

A question about price or features is not readiness. A polite "sounds interesting" is not readiness. When unsure, ask one direct question: "Would you like to proceed with [verified option]?"

### Step 2 — Choose the execution path

Use the passport's `fulfillment.mode`:

| Mode | Path |
|---|---|
| `direct_purchase` | summarize → confirm → issue payment request → verify status |
| `appointment` | check availability → offer slots → buyer chooses → book → confirm |
| `quote` | collect scope → prepare proposal → validate → send → agree next step |
| `hybrid` | follow the passport's order (for example, book a call before payment) |
| `human_only` | hand off; do not execute |

Do not force every buyer into a meeting. If the offer is directly purchasable and the buyer is ready, let them buy. Do not force a direct purchase where the passport requires an appointment or human approval.

### Step 3 — Summarize and confirm the terms

Before any irreversible action, restate:

- offer name and scope;
- price, currency, taxes, and fees;
- billing frequency and term;
- what is included and excluded;
- delivery/start date or appointment time;
- cancellation/refund terms;
- the buyer's identity and billing details needed;
- the next step after payment/booking.

Ask for explicit confirmation: "Подтверждаете? / Do you confirm?" Do not treat "ok" as confirmation of a charge unless the context clearly shows the buyer understood the terms. If the amount is material, ask a direct yes/no.

### Step 4A — Direct purchase

1. Confirm the exact offer and amount.
2. Confirm the buyer's billing identity and consent to be charged.
3. Create the payment request or invoice through the approved tool, with an idempotency key.
4. Tell the buyer what was created and how to pay, using only verified details.
5. Do **not** say "paid" until the payment status is confirmed by the tool/webhook.
6. If payment is pending, say it is pending and what happens next.
7. If payment fails, explain the failure in plain language and offer a retry or a human.
8. On confirmed payment, send the receipt/confirmation and the verified next step (onboarding, delivery, access).
9. If the buyer needs an invoice for a finance department, follow the passport's invoicing process; do not invent tax or legal details.

**Never:**
- collect full card numbers in chat;
- send a personal account number not approved by the passport;
- promise a payment link will "expire soon" unless it is true;
- claim a discount or terms that were not approved;
- mark the deal won in the CRM before the payment status confirms it.

### Step 4B — In-chat booking

1. Confirm the buyer wants to book and the purpose/duration.
2. Ask for the preferred date range and timezone if not known. Do not assume the buyer's timezone.
3. Call `calendar.check_availability` with the tenant, calendar, duration, and range.
4. If the tool returns slots, offer **two or three real options** in the chat, with date, time, timezone, and duration.
5. Do not send a Calendly/Cal.com link by default. The buyer stays in the conversation.
6. When the buyer chooses, restate the exact slot and ask for confirmation if there is any ambiguity.
7. Call `calendar.book` with the slot id, buyer identity, consent, and an idempotency key.
8. If the result is `confirmed`, send the confirmation with the exact date/time/timezone and what happens next.
9. If the result is `conflict`/`slot_taken`, apologize briefly, re-check availability, and offer new real slots. Do not book a different time without the buyer's choice.
10. If the result is `failed`/`timeout`, do not claim the booking. Say it is not confirmed, preserve the chosen slot in state, retry once if allowed, then offer a human or a callback.
11. If the buyer needs a reminder or calendar invite, use the approved tool; do not claim it was sent unless confirmed.

**Never:**
- invent availability;
- offer a slot you have not checked;
- book without the buyer's choice;
- confirm a slot the tool has not confirmed;
- double-book by retrying without an idempotency key;
- send an external link "because it's easier".

### Step 4C — Proposal or quote

1. Confirm what the proposal must cover, who will read it, and the decision date.
2. Use the approved template and only verified facts.
3. State assumptions, exclusions, validity dates, and taxes.
4. Do not include unapproved discounts, guarantees, or case studies.
5. If the proposal requires legal/technical review, say so and route it.
6. Send through the approved channel; confirm delivery only if the tool confirms it.
7. Agree on a specific next step after review; do not end with "let me know".

### Step 4D — Human close

1. Explain why a human is needed, without blaming the buyer.
2. Summarize the agreed terms and open questions.
3. Call the handoff tool with the reason code and summary.
4. Pause automated sales messages.
5. Confirm the handoff only if the tool confirms it.
6. Tell the buyer what happens next using only verified timing.

### Step 5 — Confirm what actually happened

A confirmation must include:

- what was executed (booking/payment/proposal/handoff);
- the exact identifier or reference, if the buyer needs it;
- the date/time/timezone for a booking;
- the amount/currency for a payment;
- the next step and who owns it;
- what the buyer should do if something is wrong.

Do not add marketing to the confirmation. Do not ask a new qualifying question. A confirmation is a receipt, not a pitch.

### Step 6 — Close the loop

- Update the CRM/state with the verified result.
- If the buyer agreed to follow-up, schedule it with consent.
- If the buyer did not agree, do not add them to a sequence.
- If the action failed, log the failure and the recovery path.
- If the buyer is a no, mark it and stop.

## Branches

### Buyer says "I'll pay later"

- Ask when and how; check the passport's payment terms.
- Do not reserve inventory or a slot indefinitely unless the passport allows it.
- If a hold is allowed, state the expiry and confirm it.
- Do not claim a payment is "reserved".

### Buyer asks for a payment link

- Use the approved payment tool; send the link only if it is the passport's approved method.
- Do not send a raw bank account or personal wallet unless explicitly approved.
- Explain fees/currency if relevant.

### Buyer asks for an invoice before payment

- Follow the passport's invoicing process.
- Confirm the legal entity, billing details, and purchase order requirement.
- Do not invent tax IDs or payment terms.
- If the amount is unusual, hand off.

### Buyer wants a slot that is not available

- Say it is not available; do not imply it is.
- Offer the nearest real alternatives.
- If the buyer needs a specific time, offer a waitlist or human follow-up if approved.
- Do not overbook or promise a "maybe".

### Slot is taken between offer and confirmation

- Acknowledge the race plainly: "That slot was taken while we were confirming."
- Re-check availability.
- Offer new real options.
- Do not silently book a different time.

### Buyer needs to reschedule

- Check the passport's rescheduling policy.
- Check availability.
- Confirm the new slot.
- Cancel/rebook through the tool; do not create a duplicate.
- Confirm only the confirmed result.

### Buyer asks to cancel

- Follow the passport's cancellation policy.
- Do not argue or delay.
- Process the cancellation through the tool.
- Confirm only the confirmed result.
- If a refund is due, explain the verified timeline.

### Payment fails

- Do not retry blindly; check the error.
- Explain the likely cause in plain language (card declined, timeout, currency, bank).
- Offer a retry or another approved method.
- Do not ask for card details in chat.
- If repeated, hand off.

### Booking tool is down

- Say the calendar is unavailable; do not invent slots.
- Offer a human handoff or a specific time to check back.
- If the buyer agrees, set a follow-up with consent.
- Do not send an external link as a workaround unless the passport explicitly allows it and the buyer agrees.

### Buyer wants a custom contract

- Do not draft legal terms.
- Capture the request and hand off to a human with authority.
- Do not promise the terms will be accepted.

### Buyer is ready but the passport has no payment method

- Do not improvise.
- Explain that the payment path needs confirmation.
- Hand off or arrange a callback.
- Do not take money through an unapproved channel.

## Stopping Conditions

Stop execution when:

- the action is confirmed and the buyer has the confirmation;
- the buyer withdraws consent;
- a required fact is missing and cannot be verified;
- the tool fails after the allowed retries;
- the request exceeds authority;
- the buyer asks for a human;
- a legal/safety issue appears.

Do not stop at "I sent the request" unless the tool confirms it was sent. Do not stop at "I'll book it" without a result.

## Failure Recovery

| Failure | Agent response | Do not |
|---|---|---|
| Availability timeout | "I can't confirm the calendar right now. I can retry or pass this to a human." | Invent slots or say "probably available" |
| Booking conflict | "That slot was taken. Here are the current options." | Book a different time silently |
| Booking timeout | "The booking is not confirmed yet. I'll retry / hand off." | Say "you're booked" |
| Payment timeout | "The payment status is pending. I won't mark it paid until it's confirmed." | Send a second charge without idempotency |
| Invoice tool error | "I couldn't issue the invoice. I can retry or have a human issue it." | Invent an invoice number |
| Handoff tool error | "I couldn't create the handoff automatically. Here is what I can do…" | Claim a human is already handling it |
| CRM write failure | Keep the state locally; retry; tell the buyer only if it affects them. | Claim the CRM is updated |
| Duplicate request | Check idempotency key/status before retrying. | Create a second booking/charge |

## Examples

### Example 1 — Direct purchase

Buyer: "Готовы. Как оплатить?"

Agent: "Отлично. Фиксирую: [verified offer], [verified price] [currency], [verified billing period], [verified included/excluded]. Оплата — [verified method]. Подтвердите, пожалуйста, что условия верны, и я выставлю счёт."

Buyer: "Да, верно."

Agent: "Счёт [invoice id] создан на [amount] [currency]. Ссылка на оплату: [verified payment link]. После оплаты пришлю подтверждение и [verified next step]. Если ссылка не открывается, скажите — помогу."

After webhook: "Оплата подтверждена. [Receipt/next step]. Спасибо."

Why: terms first, consent, verified invoice, no claim of payment before confirmation.

### Example 2 — In-chat booking

Buyer: "Хочу записаться на консультацию."

Agent: "Конечно. Консультация — [verified duration], [verified timezone]. Вам удобнее на этой неделе или в начале следующей?"

Buyer: "На этой."

Agent: [checks calendar] "Есть два реальных окна: [date/time A] и [date/time B]. Какое выбрать?"

Buyer: "A."

Agent: [books with consent] "Подтверждаю: [date/time A], [timezone], [duration]. Запись [booking id] создана. За день до визита придёт напоминание, если оно включено в [verified process]. Если планы изменятся — [verified reschedule policy]."

Why: real slots, buyer chooses, booking confirmed only after the tool, exact details.

### Example 3 — Slot taken

Agent: "Есть [slot A] и [slot B]."

Buyer: "A."

Agent: [booking returns conflict] "К сожалению, [slot A] только что заняли. Не буду записывать вас на другое время без вашего согласия. Сейчас есть [slot C] и [slot D]. Какой подходит?"

Why: transparent, no silent substitution, re-checks real availability.

### Example 4 — Payment pending

Buyer: "Оплатил."

Agent: "Спасибо. Проверяю статус… [tool says pending]. Платёж пока в обработке, подтверждения от банка ещё нет. Я не буду отмечать его как оплаченный, пока статус не изменится. Обычно это занимает [verified time]. Если через [time] статус не изменится, я передам вопрос человеку."

Why: does not take the buyer's word as payment confirmation; gives a verified expectation.

### Example 5 — No external link

Buyer: "Скиньте Calendly, я сам выберу."

Agent: "Могу записать прямо здесь — так быстрее и без перехода на другой сайт. Есть [slot A] и [slot B]. Какое время удобнее?"

Why: respects the in-chat booking policy and offers a concrete alternative.

## Counterexamples

- **False confirmation:** "Записал вас на завтра" without a booking result.
- **External link reflex:** sending a scheduling link before checking availability.
- **Silent substitution:** booking a different slot when the chosen one is taken.
- **Payment fiction:** "Оплата прошла" because the buyer said so.
- **Double charge:** retrying a payment without checking status/idempotency.
- **Card data collection:** asking for full card number, CVV, or password in chat.
- **Unapproved account:** sending a personal wallet or bank account.
- **Skipping terms:** charging before the buyer sees the price, currency, and cancellation policy.
- **Marketing after confirmation:** "Кстати, у нас есть ещё..." instead of a clean receipt.
- **Forcing a meeting:** refusing a direct purchase when the passport allows it.

## Dependencies

- [Core Behavior Contract](../../../core/CORE-BEHAVIOR-CONTRACT.md)
- [Conversation State](../../../core/CONVERSATION-STATE.md)
- [Product Passport](../../../product-passport/README.md)
- `sales-objection-negotiation`, `sales-follow-up`, `sales-integrity-escalation`
- [`calendar-availability`](../../../tools/contracts/calendar-availability.md)
- [`calendar-booking`](../../../tools/contracts/calendar-booking.md)
- [`payments-invoicing`](../../../tools/contracts/payments-invoicing.md)
- [`crm-memory`](../../../tools/contracts/crm-memory.md)
- [`human-handoff`](../../../tools/contracts/human-handoff.md)

## Sources

- Neil Rackham, *SPIN Selling* (1988), for obtaining commitment as a stage and the warning that closing techniques can be counterproductive in large sales: <https://www.huthwaiteinternational.com/spin-methodology>.
- David Sandler's seven-step system, especially the up-front contract and post-sell confirmation: <https://sandler.com/sandler-selling-system/>.
- Chris Voss, *Never Split the Difference* (2016), for calibrated questions and "that's right" moments before commitment.
- Agent Skills specification, for the skill's structure and progressive disclosure: <https://agentskills.io/specification>.
- Tool contracts in this repository define the only permitted execution semantics. They are specifications, not implementations; the runtime must supply real tool adapters before this skill can execute a transaction.

The in-chat booking preference is a business/product decision based on the owner's requirements, not an empirically proven universal best practice. It should be A/B tested per market. See [`research/decisions-and-tradeoffs.md`](../../../research/decisions-and-tradeoffs.md).
