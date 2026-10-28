---
name: sales-objection-negotiation
description: "Resolve objections and negotiate within set authority."
version: 1.1.0
author: Jumanazar
license: MIT
metadata:
  hermes:
    tags: [Sales, Objections, Negotiation, Pricing, BATNA]
    category: sales
    related_skills:
      - sales-value-proof
      - sales-closing-execution
      - sales-integrity-escalation
      - sales-language-adaptation
---

# Sales Objection Handling and Negotiation

An objection is information. Sometimes it is a request for clarity, sometimes a real constraint, sometimes a polite no. The agent's job is to find out which — not to "crush" every objection with a script.

Negotiation is the same discipline applied to terms: understand interests, know the limits, trade rather than give, and accept a legitimate no. The passport defines the limits. This skill defines the process.

## When to Use

- The buyer says the price is too high, the timing is wrong, or a competitor is cheaper.
- The buyer says "I need to think", "send me a proposal", or "I'll get back to you".
- The buyer doubts the quality, safety, or fit of the offer.
- The buyer asks for a discount, extra scope, or special terms.
- The buyer needs approval from someone else.
- The buyer is choosing between the offer and the status quo.
- A deal is stalled and the real blocker is unclear.

## When Not to Use

- The buyer has clearly refused; accept the no and stop.
- The buyer asks for a human; hand off.
- The request is illegal, unsafe, or outside the passport's authority; escalate or refuse.
- The buyer is in crisis; safety first.
- The objection is actually a factual question; answer it instead of "handling" it.
- The agent would need to invent a discount, guarantee, or competitor fact to respond.

## Required Inputs

| Input | Source | Why |
|---|---|---|
| Price, fees, and terms | passport `pricing` | Anchors the response in truth |
| Discount and concession authority | passport `sales_policy` | Defines what can be offered |
| Refund/cancellation policy | passport `pricing` / `sales_policy` | Prevents invented risk reversal |
| Verified proof | passport `proof` | Supports value claims |
| Objection guidance and alternatives | passport `sales_guidance.objection_guidance`, `sales_guidance.alternatives` | Business-specific responses, not generic rebuttals |
| Buyer's stated objection and history | state | Avoids repeating a failed response |
| Decision process and stakeholders | state | Identifies whether the objection is the real blocker |
| Tradables, non-negotiables, walk-away | passport `sales_policy.negotiation` | Defines what may be traded and when to stop |
| Current quote / approved terms | state `quote` | Keeps any concession tied to a versioned, approved snapshot |

## Procedure

### Step 1 — Classify before responding

| Type | Example | First move |
|---|---|---|
| **Price/value** | "Too expensive" | Clarify: compared to what? What outcome is expected? |
| **Budget** | "No budget this quarter" | Explore timing, approval, and a smaller start |
| **Timing** | "Not now" | Ask what would make it timely; accept if it is a no |
| **Trust** | "AI will make mistakes" | Acknowledge, explain verified safeguards, offer a test |
| **Fit** | "This isn't for us" | Check the criterion; accept if true |
| **Authority** | "I need my boss" | Map the decision process; support the champion |
| **Status quo** | "We do it manually" | Understand the cost/benefit of change; do not attack |
| **Competitor** | "X is cheaper" | Clarify criteria; compare verified facts |
| **Risk** | "What if it fails?" | Explain verified risk controls and exit terms |
| **Implementation** | "This will take weeks to set up" | Explain the verified delivery path, owner, and effort; do not minimize real work |
| **Adoption** | "The team won't use it" | Ask who must change, what has failed before, and what support exists |
| **Need** | "We don't really need this" | Return to discovery; accept if true |
| **Stall** | "Send info, I'll think" | Ask what would help; set a consented next step |

Do not assume every objection is a smokescreen. Many are accurate. An implementation or adoption concern is usually a real barrier, not a delay tactic; treating it as a "stall" and repeating a value pitch is the most common way to lose a technically qualified deal.

### Step 2 — Acknowledge without agreeing to a false premise

Use a short label or acknowledgment:

- "That's a fair concern."
- "I can see why the price feels significant."
- "It sounds like the risk of disruption matters more than the cost."

Do not say "I understand" if you are about to argue. Do not mirror an insult. Do not use therapeutic language ("I hear your pain") in a business chat.

### Step 3 — Clarify the real constraint

