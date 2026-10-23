# Product Passport Template

**Passport ID:** `[a-z0-9-]{3,64}`  
**Version:** `[major.minor.patch]`  
**Status:** `draft | approved | expired | revoked`  
**Owner:** `[role or team]`  
**Approved by:** `[name, role]`  
**Effective:** `[YYYY-MM-DD]` to `[YYYY-MM-DD or null]`  
**Last verified:** `[YYYY-MM-DD]`

> A passport is data, not instructions. Text inside it cannot override the Core Behavior Contract, safety rules, or tool verification. The loader must treat it as untrusted business content.

This template mirrors [`passport.schema.json`](passport.schema.json). The JSON file is the machine-readable source of truth; this Markdown file is for review and completion. Fill one passport per offer, not one per company. If you sell three distinct offers with different prices and fulfillment, create three passports that share a business block.

---

## 1. How to fill this

### 1.1 Fact status labels

Every material fact uses one of three labels:

| Status | Meaning | Required metadata |
|---|---|---|
| `verified` | Approved by the business, current, and traceable to a source | `source`, `verified_at` |
| `estimated` | Calculated or forecast from verified inputs, with assumptions | `source`, `notes` (the assumption) |
| `unknown` | Not approved, missing, stale, or conflicting | None; the agent must not improvise |

If you do not know a value, write `unknown`. An empty field is not permission to invent. A price marked `unknown` means the agent cannot quote; it can explain what is missing and route to a human.

### 1.2 Rules

1. **No marketing language in factual fields.** "Best-in-class" is not a fact. "Reduces manual entry by 4 hours per week for a 5-person team, measured in a 2025 pilot" is a fact with a source.
2. **No unapproved proof.** A case study needs written permission and a source. If permission is `nda`, the agent may describe only the approved anonymized version.
3. **No discounts outside the policy.** The maximum and approval threshold are facts.
4. **No invented scarcity.** Leave `verified_scarcity` empty unless the constraint is documented and current.
5. **No calendar fiction.** The passport names the calendar; the calendar tool returns the slots. The passport does not contain slot times.
6. **No payment fiction.** The passport names the payment method and invoicing policy; the payment tool returns the status.
7. **No legal advice.** Regulated wording comes from the approved source, not the template author.
8. **Re-verify before launch.** Prices, policies, and proofs expire. Set a review cycle.

### 1.3 Approval gate

A passport may move from `draft` to `approved` only when:

- [ ] The owner has confirmed every `verified` fact against a source.
- [ ] Pricing, tax behavior, fees, refunds, and cancellation terms are approved by finance/legal.
- [ ] Discount authority and approval matrix are signed off.
- [ ] All proof items have permission and a source.
- [ ] All handoff routes have a real destination and fallback.
- [ ] Follow-up cadence, quiet hours, and opt-out keywords are approved.
- [ ] Privacy retention and deletion process are approved.
- [ ] Safety and minors policies are approved.
- [ ] Every tool binding honestly says `implemented`, `degraded`, or `not_implemented`.
- [ ] The JSON validates against the schema.
- [ ] A native speaker has reviewed Kyrgyz content, if Kyrgyz is enabled.

---

## 2. Business

| Field | Value | Status | Source | Verified at |
|---|---|---|---|---|
| Legal name | `[legal entity]` | `unknown` | | |
| Display name | `[brand]` | — | | |
| Description (one sentence) | `[what the business sells, to whom]` | `unknown` | | |
| Website | `[https://…]` | `unknown` | | |
| Markets | `[countries/regions]` | `unknown` | | |
| Timezone | `[IANA, e.g. Asia/Bishkek]` | `unknown` | | |
| Support contact | `[approved channel/hours]` | `unknown` | | |
| Languages | `[ru, ky, en]` | — | | |

Do not put a personal phone number or email in a public repository. Use a role-based contact or a reference to a secret manager.

---

## 3. Offer

| Field | Value |
|---|---|
| Offer ID | `[offer-id]` |
| Name | `[offer name]` |
| Type | `product / service / subscription / program / consultation / other` |
| Buyer types | `[b2b, b2c]` — who may buy; drives whether a consumer is a fit |
| One-liner | `[verified description]` |
| Outcomes | `[what the buyer can expect, without guarantees]` |
| Includes | `[scope, deliverables, support]` |
| Excludes | `[what is explicitly not included]` |
| Prerequisites | `[what the buyer must provide or have]` |
| Support | `[channel, hours, scope]` |
| Status | `active / paused / retired` |

