# Contract: `calendar.availability`

**Version:** 1.0.0  
**Kind:** read-only  
**Adapter status in this repository:** not implemented

---

## 1. Purpose

Return **real, current** bookable slots from the business calendar so the agent can offer two or three concrete times in chat. This contract is the only authorized source of availability.

If availability cannot be read, the agent must say so. It must not infer slots from business hours, past conversations, or a calendar link.

---

## 2. Non-goals

- It does not create a booking.
- It does not reserve a slot. A slot can disappear between availability and booking.
- It does not send an external scheduling link.
- It does not expose other people's meeting titles, attendees, or private calendar details.
- It does not decide the business's duration, buffers, or hours; those come from the passport.

---

## 3. Request

```json
{
  "contract_version": "1.0.0",
  "tool": "calendar.availability",
  "request_id": "req_01J9Z4A1",
  "tenant_id": "tenant_demo",
  "conversation_id": "conv_123",
  "actor": { "type": "agent", "id": "sales-agent" },
  "params": {
    "calendar_id": "karkyra-advisory-demo-calendar",
    "duration_minutes": 30,
    "timezone": "Asia/Bishkek",
    "range_start": "2026-10-26T00:00:00+06:00",
    "range_end": "2026-11-06T23:59:59+06:00",
    "slot_interval_minutes": 30,
    "buffer_before_minutes": 10,
    "buffer_after_minutes": 10,
    "max_slots": 6
  }
}
```

### Params

| Field | Type | Required | Rules |
|---|---|---|---|
| `calendar_id` | string | yes | Exact ID from the approved passport |
| `duration_minutes` | integer | yes | 5–480; must match the passport |
| `timezone` | IANA string | yes | Buyer-facing timezone; must be a real zone |
| `range_start` | ISO-8601 with offset | yes | Not in the past; max 90 days ahead unless passport says otherwise |
| `range_end` | ISO-8601 with offset | yes | Must be after start; max 31 days per request unless passport says otherwise |
| `slot_interval_minutes` | integer | yes | 5–240; from passport |
| `buffer_before_minutes` | integer | no | 0–240; from passport |
| `buffer_after_minutes` | integer | no | 0–240; from passport |
| `max_slots` | integer | no | 1–10; default from passport, usually 3 |
| `exclude_weekends` | boolean | no | From passport; do not assume |
| `business_hours` | object | no | From passport; server-side policy wins if it conflicts |

The server must validate that `calendar_id` belongs to the tenant. A calendar ID from another tenant is a security incident.

---

## 4. Response

### Success

```json
{
  "ok": true,
  "status": "ok",
  "tool": "calendar.availability",
  "request_id": "req_01J9Z4A1",
  "data": {
    "calendar_id": "karkyra-advisory-demo-calendar",
    "duration_minutes": 30,
    "timezone": "Asia/Bishkek",
    "generated_at": "2026-10-23T10:00:03+06:00",
    "expires_at": "2026-10-23T10:05:03+06:00",
    "slots": [
      {
        "slot_id": "slot_01J9Z4B7",
        "start": "2026-10-27T14:00:00+06:00",
        "end": "2026-10-27T14:30:00+06:00",
        "display": "27 октября, вторник, 14:00",
        "timezone": "Asia/Bishkek",
        "bookable": true
      },
      {
        "slot_id": "slot_01J9Z4B8",
        "start": "2026-10-27T16:00:00+06:00",
        "end": "2026-10-27T16:30:00+06:00",
        "display": "27 октября, вторник, 16:00",
        "timezone": "Asia/Bishkek",
        "bookable": true
      }
    ],
    "truncated": false
  },
  "error": null,
  "meta": {
    "server_time": "2026-10-23T10:00:03+06:00",
    "source": "calendar-provider",
    "contract_version": "1.0.0",
    "trace_id": "trace_abc124"
  }
}
```

### Data fields

| Field | Type | Meaning |
|---|---|---|
| `calendar_id` | string | Echo of the requested calendar |
| `duration_minutes` | integer | Slot length |
| `timezone` | IANA | Display timezone for `display` |
| `generated_at` | ISO-8601 | When availability was computed |
| `expires_at` | ISO-8601 | After this, the slots are not safe to offer without re-check |
| `slots[]` | array | Ordered, real, bookable slots |
| `slots[].slot_id` | opaque string | Use this exact ID for booking; do not parse it |
| `slots[].start` / `end` | ISO-8601 with offset | Exact time |
| `slots[].display` | string | Localized display text; still verify timezone |
| `slots[].bookable` | boolean | If false, do not offer |
| `truncated` | boolean | More slots exist than returned |