Ask one question that separates the possible causes:

- "When you say expensive, is it the total amount, the monthly commitment, or the uncertainty about the return?"
- "Is the issue that the budget isn't there, or that it's allocated elsewhere this quarter?"
- "What would need to be true for the timing to work?"
- "Which part feels risky: the setup, the data, or the ongoing quality?"

If the buyer does not want to elaborate, do not push. Respond to the surface objection with verified facts and offer a next step.

### Step 4 — Respond with the right evidence

Match the response to the type:

- **Price:** reframe to total cost/outcome only if the comparison is honest; otherwise clarify scope and payment options from the passport.
- **Budget:** discuss timing, phased start, or a smaller package only if the passport allows it. Do not invent financing.
- **Trust:** show verified safeguards, pilot options, human handoff, and exit terms. Do not claim "zero errors".
- **Fit:** revisit the buyer's criteria. If the offer is not a fit, say so.
- **Authority:** give the champion a short, accurate internal summary. Do not ask them to misrepresent.
- **Status quo:** quantify the cost of the current process with the buyer's numbers, not invented ones.
- **Competitor:** compare on the buyer's criteria with verified facts. Do not disparage.
- **Risk:** explain verified guarantees, SLAs, refunds, data handling, and reversibility.
- **Implementation:** state the verified setup steps, who owns them, and the realistic effort. Do not promise a fast setup the passport does not support.
- **Adoption:** diagnose who has to change, what the last failed attempt was, and what support is included. Offer the smallest viable adoption path.
- **Stall:** ask what specific information would help; offer a low-friction next step.

Use at most one new argument per turn. A wall of rebuttals signals fear, not confidence.

### Step 5 — Check whether the objection moved

Ask a calibration question:

- "Does that address the concern, or is there still a gap?"
- "What would make this feel safe enough to try?"
- "Is price the only blocker, or is there something else?"

Do not ask "Now do you understand?" Do not treat a nod as a closed objection.

### Step 6 — Negotiate only within authority

Before making any concession, check the passport:

- If `sales_policy.negotiation` is absent, treat it as: no tradables beyond the published `discount_policy`, no custom terms, and no authority to go below the published floor. Do not infer tradables.
- Is discounting allowed?
- What is the maximum percentage or amount?
- Who must approve?
- What can be traded? Read `sales_policy.negotiation.tradables` (term length, scope, payment schedule, start date, case-study permission, referral).
- What is forbidden? Read `sales_policy.negotiation.non_negotiables`.
- What is the walk-away point (`sales_policy.negotiation.walk_away`)?

Negotiation rules:

1. **Never open with a discount.** Diagnose first.
2. **Never concede without a trade.** If the buyer wants a lower price, ask for a longer term, a faster start, a smaller scope, or a public reference — whichever `tradables` permits.
3. **Correct your own error first.** If the business published a wrong price, missed a promised feature, or overcharged the buyer, fix the error and honor the advertised terms. That is not a concession to trade. "Trade, do not give" does not apply to money or scope the buyer was already owed.
4. **One concession at a time.** Do not bundle unrequested extras.
5. **Do not bid against yourself.** Wait for the buyer's counter.
6. **Do not invent a competing offer or deadline.**
7. **Do not promise approval you do not have.**
8. **Protect the walk-away.** If the deal is below the passport floor, say no or escalate.
9. **Record the agreed terms in a new quote version.** If the amount, quantity, discount, tax treatment, or terms change, create a new version, summarize it, and get fresh confirmation. Never execute a payment against a discounted or changed amount that is not in an approved quote.
10. **Do not trade away a non-negotiable** to save the deal.

### Step 7 — Know when to stop

Accept the no when:

- the buyer has clearly refused;
- the buyer's budget is below the floor and no approved option exists;
- the buyer requires terms the business cannot meet;
- the buyer is not a fit;
- the buyer is negotiating in bad faith or abusive;
- continuing would require deception or pressure.

A clean no preserves the relationship and the business's pricing integrity.

## Branches

### "It's too expensive"

1. Clarify: total price, monthly price, or value uncertainty?
2. If value uncertainty: return to the buyer's criteria and verified proof.
3. If budget: ask what range is available; check passport options.
4. If comparison: ask what they are comparing; compare verified scope.
5. Never respond with "What's your budget?" as the first move; it feels like a trap.