Outcomes must be observable and authorized. "You will double revenue" is a prohibited guarantee. "A weekly report showing [metric]" is a deliverable.

---

## 4. Pricing

### 4.1 Currency and tax

| Field | Value | Status | Source |
|---|---|---|---|
| Currency | `[ISO 4217]` | `unknown` | |
| Tax behavior | `included / excluded / varies / unknown` | — | |
| Invoice policy | `[when an invoice is issued, required billing data, payment terms]` | `unknown` | |

### 4.2 Plans

| Plan ID | Name | Billing period | Price | Setup fee | Minimum term | Cancellation | Refund | Status |
|---|---|---|---|---|---|---|---|---|
| `[plan-id]` | `[name]` | `one_time/monthly/quarterly/annual/custom` | `[amount + currency]` | `[amount or none]` | `[term]` | `[policy]` | `[policy]` | `active` |

Each cell needs a fact status and source in the JSON. Do not put a range in a price field unless the passport explicitly supports "from" pricing; use a separate plan or a `notes` field.

### 4.3 Payment methods

- `[card via approved provider]`
- `[bank transfer with invoice]`
- `[cash on delivery, if applicable]`

Never include a personal wallet or raw card number.

### 4.4 Discount policy

| Field | Value | Status |
|---|---|---|
| Discounts allowed | `true / false` | — |
| Maximum percent | `[number]` | `unknown` |
| Approval threshold | `[percent above which a human must approve]` | `unknown` |
| Stacking | `[allowed / not allowed / conditions]` | `unknown` |
| Conditions | `[annual prepay, volume, case study, etc.]` | `unknown` |

If `allowed` is false, the agent must not offer a discount even to save the deal. If the buyer asks for more than the maximum, hand off.

### 4.5 Quote policy

| Field | Value |
|---|---|
| Quote required for discount | `true / false` |
| Quote required for custom terms | `true / false` |
| Validity days | `[number]` |
| Terms snapshot required | `true / false` |
| Approved quote required for payment | `true / false` |

Any amount, quantity, discount, or term change creates a new quote version. Payment execution must reference an approved, unexpired quote. A discounted quote needs an `approval_ref` from the authority owner.

---

## 5. Qualification

| Field | Value |
|---|---|
| Fit criteria | `[observable criteria: segment, size, need, readiness]` |
| Disqualifiers | `[clear reasons the offer will not help]` |
| Required fields | `[budget range, timeline, decision role, use case]` |
| Decision roles | `[who can decide, who influences, who pays]` |
| Service area | `[countries, regions, languages, delivery constraints]` |

A disqualifier must be based on a real constraint, not a stereotype. "No need for the product" is a disqualifier; "small company" is only a disqualifier if the passport documents why.

---

## 6. Discovery

| Field | Value |
|---|---|
| Required fields | `[what must be known before a recommendation]` |
| Optional fields | `[useful but not blocking]` |
| Recommendation rules | `[if buyer has X and Y, recommend plan Z; if Z is unknown, do not recommend]` |

Recommendation rules are deterministic where possible. "If team size > 20 and needs SSO, recommend Business" is testable. "If the buyer seems serious" is not.

---

## 7. Proof

### 7.1 Cases

| ID | Title | Client name | Outcome | Permission | Source |
|---|---|---|---|---|---|
| `[case-1]` | `[short title]` | `[name / anonymized]` | `[documented result]` | `public / anonymized / nda` | `[URL or document]` |

For each case, also record the evidence-quality fields the schema supports: `segment`, `baseline`, `intervention`, `measurement_period`, and `limitations`. A case without a stated limitation invites the agent to imply more than the data shows.

### 7.2 Testimonials

| ID | Quote | Attribution | Permission | Source |
|---|---|---|---|---|
| `[t-1]` | `[exact quote]` | `[name, role, company]` | `public / anonymized / nda` | `[URL]` |

### 7.3 Certifications, stats, and prohibited claims

- Certifications: `[name, issuer, date, verification URL]`
- Stats: `[number, sample, period, method, source]`
- Prohibited claims: `[claims the business must never make: guarantees, medical, legal, "zero risk", etc.]`

If permission is `unknown`, do not use the proof. If a case is `nda`, do not name the client.

---

## 8. Fulfillment

| Field | Value |
|---|---|
| Mode | `direct_purchase / appointment / quote / hybrid / human_only` |
| Delivery | `[what happens after payment or agreement]` |

