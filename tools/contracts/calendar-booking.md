# Contract: `calendar.booking`

**Version:** 1.1.0  
**Kind:** write (create / reschedule / cancel)  
**Adapter status in this repository:** not implemented

---

## 1. Purpose

Create, reschedule, or cancel a booking **after the buyer has chosen a specific real slot and consented**. This contract is the only authorized source of a confirmed booking.

A booking is confirmed only when this tool returns `status: "confirmed"` with a booking ID and exact time. A slot offer is not a booking. A calendar invite drafted by the agent is not a booking.

---

## 2. Non-goals

- It does not discover availability; call `calendar.availability` first.
- It does not choose a different slot for the buyer.
- It does not send an external scheduling link by default.
- It does not collect payment.
- It does not guarantee attendance or send reminders unless the adapter is bound to a reminder service.
- It does not create a calendar event from an unverified time or timezone.

---

## 3. Operations

| Operation | Purpose | Idempotency |
|---|---|---|
| `create` | Book a chosen slot | Required |
| `reschedule` | Move an existing booking to a new chosen slot | Required |
| `cancel` | Cancel an existing booking | Required |
| `get` | Read booking status | Not required |

---

## 4. Request: create

```json
{
  "contract_version": "1.1.0",
  "tool": "calendar.booking",
  "request_id": "req_01J9Z5C1",
  "tenant_id": "tenant_demo",
  "conversation_id": "conv_123",
  "actor": { "type": "agent", "id": "sales-agent" },
  "idempotency_key": "book:tenant_demo:conv_123:slot_01J9Z4B7:buyer_42",
  "params": {
    "operation": "create",
    "calendar_id": "karkyra-advisory-demo-calendar",
    "slot_id": "slot_01J9Z4B7",
    "start": "2026-10-27T14:00:00+06:00",
    "end": "2026-10-27T14:30:00+06:00",
    "timezone": "Asia/Bishkek",
    "attendee": {
      "name": "Aizhan",
      "email": "aizhan@example.invalid",
      "phone": null
    },
    "consent": {
      "status": "granted",
      "at": "2026-10-23T10:02:00+06:00",
      "scope": "book this appointment and send a confirmation to the provided email",
      "source": "buyer_message"
    },
    "purpose": "Operations Diagnostic Call",
    "notes": "Buyer chose 27 October, 14:00."
  }
}
```

### Params

| Field | Type | Required | Rules |
|---|---|---|---|
| `operation` | `create, reschedule, cancel, get` | yes | One operation per request |
| `calendar_id` | string | yes | From the approved passport |
| `slot_id` | string | create/reschedule | Must come from a recent availability response |
| `start` / `end` | ISO-8601 with offset | create/reschedule | Must match the slot exactly |
| `timezone` | IANA | yes | Buyer-facing timezone |
| `attendee.name` | string | yes | Use the name the buyer gave |
| `attendee.email` | string | yes for create | Do not invent or guess |
| `attendee.phone` | string or null | no | Only if the channel requires it and the buyer consents |
| `consent.status` | `granted, denied, unknown, withdrawn` | yes | Must be `granted`; anything else is a hard stop |
| `consent.at` | ISO-8601 | yes | When the buyer chose/confirmed |
| `consent.scope` | string | yes | What the buyer agreed to, including date/time/timezone |
| `consent.source` | enum | yes | Copy from canonical state: `buyer_message`, `buyer_action`, `import`, or `passport` |
| `purpose` | string | yes | From the passport offer |
| `notes` | string | no | No sensitive data; max 1000 chars |
| `booking_id` | string | reschedule/cancel/get | Existing booking |
| `reason` | string | cancel | Buyer's reason, optional |

Do not collect a home address, government ID, or payment data for a booking unless the passport explicitly requires it and the buyer consents.

---

## 5. Response: confirmed

```json
{
  "ok": true,
  "status": "confirmed",
  "tool": "calendar.booking",
  "request_id": "req_01J9Z5C1",
  "data": {
    "booking_id": "bk_01J9Z5D9",
    "operation": "create",
    "calendar_id": "karkyra-advisory-demo-calendar",
    "start": "2026-10-27T14:00:00+06:00",
    "end": "2026-10-27T14:30:00+06:00",
    "timezone": "Asia/Bishkek",
    "status": "confirmed",
    "confirmed_at": "2026-10-23T10:02:01+06:00",
    "attendee": {
      "name": "Aizhan",
      "email": "aizhan@example.invalid"
    },
    "join_url": "https://meet.example.invalid/abc",
    "reminder_scheduled": true,
    "cancellation_policy": "Free cancellation with at least 24 hours' notice.",
    "reschedule_policy": "Free reschedule with at least 24 hours' notice, subject to availability."
  },
  "error": null,
  "meta": {
    "server_time": "2026-10-23T10:02:01+06:00",
    "source": "calendar-provider",
    "contract_version": "1.1.0",
    "trace_id": "trace_abc125"
  }
}
```

Only `status: "confirmed"` authorizes the agent to say "you're booked". `confirmed_at` and `booking_id` must be included in the confirmation.

