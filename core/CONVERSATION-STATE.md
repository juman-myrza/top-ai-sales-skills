# Conversation State

The agent needs a small, explicit state object to avoid repeating questions, losing promises, and inventing facts. The state is an internal working record, not a CRM and not a transcript dump.

Canonical schema: [`conversation-state.schema.json`](conversation-state.schema.json).

---

## 1. Principles

1. **Minimal** — store what changes the next decision, not everything the buyer said.
2. **Source-labelled** — every business fact records where it came from and whether it is verified.
3. **Append-safe** — corrections create a new value and mark the old one superseded; they do not silently overwrite history.
4. **Consent-aware** — follow-up, booking, payment, and data-sharing consent are separate flags.
5. **Portable** — the state can be summarized for a human handoff without exposing unnecessary sensitive data.
6. **Expirable** — facts such as price, availability, and inventory become stale; store `checked_at` and re-check before use.

---

## 2. Shape

```json
{
  "schema_version": "1.0.0",
  "conversation_id": "conv_...",
  "tenant_id": "tenant_...",
  "passport_id": "passport_...",
  "passport_version": "1.4.0",
  "channel": "whatsapp",
  "language": {
    "primary": "ru",
    "detected": ["ru", "ky"],
    "register": "formal"
  },
  "stage": "discover",
  "buyer": {
    "display_name": null,
    "company": null,
    "role": null,
    "timezone": null,
    "preferred_channel": "whatsapp"
  },
  "fit": {
    "status": "unknown",
    "reasons": [],
    "disqualifiers": []
  },
  "needs": [],
  "constraints": [],
  "decision": {
    "criteria": [],
    "process": null,
    "stakeholders": [],
    "authority": "unknown",
    "timeline": null
  },
  "objections": [],
  "next_step": {
    "type": "none",
    "description": null,
    "confirmed_by_buyer": false,
    "due_at": null
  },
  "consent": {
    "follow_up": "unknown",
    "booking": "unknown",
    "payment": "unknown",
    "data_sharing": "unknown",
    "marketing": "unknown"
  },
  "tool_results": [],
  "promises": [],
  "handoff": {
    "status": "none",
    "reason_code": null,
    "handoff_id": null
  },
  "open_questions": [],
  "updated_at": "2026-10-23T10:00:00Z"
}
```

---

## 3. Field rules

### Identity

- `conversation_id` is stable for the thread. Do not create a new one after a language switch or a topic change.
- `tenant_id` and `passport_id` bind the conversation to one business and one approved passport. Never mix facts from different tenants.
- `passport_version` matters: a price quoted under version 1.3 may be stale after 1.4. Re-check before repeating it.

### Language

- `primary` is the language the agent will use next.
- `detected` records observed languages, not guesses about ethnicity or nationality.
- `register` is `formal`, `neutral`, or `familiar`, based on the buyer's own style. Default to `neutral`.
- A language switch updates `primary` only when the buyer clearly switches or asks to.

### Stage

One of: `open`, `qualify`, `discover`, `value`, `resolve`, `commit`, `execute`, `confirm`, `nurture`, `closed_won`, `closed_lost`, `handoff`.

Stage is a control hint, not a claim about the buyer. A buyer can be ready to buy during `discover`; execute then.

### Fit

`status`: `unknown`, `qualified`, `nurture`, `not_fit`, `insufficient_info`.

`reasons` and `disqualifiers` are short strings tied to passport criteria. Do not use protected traits (race, sex, religion, disability, health status, pregnancy, national origin, etc.) as fit criteria.

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

`status`: `stated`, `confirmed`, `inferred`, `retracted`.

An inferred need must be phrased as a hypothesis when used: "It sounds like…" Never convert an inference into a fact in the CRM or the pitch.

Constraints include budget range, timeline, compliance requirements, geography, language, technical environment, and decision deadlines. Record the source.

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

`status`: `open`, `resolved`, `accepted_no`, `deferred`, `escalated`.

Do not mark an objection resolved because the agent answered it. Mark it resolved only when the buyer confirms, or when the buyer moves forward without repeating it. A deferred objection must be revisited before commitment.

### Next step

`type`: `none`, `answer_question`, `send_info`, `proposal`, `book`, `pay`, `human`, `follow_up`, `close`.

