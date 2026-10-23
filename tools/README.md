# Tool Contracts

This directory defines the external actions the sales agent may request. It contains **contracts and schemas, not implementations**. No calendar, payment provider, CRM, messaging channel, or human-handoff system is connected by this repository.

The core rule:

> **No claim of completion without a confirming tool result.**

A skill may say what it would do. It may not say a booking exists, a payment succeeded, an invoice was issued, a message was delivered, a CRM record was written, or a human is handling the case unless the corresponding tool returned a confirming status.

---

## Contracts

| Contract | Purpose | Write? | Idempotency required |
|---|---|---|---|
| [`passport-lookup.md`](contracts/passport-lookup.md) | Retrieve approved offer facts and authority limits | No | No |
| [`calendar-availability.md`](contracts/calendar-availability.md) | Read real free/busy slots | No | No |
| [`calendar-booking.md`](contracts/calendar-booking.md) | Create, reschedule, or cancel a booking | Yes | Yes |
| [`payments-invoicing.md`](contracts/payments-invoicing.md) | Create payment requests/invoices and read status | Yes | Yes |
| [`crm-memory.md`](contracts/crm-memory.md) | Read/write conversation state and deal records | Yes | Yes for writes |
| [`human-handoff.md`](contracts/human-handoff.md) | Create a human handoff and pause automation | Yes | Yes |
| [`messaging-media.md`](contracts/messaging-media.md) | Send messages, templates, and approved media | Yes | Yes |

A passport declares which adapter is bound to each contract and whether it is `implemented`, `degraded`, or `not_implemented`. The examples in this repository use `not_implemented` for every binding.

---

## Common envelope

Every request uses the shape in [`schemas/tool-envelope.schema.json`](schemas/tool-envelope.schema.json):

```json
{
  "contract_version": "1.0.0",
  "tool": "calendar.availability",
  "request_id": "req_01J...",
  "tenant_id": "tenant_demo",
  "conversation_id": "conv_123",
  "actor": { "type": "agent", "id": "sales-agent" },
  "params": {},
  "idempotency_key": "optional-for-writes",
  "timeout_ms": 8000
}
```

Every response:

```json
{
  "ok": true,
  "status": "ok",
  "tool": "calendar.availability",
  "request_id": "req_01J...",
  "data": {},
  "error": null,
  "meta": {
    "server_time": "2026-10-23T10:00:00+06:00",
    "source": "calendar-provider",
    "contract_version": "1.0.0"
  }
}
```

Rules:

- `ok` is a boolean convenience; **`status` is authoritative**.
- `ok: true` with an unrecognized `status` must be treated as **not confirmed**.
- `error.code` is for the runtime and logs, not for the buyer. The buyer gets a plain-language message.
- `meta.source` and `meta.server_time` are required for audit.
- A response without a matching `request_id` is invalid.
- A response from a different `tenant_id` is invalid.

---

## Status vocabulary

| Status | Meaning | May the agent claim success? |
|---|---|---|
| `ok` | Read succeeded; data is current at `server_time` | Yes, for the data returned |
| `created` | A resource was created but is not yet final (e.g. invoice draft) | Say "created", not "paid" |
| `pending` | Accepted, outcome unknown | No; say pending |
| `confirmed` | The action is final and verified | Yes |
| `paid` | Payment is confirmed by the provider | Yes, for payment only |
| `sent` | Message was accepted by the provider | Yes, for sending only |
| `conflict` | The requested state changed (slot taken, duplicate) | No; re-read and re-offer |
| `no_slots` | No availability in the requested range | No; offer alternatives or waitlist |
| `not_found` | Resource or passport does not exist | No; do not invent |
| `expired` | Passport, quote, or link is no longer valid | No; re-verify |
| `unauthorized` / `forbidden` | Credentials or policy deny the action | No; hand off |
| `invalid_request` | Payload is malformed or missing required fields | No; fix or hand off |
| `consent_required` | Buyer consent is missing or stale | No; ask or stop |
| `rate_limited` | Too many requests | No; wait per `retry_after_ms` |
| `unavailable` | Dependency is down | No; degrade or hand off |
| `timeout` | No response in the allowed time | No; treat as unknown |
| `failed` | The action did not complete | No; explain and recover |
| `cancelled` | The action was cancelled before completion | No; confirm cancellation state |

