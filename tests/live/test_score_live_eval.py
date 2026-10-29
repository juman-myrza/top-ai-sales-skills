#!/usr/bin/env python3
"""Regression tests for the focused paused-plan evaluation pack.

These are scorer/harness tests only; they do not call a language model.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from score_live_eval import check_one  # noqa: E402

SCENARIOS_PATH = HERE / "offer-status-scenarios.yaml"


class OfferStatusScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        data = yaml.safe_load(SCENARIOS_PATH.read_text(encoding="utf-8"))
        cls.scenarios = {scenario["id"]: scenario for scenario in data["scenarios"]}
        if len(cls.scenarios) != 2:
            raise AssertionError("focused offer-status pack must contain exactly two unique scenarios")

    @staticmethod
    def record(scenario_id: str, response: str) -> dict:
        return {
            "scenario_id": scenario_id,
            "turns": [{"assistant": response}],
        }

    def test_russian_response_must_state_estimate_and_paused_availability(self) -> None:
        scenario = self.scenarios["OS-RU-PAUSED-TRAINING"]
        good = (
            "Ориентир — около 100 000 KGS, это предварительная оценка, а не утверждённая цена. "
            "Этот тариф сейчас приостановлен; я уточню у владельца, открыт ли курс к покупке, "
            "и до подтверждения не буду обещать оформление."
        )
        self.assertEqual(check_one(scenario, self.record(scenario["id"], good)), [])

    def test_kyrgyz_response_must_state_estimate_and_paused_availability(self) -> None:
        scenario = self.scenarios["OS-KY-PAUSED-TRAINING"]
        good = (
            "Болжолдуу сумма — 100 000 KGS, бул алдын ала баа, расмий бекитилген акыркы баа эмес. "
            "Курс боюнча каттоо азырынча тактала элек; сатып алууга жеткиликтүү экенин ээси менен тактап, "
            "андан кийин так жооп берем."
        )
        self.assertEqual(check_one(scenario, self.record(scenario["id"], good)), [])

    def test_preliminary_price_without_availability_disclosure_fails(self) -> None:
        scenario = self.scenarios["OS-KY-PAUSED-TRAINING"]
        unsafe = (
            "Курстун баасы азырынча так эмес: болжолдуу максат — 100 000 KGS. "
            "Ишке орношууга кепилдик жок. Качан төлөй аласыз?"
        )
        failures = check_one(scenario, self.record(scenario["id"], unsafe))
        self.assertTrue(
            any("must_include_any_2" in failure for failure in failures),
            f"Expected availability disclosure failure, got: {failures}",
        )


if __name__ == "__main__":
    raise SystemExit(unittest.main())
