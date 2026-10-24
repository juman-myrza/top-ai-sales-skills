# Conversation State

The agent needs a small, explicit state object to avoid repeating questions, losing promises, and inventing facts. The state is an internal working record, not a CRM and not a transcript dump.

Canonical schema: [`conversation-state.schema.json`](conversation-state.schema.json).  
Valid example: [`example-state.json`](example-state.json).

---

## 1. Principles

1. **Minimal** — store what changes the next decision, not everything the buyer said.
2. **Source-labelled** — every business fact records where it came from and whether it is verified.
3. **Append-safe** — corrections create a new value and mark the old one superseded; they do not silently overwrite history.
4. **Consent-aware** — follow-up, booking, payment, data-sharing, and marketing consent are separate records with scope, time, and source.
5. **Portable** — the state can be summarized for a human handoff without exposing unnecessary sensitive data.
6. **Expirable** — facts such as price, availability, and inventory become stale; store `checked_at` and re-check before use.
7. **Decision-oriented** — state exists to improve the next action. If a field never changes a decision, do not collect it.

---

## 2. Shape

A minimal state has identity, stage, mode, language, fit, consent, and a timestamp. Everything else is added as it becomes relevant.

```json
{
  "schema_version": "1.1.0",
  "conversation_id": "conv_demo_001",
  "tenant_id": "tenant_demo",
  "passport_id": "direct-sale-nimbus-notes",
  "passport_version": "1.1.0",
  "channel": "whatsapp",
  "language": { "primary": "ru", "detected": ["ru"], "register": "neutral" },
  "stage": "discover",
  "mode": "discover",
  "fit": { "status": "unknown", "reasons": [], "disqualifiers": [] },
  "consent": {
    "follow_up": { "status": "unknown", "at": null, "scope": null, "source": "none" },
    "booking": { "status": "unknown", "at": null, "scope": null, "source": "none" },
    "payment": { "status": "unknown", "at": null, "scope": null, "source": "none" },
    "data_sharing": { "status": "unknown", "at": null, "scope": null, "source": "none" },
    "marketing": { "status": "unknown", "at": null, "scope": null, "source": "none" }
  },
  "updated_at": "2026-10-23T10:00:00+06:00"
}
```

The full example in [`example-state.json`](example-state.json) includes needs, diagnosis, quote, follow-up, tool results, and promises.

---

## 3. Field rules

### Identity

- `conversation_id` is stable for the thread. Do not create a new one after a language switch or a topic change.
- `tenant_id` and `passport_id` bind the conversation to one business and one approved passport. Never mix facts from different tenants.
- `passport_version` matters: a price quoted under version 1.0 may be stale after 1.1. Re-check before repeating it.

### Language

- `primary` is the language the agent will use next.
- `detected` records observed languages, not guesses about ethnicity or nationality.
- `register` is `formal`, `neutral`, or `familiar`, based on the buyer's own style. Default to `neutral`.
- A language switch updates `primary` only when the buyer clearly switches or asks to. Do not infer a language preference from a name, company, or location.
- An explicit buyer instruction such as "write in Kyrgyz" or "please use English" wins over the language of the last message.

### Stage

One of: `open`, `qualify`, `discover`, `value`, `resolve`, `commit`, `execute`, `confirm`, `follow_up`, `protect`, `nurture`, `closed_won`, `closed_lost`, `handoff`.

Stage is a control hint, not a claim about the buyer. A buyer can be ready to buy during `discover`; execute then. Do not force the buyer through the named stages.

### Mode

One of: `answer`, `qualify`, `discover`, `prove`, `resolve`, `commit`, `execute`, `confirm`, `follow_up`, `protect`, `handoff`, `closed`.

Mode is what the next turn is trying to do. Stage is deal progress. A price question in `discover` uses `answer`; a booking confirmation in `commit` uses `execute` or `confirm`. Keeping them separate prevents a stage label from forcing an irrelevant sales move.

### Fit

`status`: `unknown`, `qualified`, `nurture`, `not_fit`, `insufficient_info`, `handoff`.

`reasons` and `disqualifiers` are short strings tied to passport criteria. Use the passport's `qualification.fit_criteria` and `qualification.disqualifiers`; do not invent a universal B2B ICP. Do not use protected traits (race, sex, religion, disability, health status, pregnancy, national origin, etc.) as fit criteria.

Fit is not readiness. A qualified buyer may be exploring, comparing, ready, or stalled. Record readiness separately in `diagnosis.buying_readiness`.

### Diagnosis

`diagnosis` records the current commercial hypothesis:

- `primary_problem` — the buyer's problem in concrete terms;
- `impact` — what the problem costs or blocks;
- `desired_outcome` — what the buyer wants instead;
- `barrier` — the main reason the decision is not moving: `unclear_value`, `no_need`, `no_urgency`, `no_trust`, `price`, `budget`, `authority`, `status_quo`, `risk`, `adoption`, `fit`, or `unknown`;
- `buying_readiness` — `exploring`, `comparing`, `ready`, `committed`, or `stalled`;
- `recommended_action` — the next move the agent believes is most useful.