`confirmed_by_buyer` must be true before an irreversible action. A vague "sounds good" is not consent to charge a card.

### Consent

Values: `granted`, `denied`, `unknown`, `withdrawn`.

- `follow_up` covers non-transactional follow-up.
- `booking` covers creating a calendar event.
- `payment` covers issuing an invoice or charging.
- `data_sharing` covers sharing buyer data with a third party or using it as a reference.
- `marketing` covers promotional messages, separate from transactional follow-up.

When consent is `unknown`, ask or stop. Do not infer consent from silence.

### Tool results

```json
{
  "tool": "calendar.book",
  "status": "confirmed",
  "id": "booking_123",
  "checked_at": "2026-10-23T09:55:00Z",
  "summary": "2026-10-24 14:00 Asia/Bishkek",
  "error_code": null
}
```

`status`: `pending`, `confirmed`, `failed`, `unknown`.

A `confirmed` result is required before the agent claims success. Store the idempotency key for retries.

### Promises

Every commitment the agent makes ("I'll send it by 4 pm", "I'll ask the manager") goes here with an owner and due time. Do not make a promise the agent cannot keep. At handoff, unresolved promises travel with the summary.

### Handoff

`status`: `none`, `requested`, `created`, `accepted`, `failed`, `completed`.

`created` requires a tool id. If the tool fails, status is `failed` and the buyer gets a truthful fallback.

### Open questions

Questions the buyer asked that the agent has not answered. Do not lose them during a stage transition. Answer them before or alongside the next sales step.

---

## 4. Update rules

1. **Answer first.** If the buyer asked a question, record it and answer it before adding a new discovery question.
2. **One new question per turn** unless the buyer asks for a checklist.
3. **No repeat.** Before asking, check `needs`, `constraints`, and `decision`. If the answer is present and current, use it.
4. **Contradiction.** If a new statement conflicts with an old one, ask which is current. Mark the old value `superseded`.
5. **Correction.** If the buyer corrects a name, date, amount, or product, update immediately and do not repeat the old value.
6. **Staleness.** Re-check price, availability, and inventory before quoting if `checked_at` is older than the passport's freshness window.
7. **Summarize before irreversible action.** Restate the offer, amount, currency, date/time, timezone, and cancellation terms; ask for confirmation.
8. **Handoff summary.** Include stage, fit, needs, objections, next step, consent, tool results, promises, and open questions. Exclude sensitive data not needed by the human.

---

## 5. What not to store

- passwords, one-time codes, full card numbers, CVV, bank credentials;
- government ID numbers unless the passport explicitly requires them for a regulated process and the channel is approved;
- health records or diagnoses unless required and consented;
- other buyers' personal data;
- free-form transcripts beyond the retention window;
- internal scores or personality labels.

If such data arrives unsolicited, do not repeat it, do not store it beyond the immediate need, and follow the deletion policy.

---

## 6. Handoff summary template

```text
HANDOFF SUMMARY
Conversation: conv_...
Tenant/passport: tenant_... / passport_... v...
Language: ru (buyer also used ky)
Stage: resolve
Buyer: [name/role if volunteered]
Company: [if volunteered]
Fit: qualified — [one-line reason]
Needs: [1–3 bullets, buyer's words]
Objections: [open/resolved, one line each]
Decision: [authority/process/timeline]
Next step agreed: [what the buyer agreed to]
Consent: follow_up=granted, booking=unknown, payment=unknown
Tool results: [calendar.check_availability confirmed 3 slots; booking not attempted]
Promises: [none / what and by when]
Open questions: [what the buyer asked that remains unanswered]
Why handoff: [reason code + one sentence]
Sensitive data: [none / masked reference only]
```

---

## 7. Example: contradiction handling

Buyer: "Our budget is around 5,000."
Agent: "Got it — around 5,000."
Later buyer: "Actually we can go to 8,000 if it includes onboarding."
Agent: "Thanks for clarifying. I'll treat 8,000 as the ceiling including onboarding, and 5,000 as the earlier figure. Which should I use for the proposal?"

State change:

- old constraint `budget_max=5000` → `superseded`;
- new constraint `budget_max=8000`, `conditions="includes onboarding"`, `source="buyer"`;
- open question: "confirm which budget applies".

Do not silently use 8,000 because it is a bigger sale, and do not keep quoting 5,000 after the correction.
