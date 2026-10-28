---
name: sales-follow-up
description: "Follow up with consent, context, and a clean stop."
version: 1.1.0
author: Jumanazar
license: MIT
metadata:
  hermes:
    tags: [Sales, Follow-up, Consent, Cadence, Retention]
    category: sales
    related_skills:
      - sales-conversation-orchestrator
      - sales-closing-execution
      - sales-objection-negotiation
      - sales-language-adaptation
      - sales-integrity-escalation
---

# Sales Follow-Up

Follow-up exists to keep a decision moving, not to wear the buyer down. A good follow-up gives the buyer something useful: an answer, a document, a verified deadline, a summary, or a clear next step. A bad follow-up repeats "just checking in" until the buyer blocks the number.

This skill defines eligibility, timing, content, cadence, and stop rules. All cadence numbers, channels, and quiet hours come from the product passport. The skill contains no business-specific schedule.

## When to Use

- The buyer asked to be contacted later, with a date or time.
- Both sides agreed on a next step that has not happened.
- The buyer asked for a document, calculation, or answer that is now ready.
- A proposal or quote was sent and a decision date was agreed.
- The buyer missed a booked appointment and the passport allows a recovery message.
- A purchase is complete and a transactional onboarding check-in is appropriate.
- A customer asked a question that could not be answered in the previous turn.
- The buyer started a sales inquiry and the passport permits a bounded follow-up on that inquiry even though the buyer has not separately consented to marketing.
- A legitimate re-engagement is permitted by consent and the passport.

## When Not to Use

- The buyer refused, opted out, or asked not to be contacted.
- The buyer asked for a human and the handoff is active.
- There is no new information, no agreed next step, no buyer-initiated inquiry, and no consent.
- The passport's `follow_up.basis` does not include any basis that applies to this thread.
- The passport has no cadence and the buyer did not request contact.
- The message would be pure pressure ("just following up", "any update?", "last chance").
- The buyer is in distress, angry, or a safety situation; use the integrity path.
- The purpose is marketing to someone who only consented to a transactional conversation.
- A human has taken over the thread; do not interleave automated messages.

## Required Inputs

| Input | Source | If missing |
|---|---|---|
| Consent to follow up | state / buyer's request | Do not send; ask once or stop |
| Reason for the follow-up | state / agreed next step | Do not send |
| New value or answer to deliver | passport / tool / human | Do not send a content-free reminder |
| Cadence, channel, quiet hours | passport `follow_up` | Send only if the basis and passport allow it; otherwise stop |
| Attempt count and last contact | state / CRM | Treat as unknown; do not restart a sequence |
| Timezone | buyer or passport | Ask before scheduling |
| Opt-out status | state / CRM | Treat as opted out until verified |
| Handoff status | handoff tool | Do not send if a human owns the thread |

## Procedure

### Step 1 — Check eligibility before writing

A follow-up is eligible only if all are true:

1. **Basis:** one of the passport's `follow_up.basis` values applies. That includes `buyer_requested`, `agreed_next_step`, `existing_customer`, and `buyer_initiated_inquiry` (the buyer started the sales inquiry and the passport permits a bounded, transactional follow-up about it). `marketing_consent` is separate and never implied by a sales inquiry.
2. **Consent:** the buyer has not opted out and the purpose matches the consent record.
3. **Reason:** there is a concrete reason code, not "it's been a few days".
4. **Value:** the message will add a fact, answer, document, decision aid, or verified next step.
5. **Ownership:** no human has taken over the conversation.
6. **Timing:** it is inside the passport's cadence and quiet hours.
7. **Channel:** it is an approved channel for this buyer.

A buyer-initiated inquiry is not an opt-in to marketing. It permits a short, relevant continuation of the buyer's own request, within the passport's attempt limit. It never permits an unrelated promotion.

If any answer is no, do not send. Record why.

Reason codes:

| Reason code | Example | Basis |
|---|---|---|
| `buyer_requested` | "Message me on Monday" | `buyer_requested` |
| `agreed_next_step` | "I'll send the calculation by Thursday" | `agreed_next_step` |
| `buyer_initiated_inquiry` | The buyer asked for a price, then went quiet | `buyer_initiated_inquiry` |
| `document_ready` | The proposal or invoice is ready | `agreed_next_step` |
| `answer_ready` | The human/technical answer arrived | `buyer_requested` or `buyer_initiated_inquiry` |
| `appointment_recovery` | The buyer missed a booked appointment | `agreed_next_step` |
| `post_purchase` | Onboarding or delivery check-in | `existing_customer` |
| `re_engagement` | Permitted marketing consent, with something new | `marketing_consent` |

