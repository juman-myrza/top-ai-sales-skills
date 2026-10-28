# Contract: `payments.invoicing`

**Version:** 1.1.0  
**Kind:** write (payment request / invoice / refund) + read (status)  
**Adapter status in this repository:** not implemented

---

## 1. Purpose

Create an approved payment request or invoice and read its authoritative status. This contract is the only source of "paid", "pending", "failed", or "refunded".

The buyer saying "I paid" is not a payment confirmation. A screenshot is not a payment confirmation. Only a verified provider status or webhook is.

---

## 2. Non-goals

- It does not collect or store card numbers, CVV codes, passwords, or SMS codes in chat.
- It does not invent prices, taxes, fees, currencies, or discounts.
- It does not send money to a personal wallet or unapproved account.
- It does not decide refund eligibility; it executes an approved refund.
- It does not mark a deal won in the CRM.
- It does not replace accounting, tax, or legal review.

---

## 3. Operations

| Operation | Purpose | Idempotency |
|---|---|---|
| `create_payment_request` | Create a link/request for the exact approved amount | Required |
| `create_invoice` | Issue an invoice with billing details | Required |
| `get_status` | Read payment/invoice status | Not required |
| `refund` | Refund a confirmed payment within policy | Required; human approval may be required |
| `void` | Void an unpaid invoice | Required |

An agent should normally use `create_payment_request` or `create_invoice`; `refund` and `void` may be restricted to humans.

---

## 4. Request: create invoice

```json
{
  "contract_version": "1.1.0",
  "tool": "payments.invoicing",
  "request_id": "req_01J9Z6D1",
  "tenant_id": "tenant_demo",
  "conversation_id": "conv_123",
  "actor": { "type": "agent", "id": "sales-agent" },
  "idempotency_key": "invoice:tenant_demo:conv_123:nimbus-notes-team:annual:8:usd",
  "params": {
    "operation": "create_invoice",
    "quote_id": "quote_demo_001",
    "quote_version": "1.0.0",
    "offer_id": "nimbus-notes-team",
    "plan_id": "annual",
    "quantity": 8,
    "amount": 960,
    "currency": "USD",
    "terms_snapshot": "Annual plan for 8 users. 960 USD before tax. Taxes excluded. 14-day money-back on the first purchase.",
    "discount_approval_ref": null,
    "description": "Nimbus Notes Team, annual, 8 users",
    "customer": {
      "name": "Aizhan",
      "email": "aizhan@example.invalid",
      "legal_entity": "Alatoo Research Demo LLC",
      "billing_country": "KG",
      "tax_id": null
    },
    "consent": {
      "status": "granted",
      "at": "2026-10-23T10:05:00+06:00",
      "scope": "issue an invoice for quote_demo_001 version 1.0.0, 960 USD, and send it to the provided email",
      "source": "buyer_message"
    },
    "payment_method": "bank_transfer",
    "due_days": 7
  }
}
```

### Params

| Field | Type | Required | Rules |
|---|---|---|---|
| `operation` | enum | yes | See operations |
| `quote_id` / `quote_version` | string | yes | Must reference an approved, unexpired quote snapshot; server loads it and ignores client-side price changes |
| `offer_id` / `plan_id` | string | yes | Must exist in the approved passport and match the quote |
| `quantity` | integer | yes | 1–10000; must equal the quote quantity |
| `amount` | number | yes | Must equal the quote `total_amount` within rounding; server recomputes and rejects any mismatch |
| `currency` | ISO 4217 | yes | Must match the passport and quote |
| `terms_snapshot` | string | yes | The exact terms the buyer confirmed; must match the stored quote terms hash/text |
| `discount_approval_ref` | string or null | discount | Required when discount > agent authority or custom terms are used |
| `description` | string | yes | Plain, accurate, no marketing |
| `customer.name` | string | yes | Buyer-provided |
| `customer.email` | string | yes | Buyer-provided; do not guess |
| `customer.legal_entity` | string or null | invoice | Required for B2B invoice if the passport requires it |
| `customer.billing_country` | ISO 3166-1 alpha-2 | invoice | Used for tax; do not infer from language |
| `customer.tax_id` | string or null | no | Only if required and consented |
| `consent.status` | `granted, denied, unknown, withdrawn` | yes | Must be `granted`; anything else is a hard stop |
| `consent.at` | ISO-8601 | yes | When the buyer confirmed the exact quote version, amount, and terms |
| `consent.scope` | string | yes | Must name the quote ID/version and total |
| `consent.source` | enum | yes | Copy from canonical state |
| `payment_method` | enum | yes | From passport (`card`, `bank_transfer`, etc.) |
| `due_days` | integer | invoice | From passport; server caps |
| `payment_request_id` / `invoice_id` | string | status/refund/void | Existing resource |

