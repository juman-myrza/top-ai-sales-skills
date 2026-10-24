# Example Passport: Consumer Direct Purchase

**Passport ID:** `consumer-course-example`  
**Status:** approved (fictional)  
**Companion JSON:** [`consumer-course-example.json`](consumer-course-example.json)

This third fictional example is deliberately **B2C**. It exists to prove that the
universal skills can serve a consumer offer without importing a B2B assumption.

> **Fictional.** Every fact here is invented. The business, prices, refund rules,
> and proof points are not real and are not connected to any live offer. Do not
> treat them as legal, tax, or pricing guidance.

---

## Why this example exists

The first two examples are business offers. A universal skill library must not
require an ICP, a committee, or a meeting. This passport exercises:

- `offer.buyer_types = ["b2c"]` — the consumer is the buyer, not a disqualifier;
- `fulfillment.mode = direct_purchase` with `booking.required = false` — no
  meeting is needed to buy;
- a single one-time price in KGS with taxes included;
- a published discount with a verification condition;
- `sales_guidance` for a consumer segment and an adoption objection;
- the same consent, quote, handoff, and follow-up contracts as the B2B examples.

## What the agent may say

- The one-time price, in KGS, taxes included.
- What the course includes and excludes, including the absence of live tutoring.
- The seven-day refund condition, exactly as written.
- The published discount, only when the buyer qualifies and verification is
  available.

## What the agent must not say

- That live tutoring is included when it is not.
- A fluency level, certificate, or completion guarantee.
- A discount above the published limit or a custom refund.
- Any scarcity or deadline that is not in this passport.

## Consumer-specific review notes

- Consumer law often adds cooling-off and refund rights that a business offer
  does not have. The `unresolved` field records that this needs jurisdiction
  review; the fictional terms are not a legal opinion.
- The segment here is an adult learner. An offer marketed to minors needs a
  separate passport with an explicit minors policy and guardian consent path.
