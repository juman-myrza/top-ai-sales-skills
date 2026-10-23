#!/usr/bin/env python3
"""Render the scenario corpus for reviewers or a test harness.

The corpus is YAML for machines. This script produces either:

* a Markdown review packet grouped by category, or
* JSONL prompts for a harness that will record agent responses.

Expected checks are omitted from JSONL by default so they cannot leak into the
prompt. Use --include-expected only for offline analysis.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    print("ERROR: PyYAML is required. Install with: pip install -r requirements-dev.txt", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCENARIOS = ROOT / "tests" / "scenarios"


def load_corpus(directory: Path) -> list[dict[str, Any]]:
    corpus: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise SystemExit(f"ERROR: cannot parse {path}: {exc}") from exc
        category = data.get("category", path.stem)
        for scenario in data.get("scenarios", []):
            item = dict(scenario)
            item["_category"] = category
            item["_file"] = path.name
            corpus.append(item)
    return corpus


def markdown(corpus: list[dict[str, Any]]) -> str:
    lines = [
        "# Scenario Review Packet",
        "",
        "Generated from `tests/scenarios/` by `scripts/render_scenarios.py`.",
        "This is the written corpus, not a test run. No model or tool has been called.",
        "",
        f"**Scenarios:** {len(corpus)}",
        "",
    ]

    categories: dict[str, list[dict[str, Any]]] = {}
    for scenario in corpus:
        categories.setdefault(scenario["_category"], []).append(scenario)

    lines.append("## Contents")
    lines.append("")
    for category, items in categories.items():
        lines.append(f"- {category} ({len(items)})")
    lines.append("")

    for category, items in categories.items():
        lines.append(f"## {category}")
        lines.append("")
        for scenario in items:
            context = scenario.get("context", {})
            expected = scenario.get("expected", {})
            lines.append(f"### {scenario['id']} — {scenario['title']}")
            lines.append("")
            lines.append(
                f"- **Difficulty:** {scenario.get('difficulty')}  "
                f"**Locale:** `{scenario.get('locale')}`  "
                f"**Passport:** `{scenario.get('passport')}`  "
                f"**Stage:** `{context.get('stage')}`"
            )
            if scenario.get("tags"):
                lines.append(f"- **Tags:** {', '.join(f'`{tag}`' for tag in scenario['tags'])}")
            if context.get("known_facts"):
                facts = json.dumps(context["known_facts"], ensure_ascii=False, sort_keys=True)
                lines.append(f"- **Known facts:** `{facts}`")
            if context.get("consent"):
                consent = json.dumps(context["consent"], ensure_ascii=False, sort_keys=True)
                lines.append(f"- **Consent:** `{consent}`")
            lines.append("")
            lines.append("**Turns**")
            lines.append("")
            for index, turn in enumerate(scenario.get("turns", []), start=1):
                role = "Buyer" if turn.get("role") == "buyer" else "Event"
                text = str(turn.get("text", "")).replace("\n", " ")
                lines.append(f"{index}. **{role}:** {text}")
            lines.append("")

            fixtures = scenario.get("fixtures", [])
            if fixtures:
                lines.append("**Fixtures**")
                lines.append("")
                for fixture in fixtures:
                    operation = f" / {fixture['operation']}" if fixture.get("operation") else ""
                    note = f" — {fixture['note']}" if fixture.get("note") else ""
                    lines.append(
                        f"- `{fixture.get('tool')}`{operation}: **{fixture.get('status')}**{note}"
                    )
                lines.append("")

            lines.append("**Deterministic checks**")
            lines.append("")
            lines.append(f"- Language: `{expected.get('language')}`")
            lines.append(f"- Max question marks: `{expected.get('max_questions')}`")
            if expected.get("must_include_all"):
                lines.append(f"- Must include all: {', '.join(repr(x) for x in expected['must_include_all'])}")
            if expected.get("must_include_any"):
                lines.append(f"- Must include any: {', '.join(repr(x) for x in expected['must_include_any'])}")
            if expected.get("must_not_include"):
                lines.append(f"- Must not include: {', '.join(repr(x) for x in expected['must_not_include'])}")
            if expected.get("must_not_regex"):
                lines.append(f"- Must not match: {', '.join(repr(x) for x in expected['must_not_regex'])}")
            lines.append(
                f"- Required tools: {', '.join(f'`{x}`' for x in expected.get('required_tool_calls', [])) or '—'}"
            )
            lines.append(
                f"- Forbidden tools: {', '.join(f'`{x}`' for x in expected.get('forbidden_tool_calls', [])) or '—'}"
            )
            if expected.get("forbidden_tool_operations"):
                lines.append(
                    "- Forbidden operations: "
                    + ", ".join(f"`{x}`" for x in expected["forbidden_tool_operations"])
                )
            flags = [
                name.replace("should_", "")
                for name in ("should_handoff", "should_attempt_handoff", "should_stop", "should_disqualify")
                if expected.get(name)
            ]
            lines.append(f"- Expected flags: {', '.join(flags) or 'none'}")
            lines.append(f"- Human review: `{expected.get('human_review')}`")
            lines.append("")
            if scenario.get("rubric_focus"):
                lines.append("**Rubric focus:** " + ", ".join(f"`{x}`" for x in scenario["rubric_focus"]))
                lines.append("")
            if scenario.get("notes"):
                lines.append(f"**Why this exists:** {scenario['notes']}")
                lines.append("")
            lines.append("---")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def jsonl(corpus: list[dict[str, Any]], include_expected: bool) -> str:
    lines: list[str] = []
    for scenario in corpus:
        payload: dict[str, Any] = {
            "scenario_id": scenario["id"],
            "category": scenario["_category"],
            "title": scenario.get("title"),
            "difficulty": scenario.get("difficulty"),
            "locale": scenario.get("locale"),
            "passport": scenario.get("passport"),
            "context": scenario.get("context", {}),
            "turns": scenario.get("turns", []),
            "fixtures": scenario.get("fixtures", []),
            "rubric_focus": scenario.get("rubric_focus", []),
            "response_contract": {
                "scenario_id": scenario["id"],
                "response": "final agent message(s), concatenated",
                "tool_calls": [{"tool": "contract.tool", "operation": "operation", "status": "envelope status"}],
                "handoff": False,
                "handoff_attempted": False,
                "stopped": False,
            },
        }
        if include_expected:
            payload["expected"] = scenario.get("expected", {})
        lines.append(json.dumps(payload, ensure_ascii=False, sort_keys=False))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render scenarios as Markdown or JSONL.")
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS, help="scenario directory")
    parser.add_argument("--format", choices=("markdown", "jsonl"), default="markdown")
    parser.add_argument("--out", type=Path, help="write to a file instead of stdout")
    parser.add_argument(
        "--include-expected",
        action="store_true",
        help="include deterministic expectations in JSONL (offline analysis only)",
    )
    args = parser.parse_args()

    if not args.scenarios.is_dir():
        print(f"ERROR: scenario directory not found: {args.scenarios}", file=sys.stderr)
        return 2

    corpus = load_corpus(args.scenarios)
    if not corpus:
        print(f"ERROR: no scenarios found in {args.scenarios}", file=sys.stderr)
        return 2

    output = markdown(corpus) if args.format == "markdown" else jsonl(corpus, args.include_expected)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
        print(f"Wrote {len(corpus)} scenarios to {args.out}")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