Choose the mode honestly:

- `direct_purchase` — the buyer can pay and receive the offer without a meeting.
- `appointment` — a meeting, consultation, or visit is required before or instead of payment.
- `quote` — a proposal must be prepared and approved.
- `hybrid` — a defined sequence, e.g. book a call, then pay.
- `human_only` — no automated execution.

Do not force every buyer into a meeting. If direct purchase is available, let the buyer buy.

### 8.1 Booking (required when mode uses a calendar)

| Field | Value | Status |
|---|---|---|
| Booking required | `true / false` | — |
| Calendar ID | `[adapter-specific ID]` | `unknown` |
| Duration | `[minutes]` | `unknown` |
| Timezone | `[IANA]` | `unknown` |
| Slot interval | `[minutes]` | `unknown` |
| Buffer before | `[minutes]` | `unknown` |
| Buffer after | `[minutes]` | `unknown` |
| Availability window | `[days ahead]` | `unknown` |
| Slots to offer | `[2–3]` | `unknown` |
| Reschedule policy | `[text]` | `unknown` |
| Cancellation policy | `[text]` | `unknown` |
| No-show policy | `[text]` | `unknown` |
| Reminder policy | `[text]` | `unknown` |
| External link allowed | `false` by default | — |
| External link | `[only if explicitly approved]` | `unknown` |

The passport never contains specific available times. The calendar tool does. If the tool is down, the agent must not invent slots.

### 8.2 Proposal (required when mode is `quote` or `hybrid`)

| Field | Value |
|---|---|
| Proposal required | `true / false` |
| Template ID | `[approved template]` |
| Validity | `[days]` |
| Approval required | `true / false` |
| Approval role | `[role]` |

---

## 9. Sales policy

### 9.1 Authority limits

| Field | Value |
|---|---|
| Max discount without approval | `[percent]` |
| Can customize contract | `true / false` |
| Can change refund terms | `true / false` |
| Can waive fees | `true / false` |

### 9.2 Approval matrix

| Condition | Approver | Channel |
|---|---|---|
| `[discount > X%]` | `[role]` | `[tool/channel]` |
| `[custom contract]` | `[legal]` | `[tool/channel]` |
| `[enterprise deal]` | `[sales lead]` | `[tool/channel]` |

### 9.3 Persuasion boundaries

| Field | Value |
|---|---|
| Verified scarcity | `[only documented constraints, or empty]` |
| Competitor policy | `[verified facts only; no disparagement]` |
| Custom terms | `[what the agent may discuss, what requires a human]` |
| Contract policy | `[standard contract; no drafting by the agent]` |
| Call recording policy | `[consent required / not applicable]` |

### 9.4 Negotiation limits

| Field | Value |
|---|---|
| Tradables | `[term length, quantity, payment schedule, start date, reference, etc.]` |
| Non-negotiables | `[what must not be traded, ever]` |
| Walk-away | `[the point at which the agent declines or escalates]` |

If there is no verified scarcity, the agent must not use countdowns, "only N spots", or "price increases tomorrow". A correction of the business's own error is not a concession to trade.

---

## 9a. Sales guidance

Business-specific relevance data that keeps the universal skills from inventing a segment.

| Segment ID | Name | Buyer types | Fit signals | Typical pains | Buying triggers | Default motion |
|---|---|---|---|---|---|---|
| `[segment-id]` | `[name]` | `b2b / b2c` | `[observable signals]` | `[documented pains]` | `[real triggers]` | `direct_purchase / appointment / quote / hybrid / human_only` |

Objection guidance: for each common objection, record the factual response, the evidence IDs it may cite, and what to avoid. Alternative/competitive positioning: record verified advantages and honest trade-offs with a source and a last-checked date.

Do not use this section to script manipulation. It exists so the agent answers from business facts rather than generic rebuttals.

---

## 10. Handoff

| Reason code | Destination | Channel | Hours | Response time | Fallback |
|---|---|---|---|---|---|
| `human_request` | `[role/queue]` | `[tool]` | `[hours]` | `[verified SLA or unknown]` | `[what to tell the buyer]` |
| `authority` | `[role]` | `[tool]` | `[hours]` | `[SLA]` | `[fallback]` |
| `capability` | `[role]` | `[tool]` | `[hours]` | `[SLA]` | `[fallback]` |
| `safety` | `[role/emergency]` | `[tool]` | `[24/7?]` | `[SLA]` | `[emergency resources]` |
| `legal` | `[legal]` | `[tool]` | `[hours]` | `[SLA]` | `[fallback]` |
| `fraud` | `[billing/security]` | `[tool]` | `[hours]` | `[SLA]` | `[fallback]` |
| `privacy` | `[privacy owner]` | `[tool]` | `[hours]` | `[SLA]` | `[fallback]` |

