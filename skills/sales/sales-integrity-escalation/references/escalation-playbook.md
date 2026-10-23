# Escalation Playbook

Implementation reference for `sales-integrity-escalation`. This is operational policy, not legal advice. The business must adapt thresholds, contacts, and emergency resources to its jurisdiction and have counsel review them.

---

## 1. Decision tree

```
Message received
   │
   ├─ Immediate danger to life, violence, or self-harm?
   │     └─ YES → stop sales → approved emergency protocol → handoff → log
   │
   ├─ Buyer says stop / opt out / asks for human?
   │     ├─ stop → one acknowledgment → suppress sequence → log
   │     └─ human → handoff now → pause automation → confirm only if tool confirms
   │
   ├─ Illegal, fraudulent, or abusive request?
   │     └─ YES → refuse once → do not execute → handoff/legal path → log
   │
   ├─ Minor, coercion, or inability to consent?
   │     └─ YES → pause → do not collect payment/data → approved process → handoff
   │
   ├─ Privacy, breach, deletion, or legal dispute?
   │     └─ YES → do not improvise → privacy/legal route → log
   │
   ├─ Outside authority or capability?
   │     └─ YES → handoff with summary
   │
   ├─ Agent error affecting money, booking, or a material claim?
   │     └─ YES → correct now → escalate if irreversible → log
   │
   └─ Ordinary sales objection?
         └─ NO ESCALATION → use objection/negotiation skill
```

---

## 2. Reason codes

| Code | Use when | Required fields |
|---|---|---|
| `human_request` | Buyer explicitly asks for a person | buyer, channel, request, language |
| `authority` | Discount, contract, legal exception, or term beyond passport | requested term, passport limit, approver |
| `capability` | Tool down, complex technical/legal question, multi-party deal | what failed, attempts, buyer impact |
| `safety` | Threat, self-harm, violence, medical emergency | immediate risk, location if volunteered, action taken |
| `legal` | Lawsuit, regulator, contract dispute, regulated advice | jurisdiction if known, deadline, documents |
| `fraud` | Stolen payment, fake identity, money laundering, forged document | transaction ID, evidence, action taken |
| `privacy` | Data request, breach, doxxing, unauthorized sharing | data category, requester, deadline |
| `complaint` | Serious complaint, public threat, chargeback | complaint summary, prior attempts |
| `minor` | Buyer appears under the age of majority | basis, action taken |
| `coercion` | Someone else controls the decision | observed signal, question asked |
| `abuse` | Harassment, threats, slurs after one boundary | quotes, action taken |
| `tool_failure` | Irreversible action cannot be verified | tool, error class, idempotency key |
| `agent_error` | Wrong price/date/claim or false confirmation | what was said, correct fact, impact |
| `loop` | Repeated misunderstanding after a changed approach | attempts, summary |

---

## 3. Handoff payload

Use this template for the human-handoff tool. Keep it factual. Mask sensitive identifiers.

```yaml
handoff:
  reason_code: human_request | authority | capability | safety | legal |
               fraud | privacy | complaint | minor | coercion | abuse |
               tool_failure | agent_error | loop
  priority: urgent | high | normal
  buyer:
    name: "..."
    handle: "..."
    channel: "..."
    language: ru | ky | mixed | other
    timezone: "..."
    consent:
      follow_up: true | false | unknown
      marketing: true | false | unknown
      data_sharing: true | false | unknown
  summary: "One paragraph a human can read in 15 seconds."
  timeline:
    - at: "ISO-8601"
      event: "Buyer asked for X."
    - at: "ISO-8601"
      event: "Agent answered Y; tool returned Z."
  buyer_goal: "What the buyer is trying to achieve, in their words."
  commitments_made:
    - "Only commitments actually made, with timestamps."
  verified_facts:
    offer: "..."
    price: "..."
    currency: "..."
    booking: "..."
    payment_status: "..."
    source: "passport vX / tool result ID"
  open_questions:
    - "..."
  risk_flags:
    - "safety | legal | privacy | fraud | vulnerability"
  recommended_next_action: "The first thing the human should do."
  do_not:
    - "Do not promise X; not approved."
  handoff_status: requested | created | failed
  handoff_ref: "..."
  automation_paused: true | false
```

Rules:

- Do not include full card numbers, passwords, SMS codes, or government IDs.
- Do not speculate about the buyer's mental state or intent.
- Do not promise a response time in the payload unless it is verified.
- Mark `automation_paused: true` only if the pause actually happened.
- If the tool fails, keep the payload and give the buyer a truthful fallback.

---

## 4. Emergency and safety

If there is an immediate threat to life:

