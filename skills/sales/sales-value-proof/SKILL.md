---
name: sales-value-proof
description: "Prove value with verified evidence, never invented claims."
version: 1.2.0
author: Jumanazar
license: MIT
metadata:
  hermes:
    tags: [Sales, Value, Proof, ROI, Evidence]
    category: sales
    related_skills:
      - sales-discovery
      - sales-objection-negotiation
      - sales-closing-execution
      - sales-integrity-escalation
---

# Sales Value Proof

Value is not a adjective. It is a defensible connection between what the buyer needs and what the offering actually does, supported by evidence the buyer can check.

This skill prevents the two most common failure modes in AI sales:

1. **Feature dumping** — listing capabilities without relevance.
2. **Proof inflation** — inventing case studies, ROI, guarantees, or scarcity to make the value feel bigger.

All offer facts, proof points, prices, and permissions come from the passport. If the passport does not contain a proof point, the agent does not have one.

## When to Use

- The buyer understands the problem but has not connected it to the offer.
- The buyer asks "why this?", "what results can I expect?", or "how is this different?".
- The buyer needs an internal business case.
- The buyer is comparing options and needs criteria.
- The buyer challenges a claim and evidence is required.
- A proposal or recommendation needs a value summary.

## When Not to Use

- The buyer has already decided and only needs execution details; do not re-sell.
- The buyer has not described a problem; go back to discovery.
- The buyer asks for a guarantee or result the passport does not support; use the refusal path.
- The proof would require sharing confidential or unapproved customer data.
- The conversation is a support issue, not a purchase decision.

## Required Inputs

| Input | Source | Why |
|---|---|---|
| Verified offer capabilities | passport `offer` | Prevents feature invention |
| Verified proof points and permissions | passport `proof` | Prevents fake case studies |
| Pricing and terms | passport `pricing` | Makes ROI honest |
| Buyer's problem, impact, criteria | state / discovery | Makes value relevant |
| Approved comparison facts | passport `proof` / `offer` | Prevents competitor fabrication |
| Audience/stakeholder | state | Tailors the proof |

If the passport marks a proof point `estimated` or `unknown`, do not present it as verified. If it has no proof at all, say what is not yet proven and offer a demo, trial, reference call, or pilot if the passport allows it.

## Procedure

### Step 1 — Restate the buyer's problem and criterion

Before proving value, confirm the target:

"You said the main issue is [problem], and the decision will turn on [criterion]. Is that still right?"

If the buyer corrects you, update before continuing. A proof aimed at the wrong problem is noise.

### Step 2 — Choose the smallest relevant proof

There is no single "best" evidence type. Choose the evidence that best matches the claim and the buyer's actual uncertainty. A verified generic fact does not beat the buyer's own number when the question is about the buyer's situation; a documented outcome beats a generic fact when the question is "does this actually work?".

| Evidence | Best for | Rule |
|---|---|---|
| Verified passport fact about the offer | "What does it do?" | State directly with scope and conditions |
| Verified customer outcome with permission | "What results did others get?" | Match the segment and mechanism; name the source only if permitted |
| Verified third-party data | "What is normal in the market?" | Cite source and date |
| Buyer-provided numbers in a calculation | "What would this mean for us?" | Show the formula and assumptions; attribute the numbers |
| Clearly labeled estimate or scenario | "What could happen?" when no measured data exists | Say "estimate" and explain assumptions |
| General principle or analogy | Orientation only | Do not dress it as a result |

Rules:

- Never upgrade a weaker item into a stronger one. A scenario is not a case study. A case study is not a guarantee.
- Relevance beats volume: one matching proof is better than five adjacent ones.
- If the case study's segment or mechanism differs from the buyer's, say that it is adjacent, not equivalent.
- State the uncertainty the evidence does not remove. Do not let a strong case study imply a guarantee.
- If the buyer's own data contradicts a passport statistic, use the buyer's data for their calculation and present the passport figure only as a labeled benchmark.

### Step 3 — Connect capability → mechanism → outcome

Use a three-part structure:

1. **Capability:** what the offer actually does (verified).
2. **Mechanism:** how that changes the buyer's current situation.
3. **Outcome:** what the buyer could expect, with the appropriate qualifier.

Example shape: "[Verified capability] means [mechanism], which addresses [buyer's problem]. In a documented case with [verified segment], the result was [verified outcome] over [verified period]. That is one data point, not a promise for your situation."

Do not skip the mechanism. "We use AI" is not a mechanism. "The agent answers within the channel and hands off when a rule is hit" is a mechanism, if verified.

### Step 3a — Teach one useful insight, tailor it, then lead

Use the Challenger idea as a compact conversation move, not as a rigid script:

1. **Teach:** offer one relevant insight or reframe that helps the buyer see a material trade-off they may have missed.
2. **Tailor:** connect it to this buyer's stated situation, role, or decision criterion.
3. **Take control of the process:** state the recommendation or next step that follows from the insight. Guide the decision process; do not try to control the buyer.