### Step 2 — Choose the timing

Use the passport's `follow_up` policy:

- minimum and maximum interval between touches;
- allowed days and quiet hours;
- maximum attempts per reason and per conversation;
- timezone rules;
- channel preference and fallback order;
- whether a missed appointment triggers a message.

If the passport is silent:

- send only buyer-requested or explicitly agreed follow-ups;
- do not start an unsolicited sequence;
- if the buyer said "later" without a date, ask once for a date instead of guessing;
- when in doubt, wait longer rather than shorter.

Do not send multiple messages in a row to "bump" the thread. Do not switch channels to bypass silence.

### Step 3 — Decide what the message must contain

Every follow-up has four parts:

1. **Context** — why this message is arriving now, in one line.
2. **Value** — the new fact, answer, document, or decision aid.
3. **One ask** — a specific, low-friction next step.
4. **Exit** — an easy way to say no or pause.

Shape:

> [Context]. [New value]. [One ask]. If now is not the right time, tell me and I'll close the loop.

The exit is not a guilt trip. It is a real option, and the agent must honor it.

### Step 4 — Write in the buyer's language and register

Follow `sales-language-adaptation`:

- mirror the latest language;
- keep names, amounts, dates, and document numbers exact;
- do not become more formal or more chummy than the thread;
- keep it short — usually 2–5 sentences;
- do not attach a wall of marketing copy.

### Step 5 — Send through the approved channel

- Use the channel the buyer used, unless the passport requires another.
- Confirm the send with the messaging tool. A drafted message is not a sent message.
- If the send fails, do not claim it was delivered; retry once per contract or log the failure.
- Do not send the same content on two channels "just in case".
- Do not schedule a message outside quiet hours because the tool is convenient.

Scheduling lifecycle:

1. Decide eligibility (Step 1) and the exact time (Step 2).
2. Call the messaging adapter's `schedule_text` or `schedule_template` with the consent record, reason code, timezone, and `send_at`.
3. A `created` response with a `scheduled_message_id` means the message is **queued, not sent**. Record it in `state.follow_up` (`status: scheduled`, `scheduled_message_id`, `next_due_at`).
4. The adapter re-checks consent and opt-out at dispatch. If the buyer opted out or replied, the scheduled message must be cancelled; mark `close_reason`.
5. The message is `sent` only when the adapter returns `sent`.
6. When the buyer replies, mark `follow_up.status: replied` and cancel any pending schedule.

Never tell the buyer a scheduled message was sent. Never let a scheduler bypass an opt-out.

### Step 6 — Interpret the response