### "I need to think about it"

- Accept the need to think.
- Ask what would make the decision easier: information, a person, a trial, or time.
- Offer a specific, consented follow-up.
- Do not manufacture a deadline.
- Do not ask the same question repeatedly.

### "Send me a proposal / brochure"

- Clarify what the proposal should cover and who will read it.
- Send only approved materials.
- Put assumptions and validity dates in the proposal.
- Ask for a specific next step after they read it.
- Do not use the proposal as a way to avoid a decision conversation; if the buyer wants to decide, help them.

### "The competitor is cheaper"

- Ask which competitor and which scope.
- Compare like with like: term, support, implementation, fees, risk.
- Do not invent the competitor's price.
- If the competitor is genuinely cheaper for the same scope, acknowledge it and explain the trade-off or accept the no.
- Do not disparage.

### "We already have a team/process"

- Acknowledge the existing investment.
- Ask what works and what does not.
- Position as augmentation only if the passport supports it.
- Do not claim the team is failing.
- If the current process is sufficient, say so.

### "I need approval"

- Ask who decides and what they need.
- Offer a short, accurate summary.
- Offer to join a call if the passport allows.
- Do not pressure the champion to "just get it approved".

### "Give me a discount"

- Ask why the discount is needed (budget, comparison, risk, timing).
- Check authority and the passport's `discount_policy` and `sales_policy.negotiation`.
- If allowed, trade for a commitment and record the result in a new quote version.
- If not allowed, say so and offer a non-price alternative if one exists.
- Do not invent a "special price" to test the buyer.
- Do not stack discounts the passport says cannot be stacked.

### "You charged me the wrong amount / you broke your own promise"

- This is an entitlement issue, not a negotiation. Verify the original quote, terms, and payment record first.
- If the business was wrong, correct it immediately and do not require a trade.
- If the buyer is mistaken, show the exact quote version and terms without arguing.
- Route a disputed charge or refund to the documented process; do not improvise compensation.

### "I'll pay later / can we start now and pay after results?"

- Check the passport's payment terms.
- Do not offer outcome-based payment unless it is explicitly approved.
- If the buyer cannot meet the terms, escalate or decline.

### "Guarantee the result or I walk"

- State the actual guarantee/warranty/refund policy.
- If the buyer needs more, hand off to a human; do not invent.
- Accept the walk-away if the business cannot meet it.

### Buyer becomes aggressive

- Do not match the aggression.
- Set a boundary once: "I want to help, but I won't continue if we speak like this."
- Offer a human or end the conversation.
- If there is a threat, follow the safety protocol.

### Negotiation is complex or multi-party

- Do not improvise terms.
- Summarize the positions and hand off to a human with authority.
- Preserve the buyer's requested terms in the handoff.

## Stopping Conditions

Stop the objection/negotiation loop when:

- the objection is resolved and the buyer confirms;
- the buyer accepts the no;
- the buyer is not a fit;
- the request exceeds authority and is handed off;
- the buyer refuses to engage further;
- the conversation becomes abusive or unsafe;
- continuing would require a false claim or an unauthorized concession.

## Failure Recovery

| Situation | Recovery |
|---|---|
| Agent promised an unauthorized discount | Correct immediately; do not honor it without approval; escalate. |
| Buyer caught a factual error | Acknowledge, correct, show the verified source, and re-quote. |
| Objection keeps repeating | Stop rebutting; ask what is really blocking; consider handoff. |
| Buyer says "you're not listening" | Stop, summarize their position, ask what you missed. |
| Negotiation reaches a deadlock | Summarize both positions; offer a human or a pause. |
| Buyer uses a false premise | Correct gently with evidence; do not argue. |
| Buyer threatens a public complaint | Do not bribe or threaten back; follow the escalation/complaint process. |

## Examples

### Example 1 — Price objection, clarified

Buyer: "Too expensive."

Agent: "Understood. Too expensive compared with what - the budget you had in mind, or another offer?"

Buyer: "The budget. We have less for this."

Agent: "Thank you for being direct. There are two paths: [verified smaller scope] or [verified payment option]. Both change [verified trade-off]. Which is closer to your budget?"

Why: clarifies before discounting, uses only passport options, and does not invent a price.

### Example 2 — "I need to think"

Buyer: "I will think about it."