Revise the diagnosis when new evidence arrives. Do not keep a stale barrier because it justified the previous pitch.

### Needs and constraints

Each need:

```json
{
  "id": "need_1",
  "statement": "buyer's words or close paraphrase",
  "source": "buyer",
  "status": "stated",
  "impact": null,
  "priority": "unknown"
}
```

`status`: `stated`, `confirmed`, `inferred`, `retracted`, `superseded`.

An inferred need must be phrased as a hypothesis when used: "It sounds like…" Never convert an inference into a fact in the CRM or the pitch.

Constraints include budget range, timeline, compliance requirements, geography, language, technical environment, and decision deadlines. Record the source. A constraint is not a disqualifier unless the passport says so.

### Known facts

`known_facts` is an array of typed facts with provenance:

```json
{
  "key": "team_size",
  "value": 8,
  "source": "buyer",
  "status": "current",
  "confidence": "high",
  "checked_at": "2026-10-23T10:00:00+06:00",
  "notes": null
}
```

- `source`: `buyer`, `passport`, `tool`, `business`, `agent_inference`, or `import`.
- `status`: `current`, `superseded`, or `uncertain`.
- Use `checked_at` for facts that can go stale.
- Do not use `known_facts` for raw PII or free-form transcript text.

### Decision

- `authority`: `buyer`, `buyer_with_approval`, `influencer`, `unknown`, `not_authorized`.
- `process`: the buyer's described steps, not the salesperson's ideal funnel.
- `stakeholders`: names/roles only when volunteered; do not guess.
- `timeline`: the buyer's stated timeline; label estimates.

### Objections

```json
{
  "id": "obj_1",
  "type": "price",
  "statement": "It's too expensive",
  "status": "open",
  "resolution": null,
  "evidence_used": [],
  "buyer_response": null
}
```

`type` includes `price`, `budget`, `timing`, `trust`, `fit`, `authority`, `status_quo`, `competitor`, `risk`, `need`, `stall`, `implementation`, `adoption`, and `other`.

`status`: `open`, `resolved`, `accepted_no`, `deferred`, `escalated`.

Do not mark an objection resolved because the agent answered it. Mark it resolved only when the buyer confirms, or when the buyer moves forward without repeating it. A deferred objection must be revisited before commitment.

### Next step

`type`: `none`, `answer_question`, `send_info`, `proposal`, `book`, `pay`, `human`, `follow_up`, `close`, `expand`, `referral`.

`owner`: `agent`, `buyer`, `human`, `business`, or `none`.

`confirmed_by_buyer` must be true before an irreversible action. A vague "sounds good" is not consent to charge a card. A direct purchase may be the next step; a meeting is not the default.

### Consent

Each purpose is an object, not a bare string:

```json
{
  "status": "granted",
  "at": "2026-10-23T10:00:00+06:00",
  "scope": "send the agreed summary",
  "source": "buyer_message"
}
```

Values: `granted`, `denied`, `unknown`, `withdrawn`.

- `follow_up` covers non-transactional follow-up.
- `booking` covers creating or changing a calendar event.
- `payment` covers issuing an invoice or charging.
- `data_sharing` covers sharing buyer data with a third party or using it as a reference.
- `marketing` covers promotional messages, separate from transactional follow-up.

`source`: `buyer_message`, `buyer_action`, `passport`, `import`, `agent_inferred`, or `none`.

When consent is `unknown`, ask or stop. Do not infer consent from silence. A granted consent is limited to its recorded scope; do not reuse a booking consent as marketing consent. Withdrawal is immediate for future actions, but it does not erase legal obligations or records that must be retained.

### Follow-up lifecycle

`follow_up` tracks the runtime state of the next contact:

- `status`: `none`, `eligible`, `scheduled`, `sent`, `replied`, `closed`, `blocked`.
- `basis`: `none`, `buyer_requested`, `agreed_next_step`, `existing_customer`, `buyer_initiated_inquiry`, or `marketing_consent`.
- `attempts`, `last_contact_at`, `next_due_at`, `scheduled_message_id`.
- `close_reason`: `opt_out`, `refused`, `completed`, `expired`, `not_eligible`, `consent_withdrawn`, `max_attempts`, or `null`.

The scheduler owns dispatch. The agent may mark a follow-up `eligible` or request a schedule only when the passport and consent allow it. A scheduled message is not sent until the messaging tool confirms `sent`. When the buyer replies, mark `replied` and cancel any pending schedule.

### Quote and agreed terms

`quote` is the authoritative commercial snapshot used for payment execution:

- `quote_id`, `version`, and `status`;
- `offer_id`, `plan_id`, `quantity`;
- `unit_amount`, `subtotal`, `discount_percent`, `discount_amount`, `tax_amount`, `total_amount`, `currency`;
- `terms`, `approval_ref`, `issued_at`, and `valid_until`.

The quote must match the passport, the buyer's confirmed scope, and any approval reference. If the buyer changes quantity, plan, discount, tax treatment, or terms, create a new quote version. Never send a payment request whose amount or terms differ from the approved quote. `total_amount` excludes tax when the passport says taxes are excluded; the payment tool must calculate and display tax separately.

