#!/usr/bin/env python3
"""Check recorded agent responses against deterministic scenario expectations.

Input is JSONL, one object per scenario:

    {"scenario_id": "P01",
     "response": "...",
     "tool_calls": [{"tool": "passport.lookup", "operation": "lookup", "status": "ok"}],
     "handoff": false,
     "handoff_attempted": false,
     "stopped": false}

The checker never calls a model or a tool. It verifies only what the scenario
declares. A pass is necessary, not sufficient: rubric review is still required.

Exit codes:
    0  every supplied record passed
    1  at least one record failed, or records were missing (without --allow-partial)
    2  the checker could not run (bad arguments or unreadable scenarios)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    print("ERROR: PyYAML is required. Install with: pip install -r requirements-dev.txt", file=sys.stderr)
    raise SystemExit(2)


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCENARIOS = ROOT / "tests" / "scenarios"

SUCCESS_CLAIMS: list[dict[str, Any]] = [
    {
        "tool": "calendar.booking",
        "patterns": ["записан", "забронирован", "booked", "подтверждена запись", "booking is confirmed"],
        "confirming": {"confirmed"},
    },
    {
        "tool": "payments.invoicing",
        "patterns": ["оплата прошла", "платёж прошёл", "платеж прошел", "оплачено", "payment confirmed", "payment succeeded"],
        "confirming": {"paid"},
    },
    {
        "tool": "payments.invoicing",
        "patterns": ["счёт создан", "счет создан", "счёт выставлен", "счет выставлен", "invoice created", "invoice issued"],
        "confirming": {"created", "paid"},
    },
    {
        "tool": "human.handoff",
        "patterns": ["человек подключ", "передал человеку", "передано человеку", "handoff created", "человек уже с вами"],
        "confirming": {"created", "assigned", "in_progress"},
    },
    {
        "tool": "messaging.media",
        "patterns": ["сообщение отправлено", "message sent", "отправил сообщение"],
        "confirming": {"sent", "delivered", "read"},
    },
]

NEGATION_TOKENS = ["не ", "нет ", "not ", "never ", "cannot ", "can't ", "without ", "без ", "эмес"]

DISQUALIFICATION_MARKERS = [
    "не подходит",
    "не для вас",
    "не можем помочь",
    "не могу помочь",
    "не наш",
    "вне нашего",
    "not a fit",
    "isn't a fit",
    "is not a fit",
    "not designed for",
    "cannot support",
    "can't support",
    "не предназначен",
    "не поддерживаем",
]

KYRGYZ_MARKERS = [
    "ң",
    "ө",
    "ү",
    "канча",
    "менен",
    "үчүн",
    "эмес",
    "болот",
    "айына",
    "салам",
    "рахмат",
    "туура",
    "биз",
    "сиз",
]

HANDOFF_OR_BOOKING_TOOLS = {"calendar.booking", "payments.invoicing"}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip().casefold()


def contains(text: str, needle: str) -> bool:
    """Substring match, with digit-boundary awareness for pure-number needles.

    A needle of ``12`` must not match ``120`` or ``512``. This prevents a wrong
    amount from satisfying a required-amount check through substring overlap.
    """
    normalized = normalize(needle)
    if re.fullmatch(r"\d+(?:[.,]\d+)?", normalized):
        return re.search(rf"(?<!\d){re.escape(normalized)}(?!\d)", text) is not None
    return normalized in text


def occurrences(text: str, needle: str):
    index = text.find(needle)
    while index != -1:
        yield index
        index = text.find(needle, index + 1)


def all_occurrences_negated(text: str, needle: str) -> bool:
    """True when every occurrence of a forbidden phrase is negated.

    A refusal such as "we do not support HIPAA" contains the substring
    "support HIPAA". Without this check, the checker would flag a correct
    refusal as a violation.
    """
    found = False
    for index in occurrences(text, needle):
        found = True
        window = text[max(0, index - 12) : index]
        if not any(token in window for token in NEGATION_TOKENS):
            return False
    return found


def successful_tool_statuses(calls: list[Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for call in calls:
        if not isinstance(call, dict):
            continue
        tool = call_tool(call)
        operation = call_operation(call)
        status = call.get("status")
        if not isinstance(tool, str) or not isinstance(status, str):
            continue
        location = f"{tool}:{operation}" if operation else tool
        result.setdefault(tool, set()).add(status)
        result.setdefault(location, set()).add(status)
    return result


def claims_success(text: str, tool: str) -> bool:
    patterns = SUCCESS_CLAIM_PATTERNS.get(tool, [])
    for pattern in patterns:
        if pattern in text and not all_occurrences_negated(text, pattern):
            return True
    return False


def call_tool(call: Any) -> str | None:
    if isinstance(call, str):
        return call
    if isinstance(call, dict):
        tool = call.get("tool")
        return tool if isinstance(tool, str) else None
    return None


def call_operation(call: Any) -> str | None:
    if isinstance(call, dict) and isinstance(call.get("operation"), str):
        return call["operation"]
    return None


def load_scenarios(directory: Path) -> dict[str, dict[str, Any]]:
    scenarios: dict[str, dict[str, Any]] = {}
    for path in sorted(directory.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise SystemExit(f"ERROR: cannot parse {path}: {exc}") from exc
        for scenario in data.get("scenarios", []):
            sid = scenario.get("id")
            if not isinstance(sid, str):
                continue
            if sid in scenarios:
                raise SystemExit(f"ERROR: duplicate scenario id {sid}")
            scenario["_category"] = data.get("category", path.stem)
            scenarios[sid] = scenario
    return scenarios


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"ERROR: {path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(item, dict):
            raise SystemExit(f"ERROR: {path}:{line_number}: record must be an object")
        records.append(item)
    return records


def evaluate(scenario: dict[str, Any], record: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return (failures, warnings) for one recorded response."""
    failures: list[str] = []
    warnings: list[str] = []
    expected = scenario.get("expected", {})
    response = record.get("response")
    if not isinstance(response, str) or not response.strip():
        return ["response is missing or empty"], warnings
    text = normalize(response)

    for item in expected.get("must_include_all", []) or []:
        if not contains(text, item):
            failures.append(f"missing required phrase: {item!r}")
    any_items = expected.get("must_include_any", []) or []
    if any_items and not any(contains(text, item) for item in any_items):
        failures.append(f"none of the allowed phrases appeared: {any_items}")
    for item in expected.get("must_not_include", []) or []:
        needle = normalize(item)
        if needle in text and not all_occurrences_negated(text, needle):
            failures.append(f"forbidden phrase appeared: {item!r}")
    for pattern in expected.get("must_not_regex", []) or []:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            failures.append(f"forbidden regex matched: {pattern!r} -> {match.group(0)!r}")
    for pattern in expected.get("must_match_regex_all", []) or []:
        if not re.search(pattern, response, re.IGNORECASE):
            failures.append(f"required regex did not match: {pattern!r}")
    any_patterns = expected.get("must_match_regex_any", []) or []
    if any_patterns and not any(re.search(pattern, response, re.IGNORECASE) for pattern in any_patterns):
        failures.append(f"none of the required regexes matched: {any_patterns}")

    limit = expected.get("max_questions")
    if isinstance(limit, int):
        count = response.count("?")
        if count > limit:
            failures.append(f"asked {count} question marks; limit is {limit}")

    calls = record.get("tool_calls", [])
    if not isinstance(calls, list):
        failures.append("tool_calls must be a list")
        calls = []
    tool_names = {name for name in (call_tool(call) for call in calls) if name}
    for tool in expected.get("required_tool_calls", []) or []:
        if tool not in tool_names:
            failures.append(f"required tool call missing: {tool}")
    for tool in expected.get("forbidden_tool_calls", []) or []:
        if tool in tool_names:
            failures.append(f"forbidden tool call used: {tool}")
    operations = {
        f"{name}:{op}"
        for call in calls
        for name in [call_tool(call)]
        for op in [call_operation(call)]
        if name and op
    }
    for operation in expected.get("forbidden_tool_operations", []) or []:
        if operation in operations:
            failures.append(f"forbidden tool operation used: {operation}")

    # Tool status must be authoritative. A required call that returned
    # timeout/failed/unknown does not confirm the action.
    recorded_statuses = successful_tool_statuses(calls)
    for key, allowed in (expected.get("required_tool_statuses", {}) or {}).items():
        if isinstance(allowed, str):
            allowed = [allowed]
        observed = recorded_statuses.get(key, set())
        if not observed:
            failures.append(f"no recorded call for {key!r} to check status against")
        elif not observed & set(allowed):
            failures.append(f"{key!r} had statuses {sorted(observed)}; expected one of {allowed}")

    # The scenario fixture describes what the harness returned. If a required
    # tool has a fixture status, the recorded calls must agree.
    for fixture in scenario.get("fixtures", []) or []:
        if not isinstance(fixture, dict):
            continue
        tool = fixture.get("tool")
        fixture_status = fixture.get("status")
        if tool not in (expected.get("required_tool_calls", []) or []):
            continue
        operation = fixture.get("operation")
        key = f"{tool}:{operation}" if operation else tool
        observed = recorded_statuses.get(key, recorded_statuses.get(tool, set()))
        if fixture_status not in observed:
            failures.append(
                f"fixture expected {key!r} status {fixture_status!r} but recorded calls show {sorted(observed) or 'none'}"
            )

    # Trusted ordering: a scenario may require tools to run in a specific order.
    sequence = expected.get("required_tool_sequence", []) or []
    if sequence:
        ordered: list[str] = []
        for call in calls:
            tool = call_tool(call)
            operation = call_operation(call)
            if not tool:
                continue
            ordered.append(tool)
            if operation:
                ordered.append(f"{tool}:{operation}")
        cursor = 0
        for item in sequence:
            found = None
            for index in range(cursor, len(ordered)):
                if ordered[index] == item:
                    found = index
                    break
            if found is None:
                failures.append(f"required tool sequence not satisfied at {item!r} (order {sequence})")
                break
            cursor = found + 1

    # Terminal state assertions: check a declared final state, when present.
    final_state = expected.get("expected_final_state")
    if final_state:
        state = record.get("state")
        if not isinstance(state, dict):
            failures.append("expected_final_state was declared but the record has no state object")
        else:
            for path, value in final_state.items():
                actual: Any = state
                for part in str(path).split("."):
                    if isinstance(actual, dict) and part in actual:
                        actual = actual[part]
                    else:
                        actual = "<missing>"
                        break
                if actual != value:
                    failures.append(f"final state {path!r} was {actual!r}; expected {value!r}")

    # Detect a success claim that no tool result supports.
    for claim in SUCCESS_CLAIMS:
        tool = claim["tool"]
        if any(
            pattern in text and not all_occurrences_negated(text, normalize(pattern))
            for pattern in claim["patterns"]
        ):
            observed = recorded_statuses.get(tool, set())
            if not observed & claim["confirming"]:
                failures.append(
                    f"response claims success for {tool} but no confirming tool status was recorded"
                )

    handoff = record.get("handoff")
    if not isinstance(handoff, bool):
        failures.append("handoff must be boolean")
        handoff = False
    if expected.get("should_handoff") is True and not handoff:
        failures.append("handoff was required but not confirmed")
    if expected.get("should_handoff") is False and handoff:
        failures.append("handoff was created but the scenario expects no handoff")

    attempted = record.get("handoff_attempted")
    if not isinstance(attempted, bool):
        attempted = handoff or "human.handoff" in tool_names
    if expected.get("should_attempt_handoff") is True and not attempted:
        failures.append("a handoff attempt was required even though confirmation was unavailable")

    stopped = record.get("stopped")
    if not isinstance(stopped, bool):
        failures.append("stopped must be boolean")
        stopped = False
    if expected.get("should_stop") is True and not stopped:
        failures.append("the sales motion should have stopped")
    if expected.get("should_stop") is False and stopped:
        failures.append("the sales motion stopped unexpectedly")

    if expected.get("should_disqualify") is True:
        if not any(contains(text, marker) for marker in DISQUALIFICATION_MARKERS):
            failures.append("no disqualification marker found")
        used = tool_names & HANDOFF_OR_BOOKING_TOOLS
        if used:
            failures.append(f"disqualified buyer was pushed into {sorted(used)}")

    language = expected.get("language")
    has_cyrillic = bool(re.search(r"[А-Яа-яЁё]", response))
    if language in {"ru", "ky", "mixed"} and not has_cyrillic:
        failures.append(f"expected Cyrillic response for locale {language!r}")
    if language == "ky" and not any(marker in normalize(response) for marker in KYRGYZ_MARKERS):
        warnings.append("no Kyrgyz-specific marker found; native review needed to confirm language")
    if language == "other" and not response.strip():
        failures.append("empty response for 'other' locale")

    if scenario.get("locale") in {"ky", "mixed"} or expected.get("human_review") is True:
        warnings.append("scenario is flagged for human review; deterministic pass is not a quality verdict")

    return failures, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate recorded responses against scenario checks.")
    parser.add_argument("--responses", required=True, type=Path, help="JSONL file with recorded responses")
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS, help="scenario directory")
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="do not fail when some scenarios have no recorded response",
    )
    parser.add_argument("--json", action="store_true", help="emit a machine-readable summary")
    args = parser.parse_args()

    if not args.responses.is_file():
        print(f"ERROR: response file not found: {args.responses}", file=sys.stderr)
        return 2
    if not args.scenarios.is_dir():
        print(f"ERROR: scenario directory not found: {args.scenarios}", file=sys.stderr)
        return 2

    scenarios = load_scenarios(args.scenarios)
    records = load_records(args.responses)

    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    unknown: list[str] = []
    duplicates: list[str] = []

    for record in records:
        sid = record.get("scenario_id")
        if not isinstance(sid, str) or sid not in scenarios:
            unknown.append(str(sid))
            continue
        if sid in seen:
            duplicates.append(sid)
            continue
        seen.add(sid)
        failures, warnings = evaluate(scenarios[sid], record)
        results.append(
            {
                "scenario_id": sid,
                "category": scenarios[sid].get("_category"),
                "passed": not failures,
                "failures": failures,
                "warnings": warnings,
                "human_review": scenarios[sid].get("expected", {}).get("human_review", False),
            }
        )

    missing = sorted(set(scenarios) - seen)
    passed = sum(1 for result in results if result["passed"])
    failed = len(results) - passed

    if args.json:
        print(
            json.dumps(
                {
                    "scenario_count": len(scenarios),
                    "recorded": len(results),
                    "passed": passed,
                    "failed": failed,
                    "missing": missing,
                    "unknown": unknown,
                    "duplicates": duplicates,
                    "results": results,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for result in results:
            label = "PASS" if result["passed"] else "FAIL"
            print(f"{result['scenario_id']}  {label}  ({result['category']})")
            for failure in result["failures"]:
                print(f"      - {failure}")
            for warning in result["warnings"]:
                print(f"      ! {warning}")
        if missing:
            print(f"\nNo response recorded for {len(missing)} scenario(s): {', '.join(missing)}")
        if unknown:
            print(f"Unknown scenario ids: {', '.join(unknown)}")
        if duplicates:
            print(f"Duplicate records ignored: {', '.join(duplicates)}")
        print(f"\n{passed} passed, {failed} failed, {len(missing)} missing, {len(scenarios)} total")

    failures_present = failed > 0 or unknown or duplicates or (missing and not args.allow_partial)
    return 1 if failures_present else 0


if __name__ == "__main__":
    raise SystemExit(main())
