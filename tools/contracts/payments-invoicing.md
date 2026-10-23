# Contract: `payments.invoicing`

**Version:** 1.0.0  
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
  "contract_version": "1.0.0",
  "tool": "payments.invoicing",
  "request_id": "req_01J9Z6D1",
  "tenant_id": "tenant_demo",
  "conversation_id": "conv_123",
  "actor": { "type": "agent", "id": "sales-agent" },
  "idempotency_key": "invoice:tenant_demo:conv_123:nimbus-notes-team:annual:8:usd",
  "params": {
    "operation": "create_invoice",
    "offer_id": "nimbus-notes-team",
    "plan_id": "annual",
    "quantity": 8,
    "amount": 960,
    "currency": "USD",
    "description": "Nimbus Notes Team, annual, 8 users",
    "customer": {
      "name": "Айжан",
      "email": "aizhan@example.invalid",
      "legal_entity": "Alatoo Research Demo LLC",
      "billing_country": "KG",
      "tax_id": null
    },
    "consent": {
      "given": true,
      "at": "2026-10-23T10:05:00+06:00",
      "scope": "issue an invoice for 960 USD and send it to the provided email"
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
| `offer_id` / `plan_id` | string | yes | Must exist in the approved passport |
| `quantity` | integer | yes | 1–10000; must be explicit |
| `amount` | number | yes | Must equal `unit_price × quantity` within rounding; server recomputes |
| `currency` | ISO 4217 | yes | Must match the passport |
| `description` | string | yes | Plain, accurate, no marketing |
| `customer.name` | string | yes | Buyer-provided |
| `customer.email` | string | yes | Buyer-provided; do not guess |
| `customer.legal_entity` | string or null | invoice | Required for B2B invoice if the passport requires it |
| `customer.billing_country` | ISO 3166-1 alpha-2 | invoice | Used for tax; do not infer from language |
| `customer.tax_id` | string or null | no | Only if required and consented |
| `consent.given` | boolean | yes | Must be true |
| `consent.at` | ISO-8601 | yes | When the buyer confirmed the amount and terms |
| `payment_method` | enum | yes | From passport (`card`, `bank_transfer`, etc.) |
| `due_days` | integer | invoice | From passport; server caps |
| `payment_request_id` / `invoice_id` | string | status/refund/void | Existing resource |

The server must recompute the amount from the approved price book. If the request amount differs, return `invalid_request` or `conflict`; never charge the requested amount silently.

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
      "name": "Айжан",
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
    "contract_version": "1.0.0",
    "trace_id": "trace_abc126"
  }
}
```

`status: "created"` means the invoice exists. It does **not** mean it was paid. The agent may say: "Счёт создан, ссылка на оплату…". It may not say "оплачено".

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
    "contract_version": "1.0.0"
  }
}
```

### Status values

| Provider status | Agent may say | Agent must not say |
|---|---|---|
| `created` / `open` | "Счёт создан" | "Оплачено" |
| `pending` / `processing` | "Платёж в обработке" | "Оплата прошла" |
| `paid` / `succeeded` | "Оплата подтверждена" + receipt/next step | "Скоро придёт" without a verified next step |
| `failed` | "Платёж не прошёл" + plain cause | "Попробуйте ещё раз" without a recovery path |
| `cancelled` / `void` | "Счёт отменён" | "Оплачен" |
| `refunded` | "Возврат подтверждён" | "Возврат придёт завтра" without a verified timeline |
| `partially_refunded` | "Возврат выполнен частично" + amount | "Полный возврат" |

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
| Payment pending | "Платёж пока в обработке. Я не буду отмечать его как оплаченный, пока статус не подтвердится." | "Оплачено" because the buyer said so |
| Card declined | "Платёж не прошёл. Банк не подтвердил операцию. Могу предложить другой способ или повтор." | Ask for card details in chat |
| Amount mismatch | "Сумма не совпала с утверждённой. Я не буду выставлять счёт, пока не проверю." | Charge the buyer's stated amount |
| Currency mismatch | "Валюта не совпадает с условиями. Передам человеку." | Convert silently |
| Timeout | "Статус платежа неизвестен. Проверю по номеру; если не получится — передам человеку." | Retry with a new key |
| Duplicate request | Return original invoice/payment | Create a second charge |
| Refund request | Follow policy; route if outside authority | Promise a refund before the tool confirms |
| Provider down | "Оплата сейчас недоступна. Не буду просить вас платить по неподтверждённой ссылке." | Send a personal account as a workaround |

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

1. Create invoice → `created`, correct amount, no "paid" claim.
2. Amount mismatch → rejected; no charge.
3. Currency mismatch → rejected.
4. Same idempotency key replayed → same invoice, no duplicate.
5. Same key with different amount → `idempotency_conflict`.
6. Payment pending → agent says pending, does not mark won.
7. Payment paid via verified webhook → agent confirms with receipt.
8. Buyer says "I paid" but status pending → agent does not confirm.
9. Timeout → status query by key; no second charge.
10. Refund without authority → handoff; no promise.
11. Refund confirmed → agent states amount and verified timeline.
12. Webhook with bad signature → rejected.
13. Unrecognized status → not paid.

---

## 13. Adapter notes

An adapter must:

- recompute amounts from the approved price book;
- enforce currency, tax behavior, and plan status;
- support idempotency keys and status lookup;
- verify webhooks;
- separate `created`, `pending`, `paid`, `failed`, and `refunded`;
- expose a receipt/next-step payload only when confirmed;
- report `implemented`, `degraded`, or `not_implemented`.

This repository provides no adapter and has not run a live payment test. Do not describe it as connected to Stripe, a bank, or any payment provider.
