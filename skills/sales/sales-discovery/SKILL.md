---
name: sales-discovery
description: "Diagnose buyer pain, impact, and decision criteria."
version: 1.0.0
author: Jumanazar
license: MIT
metadata:
  hermes:
    tags: [Sales, Discovery, SPIN, Gap, Needs]
    category: sales
    related_skills:
      - sales-qualification
      - sales-value-proof
      - sales-objection-negotiation
      - sales-language-adaptation
---

# Sales Discovery

Discovery is the disciplined search for the few facts that change the recommendation. It is not a questionnaire, a therapy session, or a chance to "agitate pain" until the buyer feels bad enough to buy.

The goal is a shared, accurate picture of:

- the buyer's current situation;
- the problem and its root cause;
- the impact of the problem on the buyer's goals;
- what a better future state looks like;
- the constraints and criteria that will decide the purchase.

Product-specific pains, use cases, and qualifiers come from the passport. This skill provides the universal question logic and the ethical boundaries.

## When to Use

- The buyer has a real problem but the agent does not yet understand it well enough to recommend.
- The buyer asks for a solution before describing the situation.
- The buyer is comparing options and needs help defining criteria.
- The buyer's stated problem sounds generic and the underlying cause is unclear.
- A deal is stuck and the agent suspects the real problem was never surfaced.
- The buyer wants a proposal and the scope depends on discovery.

## When Not to Use

- The buyer is ready to buy and all execution facts are known; close instead.
- The buyer is not qualified; do not deepen discovery on a poor fit.
- The buyer is in crisis, asks for a human, or raises a legal/safety issue; escalate.
- The buyer explicitly declines discovery and wants only a published fact; answer and let them decide.
- The "discovery" would require sensitive data the passport does not authorize.

## Required Inputs

| Input | Source | Why |
|---|---|---|
| Passport problem/use-case map | passport `offer`, `audience` | Keeps questions relevant |
| Qualification outcome | state | Avoids discovering with a non-fit |
| Known facts | state | Prevents repetition |
| Product constraints | passport `fulfillment`, `pricing` | Avoids recommending something impossible |
| Buyer's language/register | state | Natural questioning |
| Consent to continue | conversation | Discovery is a voluntary conversation, not an interrogation |

## Procedure

### Step 1 — Start from what the buyer already said

Do not open with a generic script. Reflect the buyer's words and ask the next question that follows from them.

Example: "You mentioned responses pile up in the evening. When that happens, what usually happens to the customer who is waiting?"

This is better than: "How many employees do you have?"

### Step 2 — Establish the current state

Understand the situation without turning it into a census:

- How does the process work today?
- Who is involved?
- What tools/channels are used?
- What is the volume or frequency, if the buyer knows it?
- What is the workaround when things go wrong?

Ask only what changes the recommendation. "How many people work in marketing?" may be irrelevant if the problem is response time.

### Step 3 — Identify the problem and its root cause

Move from symptom to cause:

- "What happens when…?"
- "Why do you think that happens?"
- "Is that always the case, or only at certain times?"
- "What have you tried?"
- "What made it better or worse?"

Do not accept the first framing. A buyer may say "we need more leads" when the real issue is follow-up speed. Test the framing gently, not argumentatively.

### Step 4 — Explore impact, with the buyer's numbers

Impact can be revenue, cost, time, risk, customer experience, or stress. Ask which impact matters to the buyer; do not assume it is money.

Use buyer-provided numbers. If the buyer does not know, offer a range and label it as an estimate. Never invent a baseline to make the gap look bigger.

Example: "You said about 30 inquiries a week and roughly 1 in 5 waits more than an hour. That's about 6 delayed inquiries a week — is that roughly right, or is the delay more frequent?"

### Step 5 — Define the future state

Ask what "better" would look like in the buyer's terms:

- What would change if this were solved?
- What would you stop doing?
- What would your team or customers notice?
- What would make this worth paying for?
- What would make you decide not to move forward?

The last question is not a trick. It surfaces the real decision criteria and gives the buyer permission to be honest.

### Step 6 — Map the decision

Understand, without interrogating:

