# Attribution and Third-Party Material

This repository is original work released under the [MIT License](LICENSE). It paraphrases ideas from published sales research and practitioner frameworks; it does not reproduce substantial portions of those works, and it does not include third-party code.

## Sales and negotiation frameworks

The skills use vocabulary and question patterns adapted from:

- Neil Rackham, *SPIN Selling* (1988) — situation, problem, implication, need-payoff, commitment.
- Matthew Dixon and Brent Adamson, *The Challenger Sale* (2011) — insight-led teaching and buying-group consensus.
- Chris Voss, *Never Split the Difference* (2016) — labels, mirrors, calibrated questions, used as optional clarification tools.
- Sandler Systems, the Sandler Selling System — up-front contract, pain, budget, decision process, post-sell.
- Robert Cialdini, *Influence* (1984; revised 2021) — influence principles, bounded by truthfulness.
- Jim Camp, *Start with No* (2002) — permission to say no and decision clarity.
- Keenan, *Gap Selling* (2018) — current state, problem, impact, future state.
- MEDDIC / MEDDPICC — qualification checklist vocabulary.
- Roger Fisher and William Ury, *Getting to Yes* (1981; revised 2011) — interests, positions, BATNA.

These are summaries and adaptations, not endorsements by the authors or publishers. Book titles remain the property of their respective rights holders. The source register records editions, evidence grades, and limitations: [`research/source-register.md`](research/source-register.md).

Jordan Belfort's *Way of the Wolf* is listed in the source register only as an explicit **exclusion** for integrity reasons. No tactic from it is used.

## Standards and software

- **Hermes Agent** — skill discovery format and loading behavior were verified against a local installation, v0.21.5+7537.ga036b13. Hermes is separate software and is not distributed with this repository.
- **Agent Skills specification** — the `SKILL.md` concept, `name`/`description` frontmatter, progressive disclosure, and `references/` layout follow the open Agent Skills specification. Hermes imposes a tighter 60-character description limit, which this repository follows.
- **`skills-ref`** — the reference validator linked from the Agent Skills project informed the validation approach. It is not bundled and was not run here.
- **PyYAML** and **jsonschema** — development dependencies, used under their respective licenses.

## Research and regulatory material

- **Gartner** — the 2025 press release on unhealthy conflict in B2B buying teams is cited as vendor research, with sample size and limitations. The related "B2B Buying Journey" page returned HTTP 403 and is not load-bearing.
- **U.S. Federal Trade Commission** — the *Guides Concerning the Use of Endorsements and Testimonials in Advertising* (16 CFR Part 255) informed the prohibition on fabricated proof and undisclosed endorsements. This is U.S. guidance, not legal advice for any other jurisdiction.
- **Huthwaite International**, **Sandler Systems**, **Gap Selling / Sales Growth**, and **Influence at Work** — official vendor descriptions were used to represent the frameworks accurately. They are commercially interested sources and are not treated as independent proof.

## Open-source repositories reviewed

The following repositories were reviewed for prior art and gap analysis only. No code, prompts, or text were copied:

- [`louisblythe/Sales-Skills`](https://github.com/louisblythe/Sales-Skills)
- [`aixier/top_ai_sales`](https://github.com/aixier/top_ai_sales)
- [`TheCraigHewitt/sales-skills`](https://github.com/TheCraigHewitt/sales-skills)

The audit is in [`research/open-source-audit.md`](research/open-source-audit.md). Repository licenses were checked at the README/metadata level on 2026-10-23; re-verify before reusing anything from them.

## Fictional examples

All names, brands, domains (`.example.invalid`), prices, case studies, calendars, and customer details in `product-passport/examples/` are fictional. They exist to demonstrate the passport format and must not be presented as real offers or proof.

## No endorsement

No author, publisher, vendor, standards body, or open-source maintainer listed here has endorsed this repository or its results. Any errors of interpretation are the responsibility of this project.