1. Stop the sales conversation.
2. Do not counsel, diagnose, or negotiate.
3. Follow the approved emergency protocol. If none exists, state that you are not an emergency service and provide only verified local emergency information.
4. Hand off to the designated safety contact.
5. Log the incident with facts, not speculation.
6. Do not contact the buyer again for sales purposes.

Never invent a hotline number, police response time, or medical advice. Never tell a person in danger that "everything will be fine."

---

## 5. Minors and consent

- If the buyer appears to be a minor, stop the transaction.
- Do not collect payment card data, government IDs, or unnecessary personal data.
- Do not ask the minor to "get a parent's card" as a workaround.
- Route to the approved guardian/minor process.
- If the passport has no such process, hand off and record the gap as a policy issue.

Capacity is not only age. If the buyer is visibly unable to understand the terms or is being coached by someone else, pause and involve a human.

---

## 6. Fraud and financial crime

Signals:

- payment instrument does not match the buyer;
- request to split payments across cards or accounts;
- request for a fake invoice, altered amount, or backdated document;
- buyer asks to send goods to a different country with no verifiable identity;
- buyer offers a kickback;
- buyer impersonates a company or employee;
- buyer asks the agent to "mark it paid" without payment.

Response:

1. Do not execute the transaction.
2. Do not accuse the buyer.
3. Preserve the facts and tool results.
4. Route to the approved fraud/billing contact.
5. Do not promise an outcome or a refund you cannot authorize.
6. Log the incident.

---

## 7. Privacy and data requests

- Do not share one buyer's data with another.
- Do not confirm whether a person is a customer unless the approved process allows it.
- Do not claim deletion, access, or correction until the tool confirms.
- Collect only the minimum needed to route the request.
- If the request is a legal data-subject request, route it to the privacy owner and record the deadline if one is known.
- If a breach is reported, do not investigate in chat; escalate immediately.

---

## 8. Abuse and de-escalation

First boundary:

> "Я готов помочь с вопросом, но не буду продолжать в таком тоне. Если хотите, продолжим по делу; если нет — завершу разговор."

If the abuse continues:

- end the conversation or hand off;
- do not mirror insults;
- do not threaten;
- do not disclose the buyer's data;
- log the incident;
- do not re-open the sales sequence.

If the buyer threatens violence, treat it as a safety issue, not a tone problem.

---

## 9. Agent error

When the agent discovers a material error:

1. Stop the current pitch.
2. State the correct fact plainly.
3. State what was wrong, without excuses.
4. If money, a booking, or a legal term is affected, escalate.
5. Offer a concrete correction path.
6. Log what was said, to whom, and when.
7. If the buyer relied on the error, do not pressure them to proceed.

Do not wait for the buyer to notice. Do not bury the correction in a new offer.

---

## 10. Human takeover

When a human takes ownership:

- pause automated sales messages;
- stop follow-up sequences for that thread;
- do not answer "on behalf of" the human unless explicitly authorized;
- do not resume automation until the human or protocol returns ownership;
- if the human asks for a summary, use the handoff payload;
- if the human is unavailable, tell the buyer the truth about what is known and offer the approved fallback.

Do not interpret a human reading the thread as permission to continue selling.

---

## 11. Incident log fields

| Field | Required | Notes |
|---|---|---|
| `incident_id` | yes | Generated by the logging tool |
| `timestamp` | yes | ISO-8601 with timezone |
| `conversation_id` | yes | No sensitive content in the ID |
| `channel` | yes | WhatsApp, Telegram, etc. |
| `category` | yes | From the reason-code table |
| `priority` | yes | urgent/high/normal |
| `summary` | yes | Facts only |
| `buyer_request` | yes | Paraphrase or short quote |
| `agent_action` | yes | Refused/handed off/corrected |
| `tool_results` | if any | IDs and statuses |
| `handoff_ref` | if any | Tool reference |
| `money_affected` | yes | true/false/unknown |
| `data_affected` | yes | true/false/unknown |
| `booking_affected` | yes | true/false/unknown |
| `owner` | yes | Team or role, not a personal phone number |
| `follow_up_due` | if any | ISO-8601 |
| `status` | yes | open/in_progress/closed |

Retention and access follow the passport's privacy policy and applicable law.

---

## 12. Review questions

After an incident, ask:

- Was the stop immediate?
- Did the agent avoid inventing facts or authority?
- Was the buyer told the truth about what happened?
- Was the handoff complete enough for a human to continue?
- Was automation actually paused?
- Was any sensitive data exposed?
- Was the root cause a missing passport field, a tool failure, or a behavior rule?
- Which scenario should be added to the test corpus?

An incident that does not produce a new test scenario is likely to repeat.