- Who else is involved?
- What criteria will they use?
- What is the process (trial, procurement, legal, board)?
- What is the timeline and what drives it?
- What would cause a "no"?
- What would make this an easy yes?

Record what is explicit versus inferred.

### Step 7 — Summarize and confirm

Before moving to value or closing, summarize in the buyer's language:

"Let me check I have this right: [current state], [problem], [impact], [future state], [decision criteria]. Did I miss anything?"

A good summary does three things: proves listening, exposes misunderstandings, and gives the buyer a chance to correct the record. Do not use the summary to slip in a pitch.

### Step 8 — Stop when you have enough

Discovery is complete when you can make a relevant recommendation and identify the next decision. It is not complete when you have asked every question in a framework.

Signs you have enough:

- you can state the buyer's problem in one sentence they agree with;
- you know which capability is relevant and which is not;
- you know the main decision criterion and who decides;
- you know the constraint that could block the sale;
- further questions would not change the recommendation.

## Branches

### Buyer does not know the numbers

- Offer a range or a simple estimation method.
- Label the result as an estimate.
- Ask whether the estimate feels high, low, or about right.
- Do not turn an estimate into a measured fact.

### Buyer is emotional

- Acknowledge the emotion in one sentence.
- Ask what part of the situation is most frustrating.
- Do not rush to a solution while the buyer is venting.
- Do not use the emotion as leverage ("You must be losing sleep — better buy now").

### Buyer is urgent

- Ask what drives the deadline.
- Focus on the minimum facts needed to act.
- Offer the fastest verified path.
- Do not skip consent or verification because of urgency.

### Buyer leads with price

- Answer the price question with verified facts.
- Then ask one question about the use case or scope.
- Do not refuse to give a price as a "discovery tactic".

### Buyer mentions a competitor

- Ask what they are comparing and which criteria matter.
- Do not disparage.
- Do not quote competitor facts you cannot verify.
- Use the comparison to clarify the buyer's criteria, not to attack.

### Buyer wants a proposal immediately

- Explain what the proposal needs (scope, quantity, terms).
- Ask the minimum questions required.
- If the buyer refuses, offer a generic proposal with clearly labeled assumptions, or hand off.
- Do not invent scope to fill the template.

### Buyer is a multi-stakeholder team

- Ask who will use, approve, pay, and block.
- Ask what each cares about, without guessing.
- Offer a summary tailored to the buying group, not a single-person pitch.
- Consider a human-assisted process for complex procurement.

### Buyer is in a regulated industry

- Stay within approved language.
- Do not give legal, medical, or compliance advice.
- Ask about the required process and escalate if it exceeds the passport.
- Do not collect regulated data unless the passport explicitly requires it and the channel is approved.

### Buyer says "just tell me what you do"

- Give a short, verified description.
- Ask one question to determine relevance.
- Do not launch into a full feature list.
- Offer a link or document only if it is approved and useful.

## Stopping Conditions

Stop discovery when:

- you have enough to recommend or disqualify;
- the buyer declines to continue;
- the buyer asks for a human;
- the buyer is clearly ready to buy;
- the conversation becomes unsafe or abusive;
- the required information is unavailable and the buyer does not want a workaround.

Do not stop just because the buyer gave a short answer. A concise buyer may still be engaged.

## Failure Recovery

| Situation | Recovery |
|---|---|
| Buyer says "stop asking questions" | Apologize briefly, answer what you can, offer a direct next step or a human. |
| Buyer contradicts themselves | Name the discrepancy, ask which is current, update state. |
| Buyer's problem is outside the offer | Say so; do not force a fit. Offer a verified alternative or end. |
| The impact is unclear | Say it is unclear; use a range; do not inflate it. |
| The buyer's numbers are sensitive | Ask only for a range; explain why; allow them to skip. |
| The conversation loops | Summarize what is known, name the missing fact, ask one direct question or hand off. |

## Examples

### Example 1 — From symptom to cause

Buyer: "Клиенты жалуются, что мы долго отвечаем."

Agent: "Понял. А в какие моменты задержка заметнее всего — в течение дня, вечером или в выходные?"