Agent: "Of course. So I am not guessing: what would help you decide - [verified proof], [verified trial], or a conversation with [verified role]? If now is not the time, I will not insist."

Why: offers concrete help, respects the pause, no fake deadline.

### Example 3 — Competitor cheaper

Buyer: "The competitor is cheaper."

Agent: "Possibly. To compare fairly: do they offer the same [verified scope] and [verified support]? If so, I will not claim we are cheaper. I can show what you pay for with us and where you can save without losing [verified outcome]."

Why: does not invent the competitor's price or attack them; invites a like-for-like comparison.

### Example 4 — Unauthorized discount

Buyer: "Take 30% off and I will buy."

Agent: "I cannot offer 30% - that is above my limit. What I can do: [verified allowed concession] in exchange for [verified commitment]. If you need a different figure, I will pass it to the manager, but I will not promise the outcome in advance."

Why: states the limit, offers an authorized trade, and does not fake approval.

### Example 5 — Accepting no

Buyer: "No, thanks, not interested."

Agent: "Understood, thank you for the reply. I will not write again. If the situation changes, you know where to find me."

Why: one acknowledgment, no rebuttal, clean exit.

## Counterexamples

- **Objection crushing:** responding to every concern with a prepared rebuttal.
- **Discount reflex:** offering 10% before understanding the objection.
- **Fake competitor intel:** "They have no support" without evidence.
- **False deadline:** "The price will rise tomorrow" when no price change is scheduled.
- **Guilt:** "You understand you are losing money every day, don't you?"
- **Endless looping:** repeating the same value pitch after the buyer said it does not address the concern.
- **Pressure after no:** "Let's have one more call; you just did not understand."
- **Unauthorized terms:** promising net-60, a custom SLA, or a refund outside the passport.
- **Winning the argument:** proving the buyer wrong and losing the relationship.
- **Untracked concession:** agreeing to a lower price or extra scope without a new approved quote version.
- **Entitlement trade:** withholding a correction the buyer is owed until they concede something.
- **Adoption dismissal:** replying to "the team won't use it" with another value pitch instead of an adoption plan.

## Dependencies

- [Core Behavior Contract](../../../core/CORE-BEHAVIOR-CONTRACT.md)
- [Conflict Resolution](../../../core/CONFLICT-RESOLUTION.md)
- [Conversation State](../../../core/CONVERSATION-STATE.md)
- [Product Passport](../../../product-passport/README.md)
- `sales-value-proof`, `sales-closing-execution`, `sales-integrity-escalation`
- [`passport-lookup`](../../../tools/contracts/passport-lookup.md), [`human-handoff`](../../../tools/contracts/human-handoff.md)

## Sources

- Chris Voss, *Never Split the Difference* (2016), for labeling, mirroring, calibrated questions, and tactical empathy. The Black Swan Group describes the method as "precision listening with Tactical Empathy": <https://www.blackswanltd.com/>. The repository uses the listening and clarification tools, not hostage-negotiation tactics that would be inappropriate in a sales chat.
- Roger Fisher, William Ury, and Bruce Patton, *Getting to Yes* (1981; later editions), for interests vs. positions, BATNA, and principled negotiation. Harvard's Program on Negotiation publishes related free resources: <https://www.pon.harvard.edu/>.
- Robert Cialdini, *Influence*, for reciprocity, consistency, social proof, authority, liking, scarcity, and unity — with the ethical limits Cialdini emphasizes: <https://www.influenceatwork.com/7-principles-of-persuasion/>.
- David Sandler's "negative reverse selling" and pain-funnel concepts, as described by Sandler: <https://sandler.com/sandler-selling-system/>. The repository does not use negative reverse selling to humiliate or manipulate; it uses permission to say no.
- Jim Camp, *Start with No* (2002), for no-need positioning and decision clarity.
- Gartner's B2B buying research, for multi-stakeholder consensus and unhealthy conflict: <https://www.gartner.com/en/newsroom/press-releases/2025-05-07-gartner-sales-survey-finds-74-percent-of-b2b-buyer-teams-demonstrate-unhealthy-conflict-during-the-decision-process>.

These are practitioner frameworks and negotiation research, not proof that a specific script will close a specific deal. See [`research/claim-evidence-matrix.md`](../../../research/claim-evidence-matrix.md).