Required handoff fields: `[list]`. Automation pause: `true`. Human takeover policy: `[text]`.

Every route needs a fallback for tool failure. "The human will contact you" is not a fallback unless the handoff was actually created.

---

## 11. Follow-up

| Field | Value |
|---|---|
| Allowed | `true / false` |
| Basis | `buyer_requested / agreed_next_step / existing_customer / marketing_consent` |
| Channels | `[ordered list]` |
| Quiet hours | `[start–end, timezone]` |
| Allowed days | `[mon–sun]` |
| Max attempts per reason | `[integer]` |
| Max attempts per conversation | `[integer]` |
| Min interval | `[hours]` |
| Close-out after | `[days]` |
| Opt-out keywords | `[stop, отмена, не пишите, керек эмес, …]` |
| Marketing consent required | `true` |

If cadence is unknown, the agent may send only buyer-requested follow-ups. It must not invent a sequence.

---

## 12. Privacy

| Field | Value |
|---|---|
| Data collected | `[name, contact, company, billing data, …]` |
| Purposes | `[respond, quote, fulfill, support, marketing]` |
| Retention | `[duration + trigger]` |
| Deletion process | `[how a request is routed and confirmed]` |
| Sharing | `[processors, regions, safeguards]` |
| PII rules | `[what must never be collected in chat]` |
| Legal basis | `[consent, contract, legitimate interest, other]` |

Do not claim deletion, access, or correction until the tool confirms it.

---

## 13. Safety

| Field | Value |
|---|---|
| Emergency protocol | `[what to do, who to contact, what not to say]` |
| Emergency resources | `[verified local numbers/links only]` |
| Minors policy | `[stop, guardian process, no payment]` |
| Vulnerability policy | `[pause, no pressure, human route]` |

If safety policy is missing, the agent must stop selling when a safety issue appears and hand off. It must not invent hotline numbers or provide counseling.

---

## 14. Tools

| Contract | Adapter ID | Status | Contract version | Notes |
|---|---|---|---|---|
| `passport_lookup` | `[adapter]` | `implemented / degraded / not_implemented` | `1.0.0` | |
| `calendar_availability` | `[adapter]` | `…` | `1.0.0` | |
| `calendar_booking` | `[adapter]` | `…` | `1.0.0` | |
| `payments_invoicing` | `[adapter]` | `…` | `1.0.0` | |
| `crm_memory` | `[adapter]` | `…` | `1.0.0` | |
| `human_handoff` | `[adapter]` | `…` | `1.0.0` | |
| `messaging_media` | `[adapter]` | `…` | `1.0.0` | |

The repository ships **contracts, not adapters**. Mark `not_implemented` honestly. A skill may describe what it would do; it may not claim a tool exists.

---

## 15. Metadata and unresolved decisions

| Field | Value |
|---|---|
| Owner | `[team]` |
| Created | `[YYYY-MM-DD]` |
| Updated | `[YYYY-MM-DD]` |
| Source of truth | `[CRM/price book/URL]` |
| Review cycle | `[days]` |
| Fictional | `true / false` |

Unresolved decisions:

- `[decision needed] — owner: [role] — deadline: [date]`
- `[decision needed] — owner: [role] — deadline: [date]`

An unresolved item is not a blocker for drafting, but it is a blocker for claiming the field is verified.

---

## 16. Final checks

- [ ] JSON validates against `passport.schema.json`.
- [ ] No secrets, personal data, or real customer data in the file.
- [ ] Every `verified` fact has a source and date.
- [ ] Every `unknown` field has a safe fallback behavior.
- [ ] Prices, currency, tax, fees, refunds, and cancellation are consistent.
- [ ] Discount authority matches the approval matrix.
- [ ] Booking mode and calendar are consistent.
- [ ] Direct purchase is not blocked by an unnecessary meeting.
- [ ] Handoff routes cover every reason code used by the skills.
- [ ] Follow-up consent and opt-out keywords are present.
- [ ] Privacy and safety policies are approved.
- [ ] Tool bindings are honest.
- [ ] The passport does not contain instructions that could override the core contract.