Buyer: "Вечером, после закрытия."

Agent: "Что происходит с сообщением, которое приходит после закрытия?"

Buyer: "Оно висит до утра, иногда человек уже не отвечает."

Agent: "То есть проблема не только в скорости, но и в том, что вечерний поток остаётся без ответа до утра. Сколько примерно таких сообщений за вечер?"

Why: moves from complaint to specific mechanism, then quantifies without inventing.

### Example 2 — Impact without exaggeration

Buyer: "Наверное, теряем какие-то продажи."

Agent: "Сколько примерно заявок в неделю остаются без ответа в тот же день?"

Buyer: "Не знаю, может, 5–10."

Agent: "Если взять 5–10 и ваш средний чек, диапазон потерь получится [calculation]. Это верхняя граница, потому что не каждая заявка стала бы продажей. Как вам кажется, ближе к 5 или к 10?"

Why: uses the buyer's range, labels the estimate, and asks the buyer to calibrate.

### Example 3 — Future state

Buyer: "Хочу, чтобы менеджеры не отвлекались на ерунду."

Agent: "Что бы они делали вместо этого, если бы рутина ушла?"

Buyer: "Работали бы с крупными клиентами."

Agent: "То есть цель не просто «быстрее отвечать», а освободить время на крупные сделки. Если рутина уйдёт, сколько часов в неделю это вернёт команде?"

Why: surfaces the outcome the buyer actually wants, not the feature.

### Example 4 — Decision criteria

Buyer: "Мне нужно подумать."

Agent: "Конечно. Чтобы вы думали с полной картиной: что для вас будет главным при решении — [verified criterion A], [verified criterion B] или что-то ещё?"

Why: does not push; asks what the decision will be judged on.

## Counterexamples

- **Interrogation:** 10 questions before answering the buyer's first question.
- **Pain theatre:** "Представьте, как вы теряете деньги каждый день" without evidence.
- **Leading questions:** "Вы же не хотите терять клиентов, правда?"
- **Invented baseline:** "У таких компаний обычно 40% потерь" with no source.
- **Feature fishing:** asking about tools only to find a place to pitch a feature.
- **Therapy:** probing childhood, health, or personal relationships under the guise of discovery.
- **Endless discovery:** refusing to recommend until the buyer fills a 20-field form.
- **Weaponized silence:** using pauses or guilt to force the buyer to reveal more.
- **Ignoring the answer:** asking the next scripted question when the buyer just revealed the real issue.

## Dependencies

- [Core Behavior Contract](../../../core/CORE-BEHAVIOR-CONTRACT.md)
- [Conversation State](../../../core/CONVERSATION-STATE.md)
- [Product Passport](../../../product-passport/README.md)
- `sales-qualification`, `sales-value-proof`, `sales-objection-negotiation`
- [`passport-lookup`](../../../tools/contracts/passport-lookup.md)

## Sources

- Neil Rackham, *SPIN Selling* (1988); Huthwaite International describes the four question types and the investigating stage: <https://www.huthwaiteinternational.com/spin-methodology>. The SPIN sequence is a useful structure, not a rigid script; Huthwaite itself describes it as "a logical persuasive framework — rather than a rigid sequence."
- Keenan, *Gap Selling* (2018), for the current-state → problem → impact → future-state structure: <https://salesgrowth.com/gap-selling-method/>. Gap Selling is a vendor methodology without independent replication in the repository's research.
- Chris Voss, *Never Split the Difference* (2016), for labels and calibrated questions used to clarify, not to trap.
- David Sandler's pain-funnel concept, as described in the Sandler Selling System: <https://sandler.com/sandler-selling-system/>.
- Gartner's B2B buying research, for the multi-stakeholder and looping nature of complex decisions: <https://www.gartner.com/en/sales/insights/b2b-buying-journey>.

The skill deliberately removes "agitation" tactics that encourage the seller to amplify negative emotion. The repository treats discovery as diagnosis, not emotional pressure. See [`research/decisions-and-tradeoffs.md`](../../../research/decisions-and-tradeoffs.md).
