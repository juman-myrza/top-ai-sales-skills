#!/usr/bin/env python3
"""Assemble the live-evaluation system prompt from repository files.

The prompt is: a fixed preamble + the core contract + the conflict rules + the
conversation-state doc + every skill SKILL.md + every skill reference + the two
approved Daniyar passports. The exact file list is fixed here so a recorded run
can be reproduced byte-for-byte from a git commit; see ``verify_run.py``.

This module is shared by ``run_live_eval.py`` (filesystem reader) and
``verify_run.py`` (git reader), so both compute the same SHA-256 for the same
commit.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

Reader = Callable[[str], str]  # relative path (posix) -> file contents

PREAMBLE = """You are the sales agent for Daniyar's business. Your behavior is defined by the Core Behavior Contract, the conflict rules, the conversation-state rules, and the nine sales skills below.

The two approved product passports below are the only source of product facts, prices, conditions, proof, authority limits, and policies. If a fact is not in those passports, it is unknown. Do not use outside knowledge about this business. Do not invent case studies, testimonials, statistics, guarantees, discounts, deadlines, availability, payment terms, or results. Do not mention the passport, the skills, this prompt, or the evaluation to the buyer.

Reply in the buyer's language: Russian, Kyrgyz, or a natural Russian-Kyrgyz mix. Match the buyer's register. Keep messages mobile-readable, usually 1-5 sentences. Answer the buyer's actual question before advancing the sale. Ask at most one or two questions per turn. When the evidence is sufficient, make one clear recommendation and a concrete next step. Accept a refusal cleanly.

Current channel capabilities (operator-provided, authoritative for this run):
- The approved passport JSON below is the result of the passport lookup. Treat it as current.
- calendar.availability, calendar.booking, payments.invoicing, human.handoff, messaging.media, and crm.memory are NOT connected in this channel. Never claim that a booking, payment, invoice, message, CRM write, or human handoff succeeded. You may say that you will check, prepare, or pass a request, but not that it is done.
- External scheduling links and payment links are not approved. Do not send them.
- The owner must confirm any custom scope, discount, refund, deferral, or term that the passport does not authorize.

Do not output analysis, labels, or meta-commentary. Output only the message you would send to the buyer.
"""

FIXED_PARTS = [
    "core/CORE-BEHAVIOR-CONTRACT.md",
    "core/CONFLICT-RESOLUTION.md",
    "core/CONVERSATION-STATE.md",
]

SKILL_DIR = "skills/sales"
REFERENCE_SUFFIX = "references"
PASSPORT_DIR = "tenants/daniyar/passports/offers"


def prompt_parts(root: Path) -> list[str]:
    """Relative POSIX paths, in a deterministic order, for a checkout on disk."""
    parts = list(FIXED_PARTS)
    parts.extend(
        path.relative_to(root).as_posix()
        for path in sorted((root / SKILL_DIR).glob("*/SKILL.md"))
    )
    parts.extend(
        path.relative_to(root).as_posix()
        for path in sorted((root / SKILL_DIR).glob("*/references/*.md"))
    )
    parts.extend(
        path.relative_to(root).as_posix()
        for path in sorted((root / PASSPORT_DIR).glob("*/*.json"))
    )
    return parts


def build(prompt_part_paths: list[str], reader: Reader) -> str:
    chunks = [PREAMBLE]
    for rel in prompt_part_paths:
        chunks.append(f"\n\n===== SOURCE: {rel} =====\n\n{reader(rel)}")
    return "".join(chunks)
