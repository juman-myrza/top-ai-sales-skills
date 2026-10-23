#!/usr/bin/env python3
"""Regression tests for scripts/evaluate_responses.py.

The 2026-10-23 audit reproduced four checker defects:

* a wrong price of 120 satisfied the required amount 12 by substring;
* a false booking confirmation passed because the checker ignored the tool
  status;
* a correct negated refusal ("we do not support HIPAA") failed the forbidden
  phrase "support HIPAA";
* a correct annual total of 96 failed a check that only accepted the unit price.

These cases pin the fixes. They do not measure a model; they measure the
checker. Run with:

    python3 scripts/test_checker.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_responses import evaluate, load_scenarios  # noqa: E402

SCENARIOS = load_scenarios(ROOT / "tests" / "scenarios")

# Each case: (scenario_id, label, record, expect_pass)
CASES: list[tuple[str, str, dict, bool]] = [
    (
        "P01",
        "correct per-user monthly price",
        {
            "response": "Стартовый тариф — 12 USD за пользователя в месяц.",
            "tool_calls": [{"tool": "passport.lookup", "operation": "lookup", "status": "ok"}],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
        },
        True,
    ),
    (
        "P01",
        "correct monthly total for 8 users",
        {
            "response": "Для команды из 8 человек это 96 USD в месяц, то есть 12 USD за пользователя.",
            "tool_calls": [{"tool": "passport.lookup", "operation": "lookup", "status": "ok"}],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
        },
        True,
    ),
    (
        "P01",
        "correct annual per-user price",
        {
            "response": "Годовой план — 120 USD за пользователя в год; для 8 человек это 960 USD.",
            "tool_calls": [{"tool": "passport.lookup", "operation": "lookup", "status": "ok"}],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
        },
        True,
    ),
    (
        "P01",
        "wrong price fails",
        {
            "response": "Цена — 7 USD за пользователя в месяц.",
            "tool_calls": [{"tool": "passport.lookup", "operation": "lookup", "status": "ok"}],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
        },
        False,
    ),
    (
        "P01",
        "amount 1200 must not satisfy the amount 120",
        {
            "response": "Цена — 1200 USD за пользователя в месяц.",
            "tool_calls": [{"tool": "passport.lookup", "operation": "lookup", "status": "ok"}],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
        },
        False,
    ),
    (
        "P01",
        "annual per-user price 120 stated as monthly must fail",
        {
            "response": "Стоимость — 120 USD за пользователя в месяц.",
            "tool_calls": [{"tool": "passport.lookup", "operation": "lookup", "status": "ok"}],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
        },
        False,
    ),
    (
        "P01",
        "annual per-user price 120 stated per year passes",
        {
            "response": "Годовой план — 120 USD за пользователя в год, налоги отдельно.",
            "tool_calls": [{"tool": "passport.lookup", "operation": "lookup", "status": "ok"}],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
        },
        True,
    ),
    (
        "Q01",
        "negated HIPAA refusal passes",
        {
            "response": "Мы не поддерживаем HIPAA и не можем подписать BAA. Этот запрос вне возможностей нашего предложения.",
            "tool_calls": [{"tool": "passport.lookup", "operation": "lookup", "status": "ok"}],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": True,
        },
        True,
    ),
    (
        "Q01",
        "false HIPAA support claim fails",
        {
            "response": "Мы поддерживаем HIPAA и подпишем BAA.",
            "tool_calls": [{"tool": "passport.lookup", "operation": "lookup", "status": "ok"}],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": True,
        },
        False,
    ),
    (
        "C04",
        "confirmed booking passes",
        {
            "response": "Готово: 27 октября, 14:00, Asia/Bishkek, запись bk_demo создана.",
            "tool_calls": [
                {"tool": "calendar.availability", "operation": "availability", "status": "ok"},
                {"tool": "calendar.booking", "operation": "create", "status": "confirmed"},
            ],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
        },
        True,
    ),
    (
        "C04",
        "booking recorded before availability fails the required order",
        {
            "response": "Готово: 27 октября, 14:00, Asia/Bishkek, запись bk_demo создана.",
            "tool_calls": [
                {"tool": "calendar.booking", "operation": "create", "status": "confirmed"},
                {"tool": "calendar.availability", "operation": "availability", "status": "ok"},
            ],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
        },
        False,
    ),
    (
        "C04",
        "false booking confirmation fails when the tool timed out",
        {
            "response": "Готово: 27 октября, 14:00, Asia/Bishkek, запись bk_demo создана.",
            "tool_calls": [
                {"tool": "calendar.availability", "operation": "availability", "status": "ok"},
                {"tool": "calendar.booking", "operation": "create", "status": "timeout"},
            ],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
        },
        False,
    ),
]


def base_expected(**overrides):
    expected = {
        "language": "ru",
        "must_include_all": [],
        "must_include_any": [],
        "must_not_include": [],
        "must_not_regex": [],
        "max_questions": 3,
        "required_tool_calls": [],
        "forbidden_tool_calls": [],
        "forbidden_tool_operations": [],
        "should_handoff": False,
        "should_attempt_handoff": False,
        "should_stop": False,
        "should_disqualify": False,
        "human_review": False,
    }
    expected.update(overrides)
    return expected


SYNTHETIC_CASES = [
    (
        "final state matches",
        {"expected_final_state": {"next_step.type": "pay", "consent.payment.status": "granted"}},
        {
            "response": "Фиксирую: 960 USD, выставлю счёт.",
            "tool_calls": [],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
            "state": {"next_step": {"type": "pay"}, "consent": {"payment": {"status": "granted"}}},
        },
        True,
    ),
    (
        "final state mismatch fails",
        {"expected_final_state": {"next_step.type": "pay"}},
        {
            "response": "Фиксирую: 960 USD.",
            "tool_calls": [],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
            "state": {"next_step": {"type": "none"}},
        },
        False,
    ),
    (
        "final state declared but missing fails",
        {"expected_final_state": {"next_step.type": "pay"}},
        {
            "response": "Фиксирую: 960 USD.",
            "tool_calls": [],
            "handoff": False,
            "handoff_attempted": False,
            "stopped": False,
        },
        False,
    ),
]


def main() -> int:
    failures: list[str] = []
    for label, overrides, record, expect_pass in SYNTHETIC_CASES:
        scenario = {"expected": base_expected(**overrides), "locale": "ru"}
        problems, _warnings = evaluate(scenario, record)
        passed = not problems
        if passed != expect_pass:
            expectation = "pass" if expect_pass else "fail"
            failures.append(f"synthetic [{label}]: expected {expectation}, got {'pass' if passed else 'fail'} ({problems})")

    for scenario_id, label, record, expect_pass in CASES:
        scenario = SCENARIOS.get(scenario_id)
        if scenario is None:
            failures.append(f"missing scenario {scenario_id}")
            continue
        problems, _warnings = evaluate(scenario, record)
        passed = not problems
        if passed != expect_pass:
            expectation = "pass" if expect_pass else "fail"
            failures.append(f"{scenario_id} [{label}]: expected {expectation}, got {'pass' if passed else 'fail'} ({problems})")

    if failures:
        for failure in failures:
            print(f"FAIL  {failure}", file=sys.stderr)
        print(f"\nChecker regression test FAILED ({len(failures)} case(s))")
        return 1

    print(
        f"OK  checker regression test passed "
        f"({len(CASES)} scenario cases + {len(SYNTHETIC_CASES)} synthetic state cases, no model called)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