| Buyer response | Action |
|---|---|
| Clear yes | Move to `sales-closing-execution`; confirm what happens next |
| Clear no | Acknowledge once; stop the sequence; record opt-out if requested |
| "Later" with a date | Schedule only that date; confirm it |
| "Later" without a date | Ask once for a date; if no date, close the loop |
| Question | Answer it; do not treat it as consent to continue selling |
| Silence | Follow the passport's attempt limit; then close the loop |
| Anger or complaint | Acknowledge, stop selling, offer a human if appropriate |
| "Stop" / "unsubscribe" (and the passport's per-language opt-out keywords) | Stop immediately; one neutral acknowledgment at most |
| Auto-reply / out of office | Do not count it as a real response; follow the stated return date if reliable |
| Wrong person | Ask for the right contact or close politely; do not pitch them |

Silence is not consent. A read receipt is not consent. A click is not consent to a sales sequence.

Distinguish the kinds of silence:

- **Silence after a buyer-initiated inquiry** is not a refusal. If the passport's `basis` includes `buyer_initiated_inquiry`, one or two bounded, value-carrying follow-ups about that inquiry are allowed, then close the loop.
- **Silence after an agreed next step** is not a refusal either, but it is the buyer's timing, not the agent's. Honor the cadence and stop at the limit.
- **Silence after a refusal or an opt-out is not silence at all.** It is a stop. No further sends.

Do not treat the absence of a reply as permission for marketing.

### Step 7 — Update state and close the loop

Record in `state.follow_up` and the CRM:

- reason code, channel, timestamp, and send result;
- basis (`buyer_requested`, `agreed_next_step`, `buyer_initiated_inquiry`, `existing_customer`, or `marketing_consent`);
- lifecycle status (`none`, `eligible`, `scheduled`, `sent`, `replied`, `closed`, `blocked`);
- attempt number for this reason and this conversation;
- buyer response and sentiment;
- `scheduled_message_id` and next scheduled touch, if any;
- opt-out status and any `close_reason`;
- whether the thread is now owned by a human.

When the cadence ends without a response, send at most one clean close-out if the passport allows it. Then stop. Do not restart the sequence under a new reason code to evade the limit.

## Branches

### Buyer says "write later" without a date

Ask once: "When would be convenient - give me a day and I will write only then." If the buyer gives no date, close the loop: "Understood, I will not remind you again. Write when it becomes relevant."

Do not choose a date for the buyer and call it agreed.

### Buyer says "write tomorrow"

Confirm the timezone and the channel. If "tomorrow" is ambiguous because the buyer is in another timezone, state your assumption and ask for confirmation. Schedule one message, not a sequence.

### Buyer says "I need to think"

Do not send a countdown. Ask what would help: a summary, a calculation, a comparison, or time. If the buyer accepts a follow-up date, schedule it. If not, close the loop.

### Buyer asks for a proposal and then goes silent

The proposal follow-up must reference the actual document and a specific open question:

> "I sent proposal [id] on [date]. It covers [one verified point]. Have you had a chance to review [section]? If it is easier, I can answer questions in writing."

Do not send "any thoughts?" with no context.

### Buyer misses a booked appointment

Check the passport's no-show policy. Send one factual message:

> "You had a booking today at [date/time] and did not join. Would you like to reschedule? If you have changed your mind, tell me and I will close the matter."

Do not imply the buyer wasted your time. Do not charge a no-show fee unless the passport authorizes it and the buyer was told in advance.

### Buyer refuses after one follow-up

Acknowledge once and stop. Do not send a "final discount". Do not add them to another sequence. If they only refused the timing, not the offer, ask whether they want a later contact — once.

### Buyer opts out, then asks a question

Answer the factual question. Do not resume the sales sequence. Do not add a pitch to the answer. The opt-out remains in force for marketing.

### Buyer asks to change channel

Move only if the new channel is approved and the buyer confirms. Confirm the switch in one line. Do not keep the old channel active "in case".

### Multiple stakeholders

Follow up with the person who consented. Do not message other stakeholders without their own consent, even if their names came up. Offer the champion a shareable summary instead.

### Out-of-office reply

Use the stated return date only if it is reliable. Do not send during the absence. If the auto-reply is ambiguous, wait for the passport's normal interval.

### Message send fails

Do not claim delivery. Retry once if the contract allows. If it fails again, log it and either try an approved fallback channel with consent or hand off. Do not silently drop the commitment.

### Buyer replies angrily "why are you writing?"

Acknowledge, state the reason in one line, and offer to stop:

> "You asked me to follow up on [date]. If it is no longer relevant, tell me and I will not write again."

If the buyer says stop, stop. Do not defend the cadence.

### Post-purchase follow-up

Keep it transactional and useful: onboarding, access, delivery, or a documented check-in. Do not use a support conversation to upsell unless the buyer asks or the passport has separate marketing consent. Do not ask for a review in exchange for support.

### Handoff is active

Do not send automated sales follow-ups. A human-owned thread may still need a transactional message, but only if the handoff protocol assigns it and the buyer expects it.

## Stopping Conditions

Stop the follow-up sequence immediately when:

- the buyer refuses or opts out;
- the buyer asks for a human;
- the buyer buys, and the next step is fulfillment;
- the buyer is not a fit and has been told;
- the cadence or attempt limit is reached;
- the reason is resolved or no longer valid;
- a safety, legal, or privacy issue appears;
- a human takes ownership;
- the agent cannot verify a material fact and has no path to verify it.

A clean close-out is better than a fourth "just checking in".

## Failure Recovery

| Failure | Response | Do not |
|---|---|---|
| Consent status unknown | Ask once or do not send | Assume opt-in |
| Cadence missing from passport | Send only buyer-requested follow-ups | Invent a sequence |
| CRM/state unavailable | Keep a local note; do not restart the sequence | Claim CRM is updated |
| Send tool fails | Retry once; log; offer human/fallback | Say "sent" without confirmation |
| Duplicate follow-up risk | Check last contact and reason before sending | Send "just in case" |
| Buyer says stop but state is stale | Stop immediately; update state | Send one more "final" message |
| Buyer's language changed | Switch language per `sales-language-adaptation` | Continue in the old language |
| Handoff status unclear | Treat the thread as human-owned; do not send | Interleave automated sales |
| Wrong recipient | Apologize once; ask for the right contact or close | Pitch the wrong person |
| Follow-up reveals a factual error | Correct it, then decide whether the thread should continue | Bury the correction in a pitch |

## Examples

Placeholders must be replaced with verified values.

### Example 1 — Buyer-requested follow-up

Buyer (Monday): "Message me on Wednesday; I will discuss it with the team."

Agent: "Okay, I will write on Wednesday. If questions come up sooner, write here."

Wednesday:

Agent: "Hello! You planned to discuss [verified topic] with your team. I prepared a short summary: [verified scope], [verified price], [verified next step]. Have you had a chance to look? If it is easier, I can answer questions in writing."

Why: honors the agreed date, adds a summary, asks one question, and does not invent urgency.

### Example 2 — Proposal follow-up with a real reason

Agent: "I sent proposal [id] on [date]. It covers [verified key term]. Have you had a chance to review [section]? If you have a question about [verified topic], I will answer here."

Why: references the actual document and a specific section. Not "any update?".

### Example 3 — No response, close-out

Agent: "I will not remind you about this again. If it comes back, write here and I will help. Thank you."

Why: clean exit, no guilt, no fake deadline. The buyer can return without friction.

### Example 4 — Follow-up in the buyer's language (English reference)

Buyer: "Write to me on Wednesday; I will discuss it with the team."

Agent (Wednesday): "Hello! You planned to discuss [verified topic] with your team. I prepared a short summary: [verified scope], [verified price], [verified next step]. Have you had a chance to look? If you have questions, write here."

Why: the reply is written in the buyer's own language and register (see the language-adaptation skill); it keeps the promise, adds value, and asks one question. The body above is the English reference; ship it in the buyer's language.

### Example 5 — Refusal

Buyer: "Do not write anymore, not interested."

Agent: "Understood, I will not write again. Thank you for the reply."

Why: one acknowledgment, no pitch, no "final offer". The sequence ends.

### Example 6 — No-show recovery

Agent: "You had a booking today at [date/time] with [verified role] and did not join. Would you like to reschedule to another real time? If the matter is no longer relevant, tell me and I will close it."

Why: factual, no blame, offers a real path, accepts a no.

## Counterexamples

- **"Just checking in":** no context, no value, no reason.
- **Bumping:** three messages in a row because the buyer is silent.
- **Channel hopping:** WhatsApp, then SMS, then Instagram to bypass silence.
- **Guilt:** "I've been waiting for your reply" or "I don't want to bother you, but…".
- **Fake deadline:** "The price changes tomorrow" without a verified policy.
- **Final-offer theater:** a "last chance" that is not the last chance.
- **Post-refusal pitch:** a discount after "no".
- **Review pressure:** tying support or a refund to a positive review.
- **Stale personalization:** referencing a need the buyer already changed.
- **Cross-stakeholder spam:** messaging the buyer's boss without consent.
- **Claimed delivery:** "I sent it" when the messaging tool failed.
- **Sequence evasion:** restarting the count under a new reason code.

## Dependencies

- [Core Behavior Contract](../../../core/CORE-BEHAVIOR-CONTRACT.md), especially §4 and §7.
- [Conversation State](../../../core/CONVERSATION-STATE.md) for consent, attempts, and next-step fields.
- [Product Passport](../../../product-passport/README.md) for cadence and channel rules.
- `sales-conversation-orchestrator`, `sales-closing-execution`, `sales-language-adaptation`, `sales-integrity-escalation`.
- [CRM and memory contract](../../../tools/contracts/crm-memory.md).
- [Messaging and media contract](../../../tools/contracts/messaging-media.md).
- [Cadence and templates](references/cadence-and-templates.md).

## Sources

- Consent and electronic-marketing rules vary by jurisdiction. This skill follows the conservative rule of explicit, purpose-specific consent and immediate opt-out; it is not legal advice. See the U.S. FTC's CAN-SPAM guidance and the official EU GDPR text on consent: <https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business> and <https://eur-lex.europa.eu/eli/reg/2016/679/oj>.
- The "add value, not reminders" rule is an engineering decision informed by practitioner writing on follow-up, not a controlled study. No response-rate benchmark is claimed.
- Gartner's B2B buying research describes buyers spending more time away from sellers and completing research independently; this supports usefulness over volume but does not prove a specific cadence: <https://www.gartner.com/en/sales/insights/b2b-buying-journey>.
- Agent Skills specification for progressive disclosure: <https://agentskills.io/specification>.

Cadence values are deliberately absent. The business must define them in the passport and test them in its own market.