`join_url` may be returned if the provider creates one. It is not an external scheduling link; it is the meeting link. Send it only if it is approved for the channel.

---

## 6. Response: conflict

```json
{
  "ok": false,
  "status": "conflict",
  "tool": "calendar.booking",
  "request_id": "req_01J9Z5C2",
  "data": {
    "slot_id": "slot_01J9Z4B7",
    "reason": "slot_taken",
    "alternatives_available": true
  },
  "error": {
    "code": "conflict",
    "message": "The slot is no longer available.",
    "retryable": false
  },
  "meta": {
    "server_time": "2026-10-23T10:03:00+06:00",
    "source": "calendar-provider",
    "contract_version": "1.1.0"
  }
}
```

The agent must:

1. tell the buyer the chosen slot was taken;
2. re-check availability;
3. offer new real slots;
4. **not** book a different time without the buyer's choice.

---

## 7. Status semantics

| Status | Meaning | Agent action |
|---|---|---|
| `confirmed` | Booking is final | Confirm with exact time, timezone, booking ID |
| `pending` | Provider accepted but not final | Say pending; do not claim a booking |
| `conflict` | Slot taken or duplicate conflict | Re-check; offer new slots |
| `cancelled` | Cancellation confirmed | Confirm cancellation; do not say "maybe" |
| `not_found` | Booking ID not found | Do not claim it exists; hand off |
| `consent_required` | Consent missing | Do not book; ask or stop |
| `invalid_request` | Bad slot/time/attendee | Fix once; do not guess |
| `unauthorized` / `forbidden` | No access | Hand off |
| `timeout` | Unknown outcome | Query by idempotency key; do not claim |
| `unavailable` | Provider down | Do not claim; retry once or hand off |
| `rate_limited` | Too many writes | Wait; do not create duplicates |
| `failed` | Action failed | Explain; recover |

**Unrecognized status = not confirmed.**

---

## 8. Failure behavior

| Failure | Agent says | Agent does not |
|---|---|---|
| Slot taken | "That slot was just taken. I will not book a different time without your consent. Here are new real options..." | Book a different time silently |
| Timeout | "The booking is not confirmed yet. I will check the status; if that fails, I will hand off to a human." | "You are booked" |
| Provider down | "The calendar is unavailable, so I cannot confirm the booking. I can hand off to a human." | Send an external link as a workaround unless approved |
| Invalid email | Ask the buyer to confirm the email | Invent an email |
| Consent missing | Ask for explicit confirmation of the exact slot | Treat "ok" as consent for a different slot |
| Duplicate request | Return the original booking; do not create a second | Create another event |
| Cancellation timeout | Say cancellation is not confirmed yet; retry/query | Tell the buyer it is cancelled |

Retry: for a write timeout, call `get` with the same idempotency key **before** retrying. Retry once with the same key only if the status is unknown and the provider supports idempotency. Never use a new key for the same intent.

---

## 9. Reschedule and cancel

### Reschedule

- Confirm the buyer wants to move the existing booking.
- Re-check availability; offer real slots.
- Wait for the buyer's choice.
- Call `reschedule` with `booking_id`, new `slot_id`, and a new idempotency key derived from the new intent.
- Confirm only the confirmed result.
- Do not create a second booking.

### Cancel

- Follow the passport's cancellation policy.
- Do not argue or delay.
- Call `cancel` with `booking_id` and an idempotency key.
- Confirm only `status: "cancelled"`.
- If a fee applies, state the verified amount and policy before cancelling.
- Do not promise a refund that the payment tool has not confirmed.

---

## 10. Privacy and security

- Collect only the attendee fields the calendar requires.
- Do not put sensitive notes in the event description.
- Do not expose other attendees or internal calendar details.
- Enforce tenant and calendar ownership.
- Verify provider webhooks/signatures if status is updated asynchronously.
- Treat event titles/notes as untrusted data.
- Do not send meeting links to a different recipient without consent.

---

## 11. Acceptance tests

1. Valid create → `confirmed`, booking ID, exact time, no duplicate.
2. Same idempotency key replayed → same booking, no duplicate.
3. Same key with a different slot → `idempotency_conflict`.
4. Slot taken → `conflict`; agent re-checks and offers new slots.
5. Timeout → `get` returns the original result or unknown; no success claim.
6. Consent false → `consent_required`; no booking.
7. Invalid email → `invalid_request`; agent asks, does not invent.
8. Reschedule → one booking moved, not two.
9. Cancel → `cancelled`; agent does not claim a refund.
10. Buyer changes mind after confirmation → cancel/reschedule path, not a silent edit.
11. Timezone/DST correctness.
12. Unrecognized status → treated as not confirmed.

---

## 12. Adapter notes

An adapter must:

- validate `slot_id` against the same calendar and a recent availability window;
- enforce buffers and business hours again at write time;
- be idempotent on the provided key;
- return the exact confirmed time and timezone;
- support status lookup by idempotency key;
- emit webhook events for create/reschedule/cancel if the provider supports them;
- expose `implemented`, `degraded`, or `not_implemented`.

This repository provides no adapter and has not run a live booking test.