Build a reframe from the buyer's own facts or a verified source. If it is an inference, label it as a possibility and invite correction. Do not manufacture a hidden problem, claim that the buyer is losing money without their numbers, invent market norms, or present generic advice as proprietary expertise.

Constructive tension means making a real trade-off visible, not frightening or cornering the buyer. Challenge the current assumption only when doing so helps the decision. Then move forward; do not deliver a mini-lecture or force the buyer to agree with your framing.

Shape: "[Buyer fact or verified constraint]. That suggests [specific implication, with uncertainty labeled if needed]. I recommend [next path] because [verified reason]. The trade-off is [limitation]."

If there is no useful, defensible insight to add, skip this step and answer or recommend directly.

### Step 4 — Make the math honest

When calculating ROI, savings, payback, or cost of inaction:

1. Write the formula.
2. Use buyer-provided or verified inputs.
3. Label assumptions.
4. Show a range when inputs are uncertain.
5. State what the calculation does **not** include.
6. Offer to redo it with better data.

Template:

"Calculation: [volume] × [conversion assumption] × [value per sale] = [range]. Assumptions: [list]. This is an upper-bound estimate; it does not include [costs/risks]. If [input] is different, the result changes to [range]."

Never say "you will save X" when the number is an estimate. Say "the estimate is X under these assumptions."

### Step 5 — Tailor to the stakeholder

Different stakeholders need different proof:

- **Economic buyer:** payback, total cost, risk, strategic fit.
- **User:** workflow, effort, learning curve, reliability.
- **Technical evaluator:** integration, security, data handling, failure modes.
- **Procurement/legal:** terms, compliance, liability, references.
- **Champion:** a concise internal case they can forward.

Use only verified facts for each. Do not invent a "technical" claim because the stakeholder is technical.

### Step 6 — Check understanding, not agreement

Ask:

- "Which part is most relevant to your decision?"
- "What evidence would you need to feel confident?"
- "Does that answer the question, or is there a gap?"

Do not ask "Do you see the value now?" That invites performance, not honesty. Do not treat silence as agreement.

### Step 6a — Make a recommendation, not a menu

When the buyer is choosing between plans or options, do not hand over an unranked feature table. Synthesize:

- the one option that best fits the buyer's stated criteria;
- the reason it fits, tied to a verified fact;
- the trade-off the buyer accepts by choosing it;
- the one condition that would change the recommendation.

Shape: "For [stated goal] and [main criterion], I would start with [option] because [verified reason]. The trade-off is [verified limitation]. If [condition] matters more than we discussed, [other option] would be worth a look."

If the buyer genuinely has two equally valid paths, say what each path optimizes and ask which matters more. Do not present ten options and call it helpful.

### Step 7 — Stop when the value is clear or the gap is evidence

If the buyer understands and has no material doubt, move to the next step. If the buyer needs evidence you do not have, say so and offer a path: demo, trial, reference, pilot, or human conversation. Do not repeat the same value pitch with more adjectives.

## Branches

### Buyer asks for a case study

- Check the passport for an approved case study.
- Share only what the passport permits (name, logo, quote, metrics).
- If none is approved, say so and offer an anonymized outcome or a reference call if allowed.
- Never invent a customer or composite "case study" presented as real.

### Buyer asks "what results can I expect?"

- Give a verified range or documented outcome if one exists.
- Otherwise say the result depends on [verified factors] and offer a pilot or a measurement plan.
- Do not promise a number.
- Do not imply a guarantee.

### Buyer asks for a guarantee

- State the actual guarantee/warranty/refund policy from the passport.
- If there is none, say there is none.
- If the buyer requires one, hand off to a human who can discuss a custom agreement.
- Do not invent a "satisfaction guarantee" to close.

### Buyer asks for a competitor comparison

- Ask which criteria matter.
- Compare only on verified facts.
- Do not disparage; do not invent competitor weaknesses.
- If you lack verified data, say so and explain your own trade-offs.
- Do not claim "we're the only one that…" unless the passport verifies it.

### Buyer asks for ROI

- Use the buyer's numbers; label assumptions.
- Show a range and sensitivity.
- Do not include unverified productivity savings.
- Offer to validate with a pilot.

### Buyer is skeptical of all claims

- Agree that skepticism is reasonable.
- Ask what evidence would change their mind.
- Offer the smallest verifiable test (demo, trial, reference, audit).
- Do not respond with more claims.

### Buyer's stakeholder is risk-averse

- Lead with risk reduction, reversibility, and exit terms.
- Use verified security/compliance facts only.
- Offer a phased start if the passport allows it.
- Do not minimize real risks.

### No proof is available

- Say plainly: "We don't have a verified case study for that yet."
- Explain what is known.
- Offer a demo, pilot, or reference if approved.
- Do not fill the gap with a hypothetical presented as fact.

## Stopping Conditions

Stop proving value when:

- the buyer confirms the relevance and has no material unanswered question;
- the buyer says the evidence is insufficient and declines a path to get it;
- the buyer asks for a human;
- the buyer is ready to decide;
- the proof would require unapproved data;
- repeating the pitch would add pressure without new information.

## Failure Recovery

