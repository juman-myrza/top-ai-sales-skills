# Open-Source Audit

**Date:** 2026-10-23  
**Method:** README, repository metadata, and file-tree inspection through the GitHub API. This is a **README-level and structure-level audit**, not a line-by-line code review, security audit, or behavioral evaluation. No code, text, or scenario was copied into this repository.

**Why audit these repositories?**

They are prior art for "sales skills for AI agents." The goal was to learn what already exists, what is missing, and which patterns are unsafe to copy. A popular repository is not evidence that its advice works.

---

## 1. Summary

| Repository | Scope | License | What it does well | What this repository does differently |
|---|---|---|---|---|
| [`louisblythe/Sales-Skills`](https://github.com/louisblythe/Sales-Skills) | 122 skills: core sales, strategy, AI-SDR/bot | MIT per README (fork; GitHub API shows no license on the fork) | Breadth; names the operational gaps (handoff, timezone, compliance, memory); simple `SKILL.md` structure | Adds a strict passport boundary, tool-confirmation rules, failure semantics, a scenario corpus, and a multilingual focus |
| [`aixier/top_ai_sales`](https://github.com/aixier/top_ai_sales) | Chinese AI sales assistant concept | MIT | Modular skill idea; CRM/knowledge-base ambition; explicit privacy intent | Rejects unverifiable success-rate claims; provides runnable validation and explicit "not implemented" boundaries |
| [`TheCraigHewitt/sales-skills`](https://github.com/TheCraigHewitt/sales-skills) | 21 B2B lifecycle skills | MIT | Clear lifecycle coverage; shared `sales-context`; validator script; practical tone | Separates facts from instructions; adds machine-readable passport, tool contracts, and 57 test scenarios |

---

## 2. `louisblythe/Sales-Skills`

### What it is

- A fork of `coreyhaines31/marketingskills`, adapted for sales.
- The README lists **122 skills** in three groups:
  - 20 core sales skills (discovery, objections, negotiation, closing, empathy, etc.);
  - 22 sales process and strategy skills (pipeline, forecasting, pricing, enablement);
  - 80 AI-SDR/bot skills (handoff detection, intent, memory, timezone, compliance, deliverability, etc.).
- Each skill is a directory with a `SKILL.md`; the README shows the minimal `name` + `description` frontmatter.
- The README claims MIT licensing. The GitHub API reports `license: null` on the fork, while the parent repository is MIT. A reuser should verify the license file and upstream attribution before copying.

### Strengths

1. **Coverage map.** The AI-SDR section names real operational concerns: handoff, timezone awareness, opt-out/compliance, duplicate prevention, response latency, and conversation memory.
2. **Low ceremony.** A skill is a Markdown file, which makes the collection easy to browse and adapt.
3. **Explicit methodology list.** SPIN, MEDDIC, SPICED, Challenger, Gap Selling, and BANT are named, so a reader can see the lineage.

### Weaknesses relevant to this project

1. **No fact boundary.** Product, pricing, and proof facts are not separated from instructions. A skill can drift into generic claims or invite the model to improvise.
2. **Some tactics need guardrails.** The collection includes skills for scarcity/urgency calibration, micro-commitment stacking, emotional-arc management, and "response latency management." These can be legitimate, but they can also become manufactured urgency, pressure, or fake delays without explicit prohibitions.
3. **Breadth over verification.** The README does not present a scenario corpus, a model evaluation, or adapter contract tests. The presence of a skill is not evidence that it works.
4. **Fork maintenance.** A 122-skill fork with no visible test suite is expensive to keep coherent; cross-skill conflicts are likely.
5. **License ambiguity.** The fork's API metadata does not show a license even though the README says MIT. Verify before reuse.

### What was borrowed

- The idea of splitting sales into lifecycle skills.
- The list of operational concerns worth covering (handoff, memory, timezone, compliance).
- The minimal `SKILL.md` format.

### What was deliberately not copied

- The 122-skill taxonomy (too broad for a coherent, testable agent).
- Any scarcity/urgency/latency skill without a truthfulness gate.
- Any text, prompt, or scenario.

---

## 3. `aixier/top_ai_sales`

### What it is

- A Chinese-language "AI Sales Brain" concept: natural-language sales assistance, meeting prep, objection handling, customer analysis, daily planning, and a "self-evolving" knowledge base.
- The repository is small: a long `CLAUDE.md`, a specification, empty `data/`, `output/`, and `templates/` directories, and one commit at the time of review. The README says dependencies and `main.py` are "coming soon."
- MIT licensed.

### Strengths

1. **Workflow framing.** It imagines a sales assistant embedded in a daily workflow, not just a copy generator.
2. **Knowledge-base ambition.** Customer profiles, objection history, and conversation logs are the right raw material for memory.
3. **Privacy intent.** The README says customer data is stored locally by default and API keys live in environment variables.

### Weaknesses relevant to this project

1. **Unverifiable performance claims.** The README shows objection responses "ranked by success rate" (e.g., 85%, 68%, 60%) without a dataset, sample size, or method. Those numbers should not be treated as evidence.
2. **Not runnable as published.** The quick start is entirely commented out; the main program and dependencies are marked "coming soon." It is a concept/specification, not a working assistant.
3. **Self-evolution without evaluation.** "Auto-learning" and "dynamic skill development" are claimed without a feedback-quality, poisoning, or regression strategy.
4. **Localization.** The implementation and examples are Chinese; the patterns are interesting, but the content is not reusable for Russian/Kyrgyz without a new design.
5. **Empty structure.** Many directories contain only `.gitkeep`; the README describes more capability than the tree contains.

### What was borrowed

- The idea of a modular skill system with a persistent knowledge base.
- The emphasis on meeting prep, objection history, and daily workflow.

### What was deliberately not copied

- Any success-rate percentage.
- The "self-evolving" claim.
- The Chinese prompts or specification text.

---

## 4. `TheCraigHewitt/sales-skills`

### What it is

- **21 B2B sales skills** covering foundation, prospecting, deal execution, close, intelligence, and sales ops.
- MIT licensed. The README says the repository has moved to a unified `TheCraigHewitt/skills` repository.
- Includes a shared `sales-context` skill that creates `.agents/sales-context.md` (ICP, value prop, sales motion, proof points) read by the other skills.
- Includes `validate-skills.sh` and a CI workflow.
- Skills are large: the file tree shows many `SKILL.md` files around 20–28 KB, close to or above the 24,000-character soft budget used by this repository's Hermes target.

### Strengths

1. **Lifecycle clarity.** The 21 skills map cleanly to a B2B sales process, with foundation skills feeding the rest.
2. **Shared context.** `sales-context` is a practical precursor to a product passport: write the business facts once, read them everywhere.
3. **Practical tone.** The README favors plain text, short messages, and one ask; it explicitly dislikes generic AI sales copy.
4. **Validation habit.** A validator script and CI workflow signal maintenance intent.

### Weaknesses relevant to this project

1. **Context file is not a controlled fact model.** `sales-context.md` is prose. It has no schema, fact status, approval gate, expiry, or authority limits. A model can still quote stale or unapproved claims.
2. **No tool-confirmation contract.** The skills are mostly content-generation and deal-review oriented; they do not define what happens when a calendar, payment, CRM, or handoff tool fails.
3. **No scenario corpus.** The validator checks skill structure, not agent behavior against buyer conversations.
4. **Large skill bodies.** Many files are near the point where progressive disclosure is needed; loading several at once consumes context.
5. **Illustrative numbers.** The README's example includes a product claim ("increases close rates by 23%") for a hypothetical offer. It is clearly an example, but a real deployment must not inherit it as a fact.

### What was borrowed

- The lifecycle decomposition and the "shared context first" idea.
- The emphasis on short, plain-text sales communication.
- The idea of a structural validator and CI.

### What was deliberately not copied

- The prose-only context file (replaced by a JSON schema + approval gate).
- The 21-skill taxonomy (replaced by nine decision-oriented skills).
- The example product claims.
- Any skill text.

---

## 5. Gap analysis

| Need | Typical open-source coverage | This repository |
|---|---|---|
| Product facts separated from instructions | Rare; usually inline prose or a context file | JSON/Markdown passport with `verified` / `estimated` / `unknown`, schema, approval checklist |
| Tool failure behavior | Often absent or optimistic | Seven contracts with status vocabulary, retries, idempotency, and failure matrices |
| False success prevention | Rare | Core rule: no completion claim without a confirming result; scenarios T01–T06 |
| Direct purchase vs. booking | Usually meeting-first | Both paths; no forced meeting; passport decides fulfillment |
| In-chat booking | Often a Calendly link | Availability → consent → booking → confirmation, with conflict/timeout scenarios |
| Russian/Kyrgyz/mixed | Rare | Dedicated skill, phrasebook, scenarios, native-review flag |
| Integrity and refusal | Mixed; some collections include pressure tactics | Hard fails for fabrication, fake identity/scarcity, privacy, minors, fraud |
| Test corpus | Usually none | 57 scenarios, deterministic checker, checker regression tests, rubric, coverage map |
| Honest implementation status | Often implied working integrations | Every example binding says `not_implemented`; contracts are specifications |
| License and attribution | Varies | MIT for original code/text; sources attributed; no copied skill text |

---

## 6. What this audit does not establish

- It does not establish that the other repositories are unsafe or ineffective. They were reviewed at the README/tree level.
- It does not establish that this repository is better. It has not been run against a model or real buyers.
- It does not establish license compatibility for every file in the other repositories. A reuser must inspect the actual license and file history.
- Star counts and repository contents change. The observations are a snapshot.

The useful conclusion is narrow: **there is a lot of sales-skill content, but very little of it separates facts from instructions, defines tool-failure behavior, or ships a testable evaluation corpus.** That gap is the reason for this repository.
