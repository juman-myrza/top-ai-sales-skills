#!/usr/bin/env python3
"""No-network structural tests for the adaptive roleplay corpus and evaluator."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "tests" / "live"
sys.path.insert(0, str(LIVE))

from run_roleplay_eval import (  # noqa: E402
    SCORE_DIMENSIONS,
    load_cases,
    parse_json_object,
    score_shape_errors,
)

CASES_PATH = LIVE / "roleplay-cases.yaml"


class RoleplayEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = load_cases(CASES_PATH)

    def test_five_unique_multilingual_cases_exist(self) -> None:
        self.assertEqual(len(self.cases), 5)
        self.assertEqual(len({case["id"] for case in self.cases}), 5)
        self.assertEqual({case["locale"] for case in self.cases}, {"ru", "ky", "mixed"})

    def test_scenarios_do_not_hardcode_passport_prices(self) -> None:
        content = CASES_PATH.read_text(encoding="utf-8")
        for stale_price in ("35 000", "10 000", "100 000", "35000", "100000"):
            self.assertNotIn(stale_price, content)

    def test_case_success_and_failure_signals_are_present(self) -> None:
        for case in self.cases:
            self.assertTrue(case["success_signals"], case["id"])
            self.assertTrue(case["failure_signals"], case["id"])
            self.assertGreaterEqual(case["max_seller_turns"], 3)

    def test_trust_case_checks_conditional_technical_claims(self) -> None:
        case = next(item for item in self.cases if item["id"] == "RP-RU-TRUST")
        success = " ".join(case["success_signals"]).lower()
        failure = " ".join(case["failure_signals"]).lower()
        self.assertIn("timestamp semantics", success)
        self.assertIn("queried/received", success)
        self.assertIn("handoff", success)
        self.assertIn("what 1c exposes", failure)
        self.assertIn("implemented", failure)

    def test_json_parser_accepts_plain_and_fenced_objects(self) -> None:
        self.assertEqual(parse_json_object('{"message":"ok","done":true}'), {"message": "ok", "done": True})
        fenced = chr(96) * 3 + 'json\n{"message":"ok","done":false}\n' + chr(96) * 3
        self.assertEqual(parse_json_object(fenced), {"message": "ok", "done": False})

    def test_score_validator_requires_all_evidence_dimensions(self) -> None:
        transcript = "DANIYAR: I cannot promise that; the terms are not verified."
        valid = {
            "hard_fail": False,
            "hard_fail_reasons": [],
            "scores": {
                dim: {"score": 3, "evidence": "I cannot promise that; the terms are not verified.", "reason": "Specific evidence"}
                for dim in SCORE_DIMENSIONS
            },
            "coaching": [],
            "missed_signals": [],
            "one_priority_for_next_practice": "Ask one diagnostic question before recommending.",
        }
        self.assertEqual(score_shape_errors(valid, transcript), [])
        invalid_scores = {**valid["scores"], "discovery_depth": {"score": 5, "evidence": "invented quote", "reason": ""}}
        del invalid_scores["language_clarity"]
        invalid = {**valid, "scores": invalid_scores}
        errors = score_shape_errors(invalid, transcript)
        self.assertTrue(any("missing score dimension" in e for e in errors))
        self.assertTrue(any("exact quote" in e for e in errors))
        self.assertTrue(any("integer from 0 to 4" in e for e in errors))

if __name__ == "__main__":
    unittest.main()