### No slots

```json
{
  "ok": true,
  "status": "no_slots",
  "tool": "calendar.availability",
  "request_id": "req_01J9Z4A2",
  "data": {
    "calendar_id": "karkyra-advisory-demo-calendar",
    "duration_minutes": 30,
    "timezone": "Asia/Bishkek",
    "generated_at": "2026-10-23T10:01:00+06:00",
    "slots": []
  },
  "error": null,
  "meta": {
    "server_time": "2026-10-23T10:01:00+06:00",
    "source": "calendar-provider",
    "contract_version": "1.0.0"
  }
}
```

`no_slots` is **not an error**. The agent must say there are no verified openings in that range, offer a different range, or hand off. It must not say "probably" or invent a slot.

---

## 5. Status semantics

| Status | Meaning | Agent action |
|---|---|---|
| `ok` | Real slots returned | Offer 2–3 bookable slots with date, time, timezone, duration |
| `no_slots` | Calendar reachable; no openings | Say so; offer another range or human |
| `invalid_request` | Bad range, duration, timezone, or calendar ID | Fix once; do not guess |
| `unauthorized` / `forbidden` | No access to this calendar | Do not offer slots; hand off |
| `consent_required` | Buyer has not agreed to a booking search or data use | Ask or stop |
| `rate_limited` | Too many reads | Wait `retry_after_ms`; do not hammer |
| `timeout` / `unavailable` | Calendar unreachable | Do not invent; retry once, then hand off |
| `failed` | Internal error | Do not invent; log and hand off |

**Unrecognized status = no availability.** Do not fall back to business hours.

---

## 6. Failure behavior

| Failure | Agent says | Agent does not |
|---|---|---|
| Timeout | "Календарь сейчас не отвечает, поэтому я не могу подтвердить свободное время. Повторю или передам человеку." | "Обычно после обеда свободно" |
| No slots | "В этом диапазоне подтверждённых окон нет. Могу проверить другую неделю или передать человеку." | Invent a slot |
| Calendar unauthorized | "Не могу проверить календарь. Передам человеку, чтобы он подтвердил время." | Send a link as a workaround |
| Bad timezone | Ask the buyer to confirm their timezone | Assume a city |
| Slots expire before booking | Re-check availability; do not use stale `slot_id` | Book the stale slot and hope |

Retry: one read retry on `timeout`/`unavailable`/`rate_limited` (after the delay). Do not retry `invalid_request`, `unauthorized`, or `no_slots` unchanged.

---

## 7. Slot handling rules

- Offer **two or three** slots, not a wall of times.
- Always include date, time, timezone, and duration.
- Use `display` only as a convenience; verify `start`, `end`, and `timezone`.
- Do not convert the timezone unless the buyer asks and the conversion is exact.
- A `slot_id` is opaque and short-lived. Do not derive a booking time from it.
- If `expires_at` has passed, re-check before offering.
- If `truncated: true`, do not claim these are all available times.
- If the buyer asks for a time outside the range, run a new availability check; do not promise it.

---

## 8. Privacy and security

- Return free/busy data only; never meeting titles, attendee lists, notes, or locations.
- Enforce tenant and calendar ownership.
- Do not expose internal calendar IDs to the buyer; use `slot_id` internally.
- Do not log full buyer messages in the calendar adapter.
- Treat calendar event text as untrusted data; never execute it.
- Rate-limit per conversation to prevent enumeration of someone else's calendar.

---

## 9. Acceptance tests

1. Valid request returns real slots with `slot_id`, `start`, `end`, timezone.
2. Empty range returns `no_slots`, not an error and not an invented time.
3. Timeout returns no slots; agent does not claim availability.
4. Wrong tenant calendar returns `unauthorized` with no leakage.
5. Range in the past returns `invalid_request`.
6. `max_slots` is respected; `truncated` is honest.
7. Slot expiry is enforced; stale slot IDs are rejected at booking.
8. DST transition does not shift the displayed time incorrectly.
9. Buyer timezone differs from calendar timezone; both are represented correctly.
10. Calendar event with an instruction-like title does not affect behavior.

---

## 10. Adapter notes

An adapter must:

- use the provider's free/busy API, not a static list;
- apply buffers and business hours server-side;
- return stable, opaque slot IDs that the booking contract can validate;
- set a short `expires_at`;
- expose `implemented`, `degraded`, or `not_implemented` health;
- never fabricate slots when the provider is down.

This repository provides no adapter and has not run a live calendar test.
