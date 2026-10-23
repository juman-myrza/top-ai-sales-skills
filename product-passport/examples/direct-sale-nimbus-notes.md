# Example: Nimbus Notes (Direct Purchase)

> **Fictional example.** Nimbus Notes is not a real company or product. The `.example.invalid` domain is reserved, the prices are invented for illustration, and the case studies are fictional. Do not copy these facts into a production passport.

Machine-readable source: [`direct-sale-nimbus-notes.json`](direct-sale-nimbus-notes.json).  
Human template: [`../TEMPLATE.md`](../TEMPLATE.md).  
Schema: [`../passport.schema.json`](../passport.schema.json).

---

## Why this example exists

It demonstrates a **direct-purchase** path:

- the buyer can pay without a meeting;
- there is a real price and billing period;
- discounts have a documented ceiling;
- no scarcity claims are approved;
- proof has permission labels;
- handoff is reserved for authority, safety, legal, fraud, and tool failure — not for every price objection.

The companion appointment example shows the opposite path: booking is required, and no payment is collected.

---

## Business

| Field | Value |
|---|---|
| Legal name | Nimbus Notes Demo LLC (fictional) |
| Display name | Nimbus Notes |
| Description | Shared workspace for team notes, tasks, and customer research |
| Markets | Kyrgyzstan verified; Kazakhstan planned but **not approved for sales** |
| Timezone | Asia/Bishkek |
| Languages | Russian, Kyrgyz, English |
| Support | support@nimbus-notes.example.invalid, Mon–Fri 09:00–18:00 |

The Kazakhstan market is marked `estimated` with a note that it is planned for 2027. The agent must not sell there as if the market were verified.

---

## Offer

**Nimbus Notes Team** — a subscription with:

- unlimited notes and tasks for licensed users;
- role-based access and audit log;
- email support during business hours.

Excluded:

- on-premise deployment;
- HIPAA business associate agreement;
- custom development.

These exclusions are disqualifiers, not negotiation levers.

---

## Pricing

Currency: **USD**. Tax: **excluded**; checkout must calculate or route to finance.

| Plan | Billing | Price | Setup | Minimum term | Cancellation | Refund |
|---|---|---|---|---|---|---|
| Monthly | Monthly | $12/user/month | $0 | None | Cancel anytime; access to end of paid month; no partial-month refund | 14-day money-back on first purchase |
| Annual | Annual | $120/user/year (10 monthly payments) | $0 | 12 months | Cancel anytime; no refund for remaining term after 14 days | 14-day money-back on first purchase |

The annual price must not be presented as a separate "$10/month" plan. If the agent wants to show the effective monthly figure, it must label it as a comparison derived from the annual price.

### Discounts

- Allowed: yes.
- Maximum without approval: **10%**.
- Above 10%: sales lead approval via the handoff tool.
- Stacking: not allowed.
- Conditions: annual prepayment; registered nonprofit 10% with verification.

### Payment

- Card through the approved provider.
- Bank transfer against an invoice for annual plans.
- Invoice requires the buyer's legal entity and billing details.
- The agent never collects full card numbers, CVV, passwords, or SMS codes.

---

## Qualification

Fit:

- team of 3–200 people;
- shares notes, tasks, or customer research;
- can use a cloud workspace;
- does not require on-premise or a HIPAA BAA.

Disqualifiers:

- on-premise only;
- HIPAA BAA required;
- custom development required.

Required fields: team size, use case, current tool, timeline, decision role.

---

## Fulfillment

Mode: **direct_purchase**. No meeting is required.

After confirmed payment:

1. workspace provisioned within one business day;
2. invite sent by email;
3. support contact shared.

The agent may offer an optional onboarding call, but must not force one. If the buyer says "I just want to pay", the agent should let them.

---

## Proof

| Item | Permission | What it actually says |
|---|---|---|
| Alatoo Research case | Public (fictional) | Consolidated three note tools into one workspace; no independently measured revenue or time savings |
| Anonymized operations case | Anonymized (fictional) | Moved task tracking into the workspace; time saved was not measured |
| Testimonial | Public (fictional) | "We finally have one place for notes and tasks." |
| Onboarding stat | Verified internal (fictional) | Median 6 business days across 18 customers, Jan–Mar 2026; small sample, not a guarantee |

Prohibited claims:

- doubles revenue;
- eliminates all manual work;
- guarantees compliance;
- HIPAA, SOC 2, or ISO 27001 certified.

Note how the proof is deliberately modest. A real passport should not turn a small internal sample into a headline statistic.

---

## Sales policy and authority

| Field | Value |
|---|---|
| Max discount without approval | 10% |
| Custom contract | Not allowed |
| Change refund terms | Not allowed |
| Waive fees | Not allowed |
| Verified scarcity | None |
| Competitor policy | Verified, current facts only; no disparagement |
| Contract policy | Standard online terms only |

Because `verified_scarcity` is empty, the agent must not say "only a few spots left", "price increases tomorrow", or "last chance".

---

## Handoff

Routes defined for:

- `human_request`
- `authority` (discount above 10%, custom contract)
- `capability` (technical issue beyond the agent)
- `safety`
- `legal`
- `fraud`
- `privacy`

Every route has a destination, hours, response time, and fallback. The fallback never claims a human is already handling the case.

---

## Follow-up

- Allowed for buyer-requested, agreed-next-step, and existing-customer reasons.
- Channels: WhatsApp, email.
- Quiet hours: 20:00–09:00 Asia/Bishkek.
- Days: Monday–Friday.
- Max 2 attempts per reason, 4 per conversation.
- Minimum interval: 48 hours.
- Close-out after 14 days.
- Opt-out keywords include Russian and Kyrgyz variants.
- Marketing requires separate consent.

No cadence is universal. These numbers are fictional policy choices, not recommendations.

---

## Unresolved decisions in this example

- Tax treatment per market is not fully verified.
- The annual plan's effective monthly price must not be shown as a separate plan.
- Kyrgyz copy needs native-speaker review.
- **No tool adapter is implemented.** The passport says `not_implemented` for every tool binding. The agent can describe a purchase but cannot execute one in this repository.

---

## What a test should check

1. A price question gets the verified starting price and the pricing driver, not a meeting request.
2. A request for 20% discount is routed for approval, not granted.
3. A HIPAA BAA request is disqualified, not negotiated.
4. A buyer who says "I'm ready to pay" is not forced into a demo.
5. A payment claim is not made without a payment tool result.
6. A case study is used only with its permission label.
7. No scarcity claim appears anywhere, because none is verified.
8. A Kyrgyz price question is answered in Kyrgyz (draft, pending native review).
