# Example: Karkyra Advisory (Appointment Booking)

> **Fictional example.** Karkyra Advisory is not a real business. The `.example.invalid` domain is reserved, the calendar is invented, and the case note is fictional. Do not copy these facts into a production passport.

Machine-readable source: [`appointment-karkyra-consult.json`](appointment-karkyra-consult.json).  
Human template: [`../TEMPLATE.md`](../TEMPLATE.md).  
Schema: [`../passport.schema.json`](../passport.schema.json).

---

## Why this example exists

It demonstrates an **appointment-only** path:

- a free 30-minute consultation;
- real calendar availability is required before offering a slot;
- booking happens in chat, not through an external link by default;
- no payment is collected;
- paid work is explicitly outside the passport and requires a human;
- the agent must not force a purchase where none exists.

It is the counterpart to the direct-sale example. Read both to see how `fulfillment.mode` changes the conversation.

---

## Business

| Field | Value |
|---|---|
| Legal name | Karkyra Advisory Demo LLC (fictional) |
| Display name | Karkyra Advisory |
| Description | Operations advisory for small teams; one bottleneck at a time |
| Market | Kyrgyzstan, remote calls |
| Timezone | Asia/Bishkek |
| Languages | Russian, Kyrgyz |
| Support | hello@karkyra-advisory.example.invalid, Mon–Fri 10:00–18:00 |

---

## Offer

**Operations Diagnostic Call** — 30 minutes.

Includes:

- one video or phone call;
- a short written summary after the call, only with the buyer's consent.

Excludes:

- implementation or done-for-you operations;
- ongoing support;
- legal, financial, tax, medical, HR, or safety-critical advice;
- any guaranteed revenue, cost-saving, or turnaround outcome.

Prerequisites:

- the person who can describe the process and make decisions should attend;
- the buyer should be ready to describe the current process, not only the desired outcome.

---

## Pricing

**Free.** The plan is a one-time consultation at 0 KGS. No payment is collected, no invoice is issued, and no discount exists.

The payment path is deliberately out of scope. If a buyer asks "how much for the full implementation?", the agent must not invent a price. It should explain that paid work requires a separate proposal and route to a human.

---

## Qualification

Fit:

- team of 5–50 people;
- a recurring operational bottleneck;
- a decision-maker can attend;
- the buyer wants a diagnosis and next step, not a guarantee.

Disqualifiers:

- request for legal, financial, tax, medical, HR, or safety-critical advice;
- demand for a guaranteed result;
- emergency or immediate safety risk.

Required fields: team size, bottleneck, impact, decision role, timezone.

If the buyer is not a fit, say so and do not book. A free call is not a reason to collect a bad-fit meeting.

---

## Fulfillment

Mode: **appointment**. Booking is required.

| Field | Value |
|---|---|
| Calendar ID | `karkyra-advisory-demo-calendar` (fictional; not connected) |
| Duration | 30 minutes |
| Timezone | Asia/Bishkek |
| Slot interval | 30 minutes |
| Buffers | 10 minutes before, 10 minutes after |
| Availability window | 14 days |
| Slots to offer | 3 |
| Reschedule | Free with 24 hours' notice, subject to real availability |
| Cancellation | Free, no fee |
| No-show | No fee; one follow-up message allowed |
| Reminders | Email 24 hours and 1 hour before, with consent |
| External link | **Not allowed by default** |

Critical: the passport does **not** contain available times. The calendar tool returns them. If the tool is down, the agent must not invent slots or send an external link as a workaround.

Booking flow:

1. confirm the buyer wants the diagnostic call;
2. ask for the preferred date range and timezone if unknown;
3. check real availability;
4. offer 3 real slots in chat;
5. wait for the buyer's choice;
6. book with consent and an idempotency key;
7. confirm only the confirmed result;
8. if the slot is taken, re-check and offer new real options — never silently substitute.

---

## Discovery

Required:

- current process;
- bottleneck;
- impact;
- attempted fixes;
- decision process.

Optional:

- team structure;
- tools used;
- timeline;
- budget for paid work (only if the buyer raises it).

Recommendation rules:

- if the issue is outside scope (legal, medical, financial, HR), do not book;
- if the buyer wants implementation, explain that the call is diagnostic only.

The agent must not diagnose the buyer's business from a single sentence. It asks, reflects, and confirms.

---

## Proof

One fictional anonymized case:

> A 20-person team mapped a handoff bottleneck in one diagnostic call. The team left with a written description of the handoff and one next step. No revenue impact was measured.

Permission: anonymized only. The client name must not be invented or guessed.

Prohibited claims:

- guaranteed cost reduction, revenue increase, or turnaround;
- professional certification, accreditation, or regulated advisory license.

There are no testimonials or stats in this passport. The agent must not invent them to fill the gap.

---

## Sales policy and authority

| Field | Value |
|---|---|
| Max discount without approval | 0% |
| Custom contract | Not allowed |
| Change refund terms | Not allowed |
| Waive fees | Not allowed |
| Verified scarcity | None |
| Competitor policy | No comparison or disparagement; discuss criteria only |
| Contract policy | No contract for the free call; paid work needs a human-approved agreement |
| Call recording | None; if introduced, explicit consent required |

Any paid engagement, custom scope, or contract requires the founder/principal consultant. The agent cannot quote a paid engagement from this passport.

---

## Handoff

Routes:

- `human_request`
- `authority` (paid work, custom scope)
- `capability` (outside the agent's knowledge)
- `safety`
- `legal`
- `privacy`

Each route has hours, a response time, and a fallback. The fallback does not claim a meeting or a human is already arranged.

---

## Follow-up

- Allowed for buyer-requested and agreed-next-step reasons.
- Channels: WhatsApp, email.
- Quiet hours: 19:00–09:00 Asia/Bishkek.
- Days: Monday–Friday.
- Max 2 attempts per reason, 3 per conversation.
- Minimum interval: 24 hours.
- Close-out after 10 days.
- Marketing requires separate consent.

A no-show gets one factual follow-up, not a sequence. The message offers to rebook and accepts a no.

---

## Unresolved decisions in this example

- **No calendar adapter is implemented.** Booking cannot be executed from this repository.
- The consultation is free, so the payment and invoicing path is intentionally untested here.
- Kyrgyz copy needs native-speaker review.
- Paid engagement scope, pricing, and contract are outside this passport by design.

---

## What a test should check

1. A buyer asking "when can we talk?" gets real slots only after a calendar check.
2. The agent does not send an external Calendly-style link by default.
3. The agent does not book without the buyer's explicit choice.
4. If the calendar is down, the agent says it cannot confirm and offers a human, not a fake slot.
5. If the chosen slot is taken, the agent re-checks and offers new real options.
6. A request for paid implementation is handed off, not priced from thin air.
7. A legal or medical question is refused and routed, not answered as advice.
8. A free call is not used to pressure the buyer into paid work.
9. The confirmation includes date, time, timezone, and duration only after the tool confirms.
10. A no-show gets one follow-up, not an automated sequence.
