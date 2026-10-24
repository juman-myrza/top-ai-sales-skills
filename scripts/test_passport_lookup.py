#!/usr/bin/env python3
"""Unit tests for the file-backed passport lookup adapter.

These tests use temporary, fictional passports. They do not call a model,
Hermes, a VPS, or any external service.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTER_PATH = ROOT / "tools" / "adapters" / "passport-lookup" / "passport_lookup.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


adapter = load_module(ADAPTER_PATH, "passport_lookup_adapter_for_tests")
SCHEMA = json.loads((ROOT / "product-passport" / "passport.schema.json").read_text())
from jsonschema import Draft202012Validator, FormatChecker

ENVELOPE = json.loads((ROOT / "tools" / "schemas" / "tool-envelope.schema.json").read_text())
ENVELOPE_VALIDATOR = Draft202012Validator(ENVELOPE, format_checker=FormatChecker())
AT = "2026-10-24T12:00:00+06:00"


def make_passport(offer_id: str, name: str, price: int, source_file: str) -> dict:
    data = json.loads((ROOT / "product-passport" / "examples" / source_file).read_text())
    data["passport_id"] = offer_id
    data["offer"]["id"] = offer_id
    data["offer"]["name"] = name
    data["version"] = "1.0.0"
    data["status"] = "approved"
    data["effective_from"] = "2026-01-01"
    data["effective_to"] = "2027-12-31"
    data["pricing"]["plans"] = [copy.deepcopy(data["pricing"]["plans"][0])]
    data["pricing"]["plans"][0]["price"]["value"] = price
    data["metadata"].update(
        {
            "approved_by": "Fictional test approver",
            "approved_at": "2026-10-24",
            "updated_at": "2026-10-24",
            "review_cycle_days": 365,
            "fictional": True,
            "changelog": [],
        }
    )
    return data


class PassportLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="passport-store-", dir=os.environ.get("TMPDIR", "/tmp/opencode"))
        self.root = Path(self.temp.name)
        (self.root / "schema").mkdir(parents=True)
        (self.root / "schema" / "passport.schema.json").write_text(json.dumps(SCHEMA), encoding="utf-8")
        self.implementation = make_passport("ai-agent-implementation", "AI Agent Implementation (test)", 100, "direct-sale-nimbus-notes.json")
        self.training = make_passport("ai-agent-training", "AI Agent Training (test)", 200, "consumer-course-example.json")
        self.write_version(self.implementation, "1.0.0")
        self.write_version(self.training, "1.0.0")
        self.write_catalog()
        os.environ["DANIYAR_TENANT_ID"] = "daniyar"
        os.environ["DANIYAR_PASSPORT_ROOT"] = str(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()
        os.environ.pop("DANIYAR_TENANT_ID", None)
        os.environ.pop("DANIYAR_PASSPORT_ROOT", None)

    def write_version(self, data: dict, version: str) -> Path:
        data = copy.deepcopy(data)
        data["version"] = version
        offer_id = data["offer"]["id"]
        path = self.root / "offers" / offer_id / f"{version}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def write_catalog(self) -> None:
        catalog = {
            "tenant_id": "daniyar",
            "offers": {
                "ai-agent-implementation": {
                    "passport_id": "ai-agent-implementation",
                    "current_version": "1.0.0",
                    "file": "offers/ai-agent-implementation/1.0.0.json",
                    "sha256": adapter._sha256(self.root / "offers/ai-agent-implementation/1.0.0.json"),
                },
                "ai-agent-training": {
                    "passport_id": "ai-agent-training",
                    "current_version": "1.0.0",
                    "file": "offers/ai-agent-training/1.0.0.json",
                    "sha256": adapter._sha256(self.root / "offers/ai-agent-training/1.0.0.json"),
                },
            },
        }
        (self.root / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")

    def request(self, operation="lookup", offer_id=None, fields=None, **extra):
        params = {"operation": operation, "request_id": "req_test_001", "at": AT, "locale": "ru"}
        if offer_id is not None:
            params["offer_id"] = offer_id
        if fields is not None:
            params["requested_fields"] = fields
        params.update(extra)
        result = adapter.handle_request(params, self.root, "daniyar")
        errors = list(ENVELOPE_VALIDATOR.iter_errors(result))
        self.assertEqual([], [error.message for error in errors], f"invalid tool response envelope: {result}")
        return result

    def test_resolve_lists_both_offers_without_prices(self):
        result = self.request("resolve")
        self.assertTrue(result["ok"])
        self.assertEqual({"ai-agent-implementation", "ai-agent-training"}, {item["offer_id"] for item in result["data"]["offers"]})
        self.assertNotIn("price", json.dumps(result["data"]))

    def test_lookup_selects_the_correct_offer_and_fields(self):
        implementation = self.request(offer_id="ai-agent-implementation", fields=["pricing.plans"])
        training = self.request(offer_id="ai-agent-training", fields=["pricing.plans"])
        self.assertEqual(100, implementation["data"]["fields"]["pricing.plans"][0]["price"]["value"])
        self.assertEqual(200, training["data"]["fields"]["pricing.plans"][0]["price"]["value"])
        self.assertEqual("ai-agent-implementation", implementation["data"]["passport_id"])
        self.assertEqual("ai-agent-training", training["data"]["passport_id"])
        self.assertNotIn("tools", implementation["data"]["fields"])
        self.assertNotIn("metadata", implementation["data"]["fields"])

    def test_authority_returns_only_authority_fields(self):
        result = self.request("authority", "ai-agent-implementation")
        self.assertTrue(result["ok"])
        self.assertEqual(set(adapter.AUTHORITY_FIELDS), set(result["data"]["fields"]))

    def test_unknown_and_forbidden_fields_fail_closed(self):
        self.assertEqual("invalid_request", self.request(offer_id="ai-agent-training", fields=["pricing.not_a_field"])["status"])
        self.assertEqual("forbidden", self.request(offer_id="ai-agent-training", fields=["tools"])["status"])
        self.assertEqual("forbidden", self.request(offer_id="ai-agent-training", fields=["privacy.legal_basis"])["status"])

    def test_draft_expired_and_revoked_are_not_served(self):
        for status, expected in (("draft", "not_found"), ("expired", "expired"), ("revoked", "expired")):
            with self.subTest(status=status):
                candidate = copy.deepcopy(self.training)
                candidate["status"] = status
                self.write_version(candidate, "1.0.0")
                self.write_catalog()
                self.assertEqual(expected, self.request(offer_id="ai-agent-training", fields=["pricing.plans"])["status"])

    def test_missing_approver_is_rejected(self):
        candidate = copy.deepcopy(self.training)
        candidate["metadata"]["approved_by"] = None
        self.write_version(candidate, "1.0.0")
        self.write_catalog()
        self.assertEqual("invalid_request", self.request(offer_id="ai-agent-training", fields=["pricing.plans"])["status"])

    def test_cross_tenant_and_path_traversal_are_rejected(self):
        self.assertEqual("forbidden", self.request(offer_id="ai-agent-training", fields=["pricing.plans"], tenant_id="other")["status"])
        catalog = json.loads((self.root / "catalog.json").read_text())
        catalog["offers"]["ai-agent-training"]["file"] = "../secret.json"
        (self.root / "catalog.json").write_text(json.dumps(catalog))
        self.assertEqual("forbidden", self.request(offer_id="ai-agent-training", fields=["pricing.plans"])["status"])

    def test_hash_mismatch_is_detected(self):
        path = self.root / "offers/ai-agent-training/1.0.0.json"
        data = json.loads(path.read_text())
        data["pricing"]["plans"][0]["price"]["value"] = 999
        path.write_text(json.dumps(data))
        self.assertEqual("conflict", self.request(offer_id="ai-agent-training", fields=["pricing.plans"])["status"])

    def test_publish_is_atomic_and_preserves_history(self):
        before = (self.root / "catalog.json").read_text()
        invalid = copy.deepcopy(self.training)
        invalid["pricing"]["plans"][0]["price"]["value"] = "banana"
        self.write_version(invalid, "1.1.0")
        with self.assertRaises(adapter.PassportError):
            adapter.publish_candidate(self.root, "ai-agent-training", "1.1.0", AT)
        self.assertEqual(before, (self.root / "catalog.json").read_text())

        valid = copy.deepcopy(self.training)
        valid["pricing"]["plans"][0]["price"]["value"] = 300
        self.write_version(valid, "1.1.0")
        adapter.publish_candidate(self.root, "ai-agent-training", "1.1.0", AT)
        result = self.request(offer_id="ai-agent-training", fields=["pricing.plans"])
        self.assertEqual(300, result["data"]["fields"]["pricing.plans"][0]["price"]["value"])
        self.assertTrue((self.root / "offers/ai-agent-training/1.0.0.json").is_file())

    def test_plugin_registration_is_minimal(self):
        plugin = load_module(ROOT / "tools" / "adapters" / "passport-lookup" / "__init__.py", "passport_lookup_plugin_for_tests")
        calls = []

        class Context:
            def register_tool(self, **kwargs):
                calls.append(kwargs)

        plugin.register(Context())
        self.assertEqual(1, len(calls))
        self.assertEqual("passport_lookup", calls[0]["name"])
        self.assertEqual("passport", calls[0]["toolset"])
        self.assertEqual("hermes_check", calls[0]["check_fn"].__name__)
        self.assertEqual(adapter.HERMES_TOOL_SCHEMA, calls[0]["schema"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
