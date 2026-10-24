#!/usr/bin/env python3
"""Read-only product-passport lookup over versioned JSON files.

The adapter is deliberately small and file-backed. It does not run a server,
write business data during a conversation, or contact an external service.

Runtime operations:
    resolve   -> list currently usable offers
    lookup    -> return selected fields for one offer
    authority -> return only authority/discount/quote policy fields

Operator commands:
    validate  -> validate one version without changing the catalog
    publish   -> validate one version, then atomically point the catalog at it

Configuration for the Hermes plugin:
    DANIYAR_PASSPORT_ROOT   e.g. /opt/data/profiles/daniyar/passports
    DANIYAR_TENANT_ID       e.g. daniyar

The model never supplies a filesystem path. The catalog and this adapter own
path resolution, approval checks, and version selection.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # pragma: no cover - deployment guard
    Draft202012Validator = None  # type: ignore[assignment]
    FormatChecker = None  # type: ignore[assignment]

CONTRACT_VERSION = "1.1.0"
TOOL_NAME = "passport.lookup"
DEFAULT_TENANT = "daniyar"
OFFER_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
FIELD_RE = re.compile(r"^[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*$")
ALLOWED_SECTIONS = {
    "business",
    "offer",
    "pricing",
    "qualification",
    "discovery",
    "proof",
    "fulfillment",
    "sales_policy",
    "sales_guidance",
    "handoff",
    "follow_up",
    "privacy",
    "safety",
}
AUTHORITY_FIELDS = [
    "pricing.discount_policy",
    "pricing.quote_policy",
    "sales_policy.authority_limits",
    "sales_policy.approval_matrix",
    "sales_policy.negotiation",
]


class PassportError(Exception):
    """An expected, safe-to-report lookup failure."""

    def __init__(self, status: str, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.status = status
        self.message = message
        self.retryable = retryable


def _error_code(status: str) -> str:
    # The shared tool-envelope error enum has no `expired` or `failed` code.
    if status == "expired":
        return "verification_failed"
    if status == "failed":
        return "internal_error"
    if status in {"not_found", "invalid_request", "forbidden", "unauthorized", "conflict", "unavailable", "timeout"}:
        return status
    return "internal_error"


def _parse_datetime(value: str | None) -> dt.datetime:
    if not value:
        return dt.datetime.now(dt.timezone.utc)
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise PassportError("invalid_request", "`at` must be an ISO-8601 datetime") from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _parse_date(value: Any, field: str) -> dt.date:
    if not isinstance(value, str):
        raise PassportError("invalid_request", f"{field} must be an ISO date")
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise PassportError("invalid_request", f"{field} must be an ISO date") from exc


def _json_read(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise PassportError("not_found", f"Required file not found: {path.name}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise PassportError("invalid_request", f"Cannot read valid JSON from {path.name}") from exc


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _fact_value(value: Any) -> Any:
    if isinstance(value, dict) and "value" in value and "status" in value:
        return value.get("value")
    return value


class PassportStore:
    def __init__(self, root: str | Path, tenant_id: str, schema_path: str | Path | None = None):
        self.root = Path(root).expanduser().resolve()
        self.tenant_id = tenant_id
        self.schema_path = Path(schema_path).expanduser().resolve() if schema_path else self.root / "schema" / "passport.schema.json"
        if not self.root.is_dir():
            raise PassportError("unavailable", "Passport root is not available", retryable=True)
        if not self.schema_path.is_file():
            raise PassportError("unavailable", "Passport schema is not available", retryable=True)
        if Draft202012Validator is None or FormatChecker is None:
            raise PassportError("unavailable", "The jsonschema package is required", retryable=True)
        schema = _json_read(self.schema_path)
        self.validator = Draft202012Validator(schema, format_checker=FormatChecker())

    def catalog(self) -> dict[str, Any]:
        path = self.root / "catalog.json"
        catalog = _json_read(path)
        if not isinstance(catalog, dict) or not isinstance(catalog.get("offers"), dict):
            raise PassportError("invalid_request", "catalog.json must contain an offers object")
        if catalog.get("tenant_id") != self.tenant_id:
            raise PassportError("forbidden", "The catalog belongs to a different tenant")
        return catalog

    def _check_offer_id(self, offer_id: Any) -> str:
        if not isinstance(offer_id, str) or not OFFER_ID_RE.fullmatch(offer_id):
            raise PassportError("invalid_request", "offer_id must be a simple lowercase offer identifier")
        return offer_id

    def _safe_file(self, relative: Any) -> Path:
        if not isinstance(relative, str) or not relative or relative.startswith(("/", "~")):
            raise PassportError("invalid_request", "Catalog file must be a relative path inside the passport root")
        candidate = (self.root / relative).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise PassportError("forbidden", "Catalog file escapes the passport root") from exc
        return candidate

    def _load_document(self, path: Path) -> dict[str, Any]:
        data = _json_read(path)
        if not isinstance(data, dict):
            raise PassportError("invalid_request", "A passport must be a JSON object")
        errors = sorted(self.validator.iter_errors(data), key=lambda error: list(error.absolute_path))
        if errors:
            location = ".".join(str(part) for part in errors[0].absolute_path) or "<root>"
            raise PassportError("invalid_request", f"Passport schema validation failed at {location}")
        return data

    def _check_approval(self, data: dict[str, Any], at: dt.datetime) -> None:
        status = data.get("status")
        if status == "draft":
            raise PassportError("not_found", "No approved passport is published for this offer")
        if status in {"revoked", "expired"}:
            raise PassportError("expired", "The passport is not active")
        if status != "approved":
            raise PassportError("invalid_request", "Passport status is not approved")

        metadata = data.get("metadata") or {}
        if not metadata.get("approved_by") or not metadata.get("approved_at"):
            raise PassportError("invalid_request", "An approved passport needs approved_by and approved_at")

        today = at.date()
        effective_from = _parse_date(data.get("effective_from"), "effective_from")
        effective_to_raw = data.get("effective_to")
        effective_to = _parse_date(effective_to_raw, "effective_to") if effective_to_raw else None
        if effective_to and effective_to < effective_from:
            raise PassportError("invalid_request", "effective_to precedes effective_from")
        if today < effective_from or (effective_to and today > effective_to):
            raise PassportError("expired", "The passport is outside its effective window")

        approved_at = _parse_date(metadata.get("approved_at"), "metadata.approved_at")
        review_days = metadata.get("review_cycle_days")
        if not isinstance(review_days, int) or review_days < 1:
            raise PassportError("invalid_request", "metadata.review_cycle_days must be a positive integer")
        if today > approved_at + dt.timedelta(days=review_days):
            raise PassportError("expired", "The passport review cycle has expired")

    def _load_offer(self, offer_id: str, at: dt.datetime, version: str | None = None) -> tuple[dict[str, Any], Path, dict[str, Any]]:
        self._check_offer_id(offer_id)
        catalog = self.catalog()
        entry = catalog["offers"].get(offer_id)
        if not isinstance(entry, dict):
            raise PassportError("not_found", "The requested offer is not published")

        pinned = bool(version)
        if version:
            if not re.fullmatch(r"\d+\.\d+\.\d+", version):
                raise PassportError("invalid_request", "version must be a semantic version")
            path = self._safe_file(f"offers/{offer_id}/{version}.json")
        else:
            path = self._safe_file(entry.get("file"))
            version = entry.get("current_version")

        if not pinned and entry.get("sha256") and entry["sha256"] != _sha256(path):
            raise PassportError("conflict", "Published file hash does not match the catalog; re-publish or restore the file")
        data = self._load_document(path)
        if data.get("passport_id") != entry.get("passport_id"):
            raise PassportError("conflict", "Catalog passport_id does not match the passport file")
        if data.get("version") != version:
            raise PassportError("conflict", "Catalog version does not match the passport file")
        offer = data.get("offer") or {}
        if offer.get("id") != offer_id:
            raise PassportError("conflict", "Catalog offer_id does not match offer.id")
        self._check_approval(data, at)
        return data, path, entry

    def resolve(self, at: dt.datetime) -> dict[str, Any]:
        offers: list[dict[str, Any]] = []
        unavailable: list[dict[str, str]] = []
        for offer_id in sorted(self.catalog()["offers"]):
            try:
                data, _path, _entry = self._load_offer(offer_id, at)
            except PassportError as exc:
                unavailable.append({"offer_id": offer_id, "status": exc.status})
                continue
            offer = data.get("offer") or {}
            offers.append(
                {
                    "offer_id": offer_id,
                    "passport_id": data["passport_id"],
                    "version": data["version"],
                    "name": offer.get("name"),
                    "one_liner": _fact_value(offer.get("one_liner")),
                    "fulfillment_mode": (data.get("fulfillment") or {}).get("mode"),
                }
            )
        return {"offers": offers, "unavailable": unavailable}

    @staticmethod
    def _extract(document: dict[str, Any], path: str) -> Any:
        current: Any = document
        for part in path.split("."):
            if not isinstance(current, dict) or part not in current:
                raise PassportError("invalid_request", f"Unknown requested field: {path}")
            current = current[part]
        return current

    @staticmethod
    def _sanitize(path: str, value: Any) -> Any:
        result = copy.deepcopy(value)
        if path == "privacy" and isinstance(result, dict):
            result.pop("legal_basis", None)
        if path == "proof" and isinstance(result, dict):
            for key in ("cases", "testimonials"):
                if isinstance(result.get(key), list):
                    result[key] = [item for item in result[key] if item.get("permission") in {"public", "anonymized"}]
        elif path in {"proof.cases", "proof.testimonials"} and isinstance(result, list):
            result = [item for item in result if isinstance(item, dict) and item.get("permission") in {"public", "anonymized"}]
        if isinstance(result, dict) and "status" in result and "value" in result:
            if result.get("status") == "unknown" or result.get("value") is None:
                return {"status": "unknown", "value": None}
        return result

    def lookup(self, offer_id: str, fields: list[str], at: dt.datetime, version: str | None = None) -> dict[str, Any]:
        if not isinstance(fields, list) or not fields or len(fields) > 40:
            raise PassportError("invalid_request", "requested_fields must contain 1–40 dot paths")
        data, path, _entry = self._load_offer(offer_id, at, version)
        selected: dict[str, Any] = {}
        for field in fields:
            if not isinstance(field, str) or not FIELD_RE.fullmatch(field):
                raise PassportError("invalid_request", f"Invalid field path: {field!r}")
            section = field.split(".", 1)[0]
            if section not in ALLOWED_SECTIONS:
                raise PassportError("forbidden", f"Field section is not available to the model: {section}")
            if field == "privacy.legal_basis" or field.startswith("privacy.legal_basis."):
                raise PassportError("forbidden", "privacy.legal_basis requires a separate approved scope")
            selected[field] = self._sanitize(field, self._extract(data, field))

        metadata = data["metadata"]
        approved_at = _parse_date(metadata["approved_at"], "metadata.approved_at")
        freshness_days = (at.date() - approved_at).days
        return {
            "passport_id": data["passport_id"],
            "offer_id": offer_id,
            "version": data["version"],
            "passport_status": data["status"],
            "effective_from": data.get("effective_from"),
            "effective_to": data.get("effective_to"),
            "approved_at": metadata["approved_at"],
            "fields": selected,
            "freshness": {
                "age_days": max(0, freshness_days),
                "review_cycle_days": metadata["review_cycle_days"],
                "stale": False,
            },
            "source_file_sha256": _sha256(path),
        }


def _meta() -> dict[str, Any]:
    return {
        "server_time": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": "versioned-json-passport-store",
        "contract_version": CONTRACT_VERSION,
        "trace_id": f"trace_{uuid.uuid4().hex[:16]}",
    }


def _response(params: dict[str, Any], data: Any = None, *, status: str = "ok", error: PassportError | None = None) -> dict[str, Any]:
    request_id = params.get("request_id") or f"req_{uuid.uuid4().hex[:16]}"
    ok = error is None
    return {
        "ok": ok,
        "status": status if ok else error.status,
        "tool": TOOL_NAME,
        "request_id": request_id,
        "data": data if ok else None,
        "error": None
        if ok
        else {
            "code": _error_code(error.status),
            "message": error.message,
            "retryable": error.retryable,
            "details": {"status": error.status},
        },
        "meta": _meta(),
    }


def handle_request(params: dict[str, Any], root: str | Path, tenant_id: str) -> dict[str, Any]:
    """Handle one logical passport.lookup request without raising to the model."""
    try:
        if not isinstance(params, dict):
            raise PassportError("invalid_request", "Request params must be an object")
        supplied_tenant = params.get("tenant_id")
        if supplied_tenant is not None and supplied_tenant != tenant_id:
            raise PassportError("forbidden", "The request tenant does not match the configured tenant")
        operation = params.get("operation", "lookup")
        if operation not in {"resolve", "lookup", "authority"}:
            raise PassportError("invalid_request", "operation must be resolve, lookup, or authority")
        at = _parse_datetime(params.get("at"))
        locale = params.get("locale", "ru")
        if locale not in {"ru", "ky", "en"}:
            raise PassportError("invalid_request", "locale must be ru, ky, or en (approved content locale)")

        store = PassportStore(root, tenant_id, params.get("schema_path"))
        if operation == "resolve":
            data = store.resolve(at)
        elif operation == "authority":
            data = store.lookup(params.get("offer_id"), AUTHORITY_FIELDS, at, params.get("version"))
        else:
            data = store.lookup(params.get("offer_id"), params.get("requested_fields"), at, params.get("version"))
        return _response(params, data)
    except PassportError as exc:
        return _response(params if isinstance(params, dict) else {}, status=exc.status, error=exc)
    except Exception:  # fail closed; do not expose internals to the model
        return _response(
            params if isinstance(params, dict) else {},
            status="unavailable",
            error=PassportError("unavailable", "Passport lookup could not be completed", retryable=True),
        )


def hermes_check() -> bool:
    """Hermes check_fn: expose the tool only with a complete local store."""
    root = os.environ.get("DANIYAR_PASSPORT_ROOT")
    if not root or not os.environ.get("DANIYAR_TENANT_ID"):
        return False
    try:
        path = Path(root).expanduser()
        return path.is_dir() and (path / "catalog.json").is_file() and (path / "schema" / "passport.schema.json").is_file() and Draft202012Validator is not None
    except OSError:
        return False


def hermes_handler(args: dict[str, Any], **kwargs: Any) -> str:
    root = os.environ.get("DANIYAR_PASSPORT_ROOT")
    tenant_id = os.environ.get("DANIYAR_TENANT_ID", DEFAULT_TENANT)
    if not root:
        return json.dumps(
            _response(args, status="unavailable", error=PassportError("unavailable", "DANIYAR_PASSPORT_ROOT is not configured")),
            ensure_ascii=False,
        )
    params = dict(args or {})
    params.setdefault("conversation_id", kwargs.get("task_id", ""))
    return json.dumps(handle_request(params, root, tenant_id), ensure_ascii=False)


HERMES_TOOL_SCHEMA = {
    "name": "passport_lookup",
    "description": "Read approved product facts from the versioned passport store. Use operation=resolve to list offers, lookup for selected fields, or authority for discount/quote limits. Returns only approved current facts with passport_id and version. Never use conversation memory as a substitute for this lookup.",
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {"type": "string", "enum": ["resolve", "lookup", "authority"], "default": "lookup"},
            "offer_id": {"type": "string", "description": "Exact offer.id returned by resolve; required for lookup and authority"},
            "locale": {"type": "string", "enum": ["ru", "ky", "en"], "default": "ru"},
            "requested_fields": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Dot paths such as pricing.plans, pricing.currency, fulfillment.mode, offer.support. Required for lookup; max 40",
            },
            "version": {"type": "string", "description": "Optional semantic version to pin for audit; default is the catalog's current approved version"},
            "at": {"type": "string", "description": "Optional ISO-8601 datetime for effective-window checks"},
        },
        "required": [],
    },
}


def _load_candidate(root: Path, offer_id: str, version: str) -> tuple[dict[str, Any], Path]:
    store = PassportStore(root, os.environ.get("DANIYAR_TENANT_ID", DEFAULT_TENANT))
    store._check_offer_id(offer_id)
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise PassportError("invalid_request", "version must be a semantic version")
    path = store._safe_file(f"offers/{offer_id}/{version}.json")
    data = store._load_document(path)
    if data.get("passport_id") != offer_id:
        raise PassportError("conflict", "For this simple store, passport_id must equal offer_id")
    if data.get("version") != version:
        raise PassportError("conflict", "Filename version and passport version differ")
    if (data.get("offer") or {}).get("id") != offer_id:
        raise PassportError("conflict", "Filename offer_id and offer.id differ")
    return data, path


def validate_candidate(root: str | Path, offer_id: str, version: str, at: str | None = None) -> dict[str, Any]:
    root_path = Path(root).expanduser().resolve()
    data, path = _load_candidate(root_path, offer_id, version)
    store = PassportStore(root_path, os.environ.get("DANIYAR_TENANT_ID", DEFAULT_TENANT))
    store._check_approval(data, _parse_datetime(at))
    return {
        "ok": True,
        "offer_id": offer_id,
        "version": version,
        "file": str(path.relative_to(root_path)),
        "sha256": _sha256(path),
    }


def publish_candidate(root: str | Path, offer_id: str, version: str, at: str | None = None) -> dict[str, Any]:
    """Validate first; only then replace the catalog pointer atomically."""
    root_path = Path(root).expanduser().resolve()
    result = validate_candidate(root_path, offer_id, version, at)
    data, path = _load_candidate(root_path, offer_id, version)
    catalog_path = root_path / "catalog.json"
    if catalog_path.exists():
        catalog = _json_read(catalog_path)
        if not isinstance(catalog, dict) or not isinstance(catalog.get("offers"), dict):
            raise PassportError("invalid_request", "Existing catalog.json is malformed; it was not changed")
    else:
        catalog = {"tenant_id": os.environ.get("DANIYAR_TENANT_ID", DEFAULT_TENANT), "offers": {}}
    if catalog.get("tenant_id") != os.environ.get("DANIYAR_TENANT_ID", DEFAULT_TENANT):
        raise PassportError("forbidden", "Catalog tenant does not match DANIYAR_TENANT_ID")

    catalog["offers"][offer_id] = {
        "passport_id": data["passport_id"],
        "current_version": version,
        "file": result["file"],
        "sha256": result["sha256"],
    }
    catalog["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()

    temporary = tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=root_path, prefix=".catalog-", suffix=".tmp", delete=False)
    try:
        with temporary as handle:
            json.dump(catalog, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary.name, catalog_path)
    finally:
        if os.path.exists(temporary.name):
            os.unlink(temporary.name)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=os.environ.get("DANIYAR_PASSPORT_ROOT"), help="Persistent passport store root")
    parser.add_argument("--tenant-id", default=os.environ.get("DANIYAR_TENANT_ID", DEFAULT_TENANT))
    subparsers = parser.add_subparsers(dest="command", required=True)

    lookup_parser = subparsers.add_parser("lookup", help="Handle a JSON request from a file or stdin")
    lookup_parser.add_argument("--request", default="-", help="JSON request file, or - for stdin")

    for command in ("validate", "publish"):
        command_parser = subparsers.add_parser(command, help=f"{command} one passport version")
        command_parser.add_argument("--offer-id", required=True)
        command_parser.add_argument("--version", required=True)
        command_parser.add_argument("--at", help="ISO-8601 datetime used for effective-window validation")

    args = parser.parse_args()
    if not args.root:
        parser.error("--root or DANIYAR_PASSPORT_ROOT is required")
    os.environ["DANIYAR_TENANT_ID"] = args.tenant_id

    try:
        if args.command == "lookup":
            raw = sys.stdin.read() if args.request == "-" else Path(args.request).read_text(encoding="utf-8")
            params = json.loads(raw)
            result = handle_request(params, args.root, args.tenant_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result.get("ok") else 1
        if args.command == "validate":
            result = validate_candidate(args.root, args.offer_id, args.version, args.at)
        else:
            result = publish_candidate(args.root, args.offer_id, args.version, args.at)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (PassportError, json.JSONDecodeError) as exc:
        message = exc.message if isinstance(exc, PassportError) else str(exc)
        print(json.dumps({"ok": False, "error": message}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