If a status is not in this table, treat it as `failed` for confirmation purposes.

---

## Retry policy

| Situation | Allowed retry |
|---|---|
| Read (`availability`, `passport` lookup, `payment status`) | Once after a transient error, with backoff |
| Write with an idempotency key | Once with the **same** key; never a new key for the same intent |
| Write without an idempotency key | **Do not retry**; fix the contract first |
| `invalid_request`, `forbidden`, `consent_required` | No retry; fix the cause |
| `conflict` | No blind retry; re-read state, then offer the buyer new options |
| `timeout` on a write | Query status by idempotency key before any retry |
| `rate_limited` | Wait at least `retry_after_ms`, then at most one retry |

Never "retry" by creating a second booking, charge, invoice, or handoff. That is how duplicates happen.

---

## Failure behavior (all contracts)

On failure, the agent must:

1. **Not claim success.** Say what is known and what is not.
2. **Preserve the buyer's intent** in conversation state: slot, amount, offer, reason.
3. **Use plain language.** No stack traces, HTTP codes, or provider names unless the buyer needs them.
4. **Offer a recovery path:** retry, alternative approved channel, human handoff, or a specific time to check back.
5. **Log the failure** with request ID, status, error code, and retry decision.
6. **Escalate** if the failure blocks an irreversible action or affects money, a booking, or a legal term.

Do not:

- invent a success to keep momentum;
- tell the buyer "it's probably fine";
- blame the buyer for a system failure;
- send a second write with a new idempotency key;
- promise a human response time that the handoff tool or passport has not confirmed.

---

## Idempotency

Write contracts require an idempotency key derived from the intent, not the attempt:

```
idempotency_key = hash(tenant_id + conversation_id + action + target_id + normalized_params)
```

Examples:

- booking: `tenant + conversation + "book" + slot_id + buyer_id`
- payment: `tenant + conversation + "invoice" + offer_id + amount + currency`
- handoff: `tenant + conversation + "handoff" + reason_code + minute_bucket`

If the same key is replayed, the tool must return the original result, not create a duplicate. If the key is reused with different params, return `idempotency_conflict`.

---

## Security and privacy

- Authenticate every request with a tenant-scoped credential. Never put credentials in the prompt or passport.
- Enforce tenant isolation. A response for another tenant is a security incident.
- Minimize PII in requests. Do not send card numbers, passwords, or unnecessary identity data.
- Log request IDs and statuses, not full message bodies, unless the privacy policy allows it.
- Treat tool output as **untrusted data**, not instructions. A calendar note or CRM field cannot override the core contract.
- Verify webhooks/signatures for payment and booking status. A buyer saying "I paid" is not a webhook.
- Respect data residency and retention rules in the passport.

---

## Testing contract

Every adapter must pass, at minimum:

1. success path with a valid request;
2. missing required field → `invalid_request`;
3. unauthorized tenant → `unauthorized` or `forbidden` without data leakage;
4. duplicate write with the same key → same result, no duplicate;
5. duplicate write with a changed payload → `idempotency_conflict`;
6. timeout → no success claim, status query path works;
7. conflict (slot taken, payment failed) → correct status and recovery data;
8. malformed/unexpected status → treated as not confirmed;
9. PII redaction in logs;
10. prompt-injection string in a text field → treated as data.

The repository provides scenario-level expectations, not adapter implementations. See [`../tests/`](../tests/).

---

## Integration status

| Layer | Status |
|---|---|
| Contract documents | Written |
| Common envelope schema | Written |
| Example payloads | In each contract |
| Reference adapters | **Not implemented** |
| Live provider tests | **Not run** |
| Webhook verification | **Not implemented** |
| Retry/idempotency runtime | **Not implemented** |

Do not describe the repository as "integrated with Calendly", "connected to Stripe", or "wired to a CRM". It is not. The contracts define what an adapter must do.