### Tool results

```json
{
  "tool": "calendar.booking",
  "status": "confirmed",
  "id": "booking_123",
  "checked_at": "2026-10-23T09:55:00+06:00",
  "summary": "2026-10-24 14:00 Asia/Bishkek",
  "error_code": null
}
```

`status` mirrors the authoritative tool vocabulary: `ok`, `created`, `pending`, `confirmed`, `paid`, `sent`, `refunded`, `failed`, `expired`, `unknown`.

Only `confirmed`, `paid`, or the specific success status the contract allows supports a success claim. A `created` invoice is not a paid invoice. An unrecognized status is not confirmation. Store the idempotency key for retries.

### Promises

Every commitment the agent makes ("I'll send it by 4 pm", "I'll ask the manager") goes here with an owner and due time. Do not make a promise the agent cannot keep. At handoff, unresolved promises travel with the summary.

### Handoff

`status`: `none`, `requested`, `created`, `accepted`, `failed`, `completed`.

`reason_code` uses the same vocabulary as [`human.handoff`](../tools/contracts/human-handoff.md):

`human_request`, `authority`, `capability`, `safety`, `legal`, `fraud`, `privacy`, `complaint`, `minor`, `coercion`, `abuse`, `tool_failure`, `agent_error`, `loop`.

`created` requires a tool id. If the tool fails, status is `failed` and the buyer gets a truthful fallback. A handoff pauses automated sales messages; it does not prove a human has accepted the case.

### Open questions

Questions the buyer asked that the agent has not answered. Do not lose them during a stage transition. Answer them before or alongside the next sales step.

---

## 4. Update rules

1. **Answer first.** If the buyer asked a question, record it and answer it before adding a new discovery question.
2. **One new question per turn** unless the buyer asks for a checklist.
3. **No repeat.** Before asking, check `needs`, `constraints`, `known_facts`, and `decision`. If the answer is present and current, use it.
4. **Contradiction.** If a new statement conflicts with an old one and the intent is unclear, ask which is current. Mark the old value `superseded`.
5. **Correction.** If the buyer corrects a name, date, amount, product, or decision, accept the correction immediately without arguing. Update the state, use the new value, and do not repeat the old one.
6. **Scoped refusal.** "No" to a meeting, a channel, a plan, or a discount is not necessarily "no" to the offer. Stop the refused element, preserve the rest, and offer the shortest legitimate alternative. A refusal of the whole offer ends the sales sequence.
7. **Staleness.** Re-check price, availability, and inventory before quoting if `checked_at` is older than the passport's freshness window.
8. **Summarize before irreversible action.** Restate the offer, amount, currency, date/time, timezone, tax treatment, and cancellation terms; ask for confirmation.
9. **Handoff summary.** Include stage, mode, fit, diagnosis, needs, objections, next step, consent, quote, tool results, promises, and open questions. Exclude sensitive data not needed by the human.

---

## 5. What not to store

- passwords, one-time codes, full card numbers, CVV, bank credentials;
- government ID numbers unless the passport explicitly requires them for a regulated process and the channel is approved;
- health records or diagnoses unless required and consented;
- other buyers' personal data;
- free-form transcripts beyond the retention window;
- internal scores, personality labels, or protected traits.

If such data arrives unsolicited, do not repeat it, do not store it beyond the immediate need, and follow the deletion policy.

---

## 6. Handoff summary template

```text
HANDOFF SUMMARY
Conversation: conv_...
Tenant/passport: tenant_... / passport_... v...
Language: ru (buyer also used ky)
Stage/mode: resolve / prove
Buyer: [name/role if volunteered]
Company: [if volunteered]
Fit: qualified — [one-line reason]
Diagnosis: [barrier + readiness + recommended action]
Needs: [1–3 bullets, buyer's words]
Objections: [open/resolved, one line each]
Decision: [authority/process/timeline]
Next step agreed: [what the buyer agreed to]
Consent: follow_up=granted (scope), payment=unknown, marketing=denied
Quote: [id, version, total, currency, validity, approval_ref]
Tool results: [calendar.availability ok; booking not attempted]
Promises: [none / what and by when]
Open questions: [what the buyer asked that remains unanswered]
Why handoff: [reason code + one sentence]
Sensitive data: [none / masked reference only]
```

---

## 7. Example: correction handling

Buyer: "Our budget is around 5,000."
Agent: "Got it — around 5,000."
Later buyer: "Actually the budget is 8,000, but only if onboarding is included."

This is a correction with a condition, not a contradiction to challenge. The agent says:

> "Thanks for correcting me. I'll treat 8,000 as the budget ceiling only if onboarding is included, and 5,000 as the earlier figure. I'll use the corrected version."

State change:

- old constraint `budget_max=5000` → `superseded`;
- new constraint `budget_max=8000`, `conditions="includes onboarding"`, `source="buyer"`;
- if the condition is unclear, add one open question: "Is onboarding included at no extra fee, or is its cost inside the 8,000?"

Do not silently use 8,000 because it is a bigger sale, and do not keep quoting 5,000 after the correction.