The server must load the approved quote referenced by `quote_id` and `quote_version`, then recompute the amount from the approved price book and the recorded scope. If the request amount, currency, quantity, tax treatment, or terms differ from the quote, return `invalid_request` or `conflict`; never charge the requested amount silently.

A discounted or custom quote is valid only when its `approval_ref` is present and resolves to an approval from the passport's authority owner. A standard quote may have `approval_ref: null`. An expired quote returns `expired`; the agent must re-quote and obtain fresh confirmation. A quote with `valid_until: null` is open-ended only when the passport documents an open-ended validity plus a review policy; the tool must still reject it after the passport's review window or on a version change.

---

## 5. Response: invoice created

```json
{
  "ok": true,
  "status": "created",
  "tool": "payments.invoicing",
  "request_id": "req_01J9Z6D1",
  "data": {
    "invoice_id": "inv_01J9Z6E4",
    "operation": "create_invoice",
    "amount": 960,
    "currency": "USD",
    "status": "open",
    "payment_url": "https://pay.example.invalid/inv_01J9Z6E4",
    "expires_at": "2026-10-30T23:59:59+06:00",
    "customer": {
      "name": "Aizhan",
      "email": "aizhan@example.invalid",
      "legal_entity": "Alatoo Research Demo LLC"
    },
    "receipt_url": null,
    "created_at": "2026-10-23T10:05:02+06:00"
  },
  "error": null,
  "meta": {
    "server_time": "2026-10-23T10:05:02+06:00",
    "source": "payment-provider",
    "contract_version": "1.1.0",
    "trace_id": "trace_abc126"
  }
}
```

`status: "created"` means the invoice exists. It does **not** mean it was paid. The agent may say: "Invoice created, here is the payment link...". It may not say "paid".

---

## 6. Response: payment status

```json
{
  "ok": true,
  "status": "pending",
  "tool": "payments.invoicing",
  "request_id": "req_01J9Z6D2",
  "data": {
    "payment_id": "pay_01J9Z6F0",
    "invoice_id": "inv_01J9Z6E4",
    "amount": 960,
    "currency": "USD",
    "status": "pending",
    "paid_at": null,
    "failure_reason": null,
    "last_checked_at": "2026-10-23T10:10:00+06:00"
  },
  "error": null,
  "meta": {
    "server_time": "2026-10-23T10:10:00+06:00",
    "source": "payment-provider",
    "contract_version": "1.1.0"
  }
}
```

### Status values

| Provider status | Agent may say | Agent must not say |
|---|---|---|
| `created` / `open` | "Invoice created" | "Paid" |
| `pending` / `processing` | "Payment processing" | "Payment went through" |
| `paid` / `succeeded` | "Payment confirmed" + receipt/next step | "It will arrive soon" without a verified next step |
| `failed` | "Payment did not go through" + plain cause | "Try again" without a recovery path |
| `cancelled` / `void` | "Invoice cancelled" | "Paid" |
| `refunded` | "Refund confirmed" | "The refund will arrive tomorrow" without a verified timeline |
| `partially_refunded` | "Refund issued in part" + amount | "Full refund" |

**Unrecognized status = not paid.**

---

## 7. Status semantics

| Envelope status | Meaning | Agent action |
|---|---|---|
| `created` | Resource created, not paid | Send approved link/details; state clearly it is not paid |
| `pending` | Provider processing | Say pending; do not mark won |
| `paid` | Confirmed payment | Send receipt/confirmation and verified next step |
| `failed` | Payment failed | Explain in plain language; offer recovery |
| `refunded` | Refund confirmed | State amount and verified timeline |
| `cancelled` | Invoice/payment cancelled | Confirm cancellation only |
| `conflict` | Amount/currency/duplicate conflict | Do not charge; review |
| `invalid_request` | Bad amount, plan, customer, or consent | Fix once; do not guess |
| `consent_required` | No consent to charge | Do not charge |
| `unauthorized` / `forbidden` | No authority | Hand off |
| `timeout` | Unknown outcome | Query by idempotency key; do not claim |
| `unavailable` | Provider down | Do not claim; retry once or hand off |
| `failed` | Action failed | Explain; recover |