| Situation | Recovery |
|---|---|
| Passport proof is missing | Say it is missing; offer a verified alternative or a path to obtain it. |
| Proof is marked estimated | Label it; do not present it as measured. |
| Case study permission is unclear | Do not share the name; ask for permission or use only approved anonymized facts. |
| Calculation inputs are missing | Show the formula with placeholders and ask for the inputs. |
| Buyer disputes a fact | Check the source; if wrong, correct immediately; if right, show the source and date. |
| Competitor claim is unverified | Withdraw it; do not repeat. |
| Buyer feels pressured by ROI | Acknowledge; return to their criteria; offer a smaller next step. |

## Examples

### Example 1 — Verified proof with scope

Buyer: "What results have other clients had?"

Agent: "In [verified case], [verified segment] reduced [verified metric] from [verified before] to [verified after] over [verified period]. That is one confirmed case, not a guarantee for your situation. Would you like me to show which conditions there match yours and which do not?"

Why: cites only approved facts, states the limit, and invites the buyer to test relevance.

### Example 2 — Honest ROI range

Buyer: "How much will I save?"

Agent: "It depends on two figures: [input A] and [input B]. Using your range [A] and [B], the result is [range] per month. That is an upper-bound estimate: it assumes [assumption] and does not include [excluded cost]. Let's use your real numbers - which ones do you know exactly?"

Why: formula, range, assumptions, exclusions, and a request for better data.

### Example 3 — No proof available

Buyer: "Do you have a case study in my niche?"

Agent: "We do not have a confirmed case study specifically in [niche] yet. There are [verified adjacent case] and [verified product fact]. I do not want to present one as the other. I can show a demo on your scenario or arrange a conversation with [verified reference type], if that helps."

Why: does not fabricate a case; offers real alternatives.

### Example 4 — Competitor comparison

Buyer: "How are you better than [competitor]?"

Agent: "It depends on what matters most to you. On [verified criterion A] we have [verified fact]; on [verified criterion B] - [verified trade-off]. For [competitor] I do not have verified data, so I will not invent it. Which two criteria are decisive for you?"

Why: fair, specific, admits the gap, and returns the decision to the buyer's criteria.

## Counterexamples

- **Fabricated case study:** "We had a client who increased revenue by 300%" with no source.
- **Fake precision:** "You will save exactly 47,382" from invented inputs.
- **Guarantee inflation:** "We guarantee the result" when the passport has no guarantee.
- **Feature dump:** 12 bullets with no connection to the buyer's problem.
- **Borrowed authority:** "All the big companies trust us" without evidence.
- **Competitor smear:** "Everything is broken over there" without verified facts.
- **Testimonial without permission:** sharing a customer name or quote that is not approved.
- **False uniqueness:** "No one else on the market does this" without evidence.
- **Pressure through ROI:** "You do not want to lose that much money, do you?" used to force a decision.
- **Evidence dump:** every case study and statistic, whether or not it matches the buyer's situation.
- **Menu, not advice:** listing five plans with no recommendation and calling it neutrality.
- **Misapplied proof:** presenting an adjacent-segment case as if it were the buyer's segment.

## Dependencies

- [Core Behavior Contract](../../../core/CORE-BEHAVIOR-CONTRACT.md)
- [Conversation State](../../../core/CONVERSATION-STATE.md)
- [Product Passport](../../../product-passport/README.md)
- `sales-discovery`, `sales-objection-negotiation`, `sales-closing-execution`
- [`passport-lookup`](../../../tools/contracts/passport-lookup.md)

## Sources

- Neil Rackham, *SPIN Selling* (1988), for need-payoff questions and the finding that benefit statements work differently in large sales: <https://www.huthwaiteinternational.com/spin-methodology>.
- Robert Cialdini, *Influence* (1984; expanded editions), for social proof and authority — used only with verified, permitted evidence. Cialdini's own site emphasizes ethical use: <https://www.influenceatwork.com/7-principles-of-persuasion/>.
- Matthew Dixon and Brent Adamson, *The Challenger Sale* (2011), for the practitioner framework "Teach, Tailor, Take Control" and constructive tension; see Challenger's current description at <https://challengerinc.com/what-is-challenger-sales-methodology/>. This is a framework for complex B2B conversations, not proof of universal superiority.
- Gartner's B2B buying research on stakeholder-specific relevance and consensus: <https://www.gartner.com/en/newsroom/press-releases/2025-05-07-gartner-sales-survey-finds-74-percent-of-b2b-buyer-teams-demonstrate-unhealthy-conflict-during-the-decision-process>.
- Research on retrieval-augmented generation's limits: Wu, Wu, and Zou, "ClashEval: Quantifying the tug-of-war between an LLM's internal prior and external evidence" (2024), <https://arxiv.org/abs/2404.10198>. The finding that models may adopt incorrect retrieved content is why the passport marks fact status and why the agent must not "fill gaps" from memory.
- The evidence hierarchy and ROI template are original repository design choices, not a published framework.

See [`research/claim-evidence-matrix.md`](../../../research/claim-evidence-matrix.md) for evidence grades and the limits of each source.