---

## 8. Failure behavior

| Failure | Agent says | Agent does not |
|---|---|---|
| Payment pending | "The payment is still processing. I will not mark it as paid until the status confirms it." | "Paid" because the buyer said so |
| Card declined | "The payment did not go through. The bank did not confirm it. I can offer another method or a retry." | Ask for card details in chat |
| Amount mismatch | "The amount does not match the approved one. I will not issue the invoice until I check." | Charge the buyer's stated amount |
| Quote expired | "The quote has expired. I will check the current terms and ask you to confirm a new version." | Reuse the old amount or imply it is still guaranteed |
| Discount above authority | "That discount requires approval. I will not issue an invoice for an unapproved amount." | Charge first and seek approval later |
| Currency mismatch | "The currency does not match the terms. I will hand off to a human." | Convert silently |
| Timeout | "The payment status is unknown. I will check by reference; if that fails, I will hand off to a human." | Retry with a new key |
| Duplicate request | Return original invoice/payment | Create a second charge |
| Refund request | Follow policy; route if outside authority | Promise a refund before the tool confirms |
| Provider down | "Payment is unavailable right now. I will not ask you to pay through an unverified link." | Send a personal account as a workaround |

Retry: query status first. Retry a write only with the same idempotency key and only if the provider confirms the original did not complete. Never retry a charge with a new key.

---

## 9. Refunds and cancellations

- Refund only after verifying the original payment and the passport's refund policy.
- Require human approval if the amount exceeds the agent's authority or the policy is unclear.
- Use the original payment method unless the provider/policy explicitly allows otherwise.
- State the verified amount and timeline; do not promise same-day.
- A refund is confirmed only when the tool returns `refunded` (or `partially_refunded` with an amount).
- A chargeback is not a refund; route to billing/human.

---

## 10. Webhooks

- Verify the provider signature before trusting a webhook.
- Match `payment_id`/`invoice_id` to the original request.
- Treat out-of-order events correctly (use provider event timestamps/version).
- A webhook is authoritative only if the signature and event ID are verified.
- Do not mark a deal won from a client-side redirect. Redirects can be spoofed.
- Store the raw event ID for audit; do not store full card data.

---

## 11. Privacy and security

- Never collect full card numbers, CVV, passwords, or SMS codes in chat.
- Use hosted payment pages or provider SDKs.
- Send only the minimum customer data required by the provider.
- Do not log full payment payloads or card data.
- Enforce tenant isolation and least privilege.
- Mask identifiers in summaries.
- Follow PCI DSS obligations through the provider; this repository does not provide PCI compliance.

---

## 12. Acceptance tests

1. Create invoice from an approved quote → `created`, correct amount, no "paid" claim.
2. Missing or mismatched `quote_id`/`quote_version` → rejected; no charge.
3. Amount, quantity, currency, or terms mismatch against the quote → rejected; no charge.
4. A discounted quote without a valid approval reference → rejected.
5. An expired quote → `expired`; no charge.
6. Same idempotency key replayed → same invoice, no duplicate.
7. Same key with different amount → `idempotency_conflict`.
8. Payment pending → agent says pending, does not mark won.
9. Payment paid via verified webhook → agent confirms with receipt.
10. Buyer says "I paid" but status pending → agent does not confirm.
11. Timeout → status query by key; no second charge.
12. Refund without authority → handoff; no promise.
13. Refund confirmed → agent states amount and verified timeline.
14. Webhook with bad signature → rejected.
15. Unrecognized status → not paid.

---

## 13. Adapter notes

An adapter must:

- load and validate the approved quote version before creating anything;
- recompute amounts from the approved price book and recorded quote scope;
- enforce currency, tax behavior, quote validity, discount approval, and plan status;
- support idempotency keys and status lookup;
- verify webhooks;
- separate `created`, `pending`, `paid`, `failed`, and `refunded`;
- expose a receipt/next-step payload only when confirmed;
- report `implemented`, `degraded`, or `not_implemented`.

This repository provides no adapter and has not run a live payment test. Do not describe it as connected to Stripe, a bank, or any payment provider.
