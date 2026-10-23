#!/usr/bin/env python3
"""Static validation for the universal AI sales skills repository.

This script checks structure, schemas, scenario integrity, and local links.
It does not call a model, a tool adapter, or Hermes. Passing means the files
are internally consistent, not that an agent behaves well.

Exit codes:
    0  all checks passed (warnings allowed)
    1  one or more errors
    2  validation could not run (missing dependency or repository root)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    print("ERROR: PyYAML is required. Install with: pip install -r requirements-dev.txt", file=sys.stderr)
    raise SystemExit(2)

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - environment guard
    print("ERROR: jsonschema is required. Install with: pip install -r requirements-dev.txt", file=sys.stderr)
    raise SystemExit(2)


ROOT = Path(__file__).resolve().parent.parent

EXPECTED_SKILLS = [
    "sales-conversation-orchestrator",
    "sales-qualification",
    "sales-discovery",
    "sales-value-proof",
    "sales-objection-negotiation",
    "sales-closing-execution",
    "sales-language-adaptation",
    "sales-follow-up",
    "sales-integrity-escalation",
]

EXPECTED_CATEGORIES = {
    "price-intent": 6,
    "qualification-discovery": 6,
    "objections": 8,
    "closing-booking": 7,
    "tool-failures": 6,
    "handoff-safety": 6,
    "multilingual-multiturn": 6,
    "follow-up-refusal": 6,
}

EXPECTED_TOTAL = sum(EXPECTED_CATEGORIES.values())

CATEGORY_LABELS = {
    "price-intent": "Price and buying intent",
    "qualification-discovery": "Qualification and discovery",
    "objections": "Objections and negotiation",
    "closing-booking": "Closing and booking",
    "tool-failures": "Tool failures",
    "handoff-safety": "Handoff and safety",
    "multilingual-multiturn": "Multilingual and multi-turn",
    "follow-up-refusal": "Follow-up and refusal",
}

SKILL_SECTIONS = [
    "## When to Use",
    "## When Not to Use",
    "## Required Inputs",
    "## Procedure",
    "## Branches",
    "## Stopping Conditions",
    "## Failure Recovery",
    "## Examples",
    "## Counterexamples",
    "## Dependencies",
    "## Sources",
]

LOCALES = {"ru", "ky", "mixed", "other"}
DIFFICULTIES = {"basic", "intermediate", "advanced"}
STAGES = {
    "open",
    "qualify",
    "discover",
    "value",
    "resolve",
    "commit",
    "execute",
    "confirm",
    "follow_up",
    "protect",
}
RUBRIC_DIMENSIONS = {"truth", "consent", "diagnosis", "execution", "language", "integrity", "efficiency"}

TOOL_NAMES = {
    "passport.lookup",
    "calendar.availability",
    "calendar.booking",
    "payments.invoicing",
    "crm.memory",
    "human.handoff",
    "messaging.media",
}

SCENARIO_KEYS = {
    "id",
    "title",
    "difficulty",
    "passport",
    "locale",
    "tags",
    "context",
    "turns",
    "fixtures",
    "expected",
    "rubric_focus",
    "notes",
}
CONTEXT_KEYS = {"stage", "known_facts", "consent"}
EXPECTED_KEYS = {
    "language",
    "must_include_all",
    "must_include_any",
    "must_not_include",
    "must_not_regex",
    "max_questions",
    "required_tool_calls",
    "forbidden_tool_calls",
    "forbidden_tool_operations",
    "should_handoff",
    "should_attempt_handoff",
    "should_stop",
    "should_disqualify",
    "human_review",
}
REQUIRED_EXPECTED = {
    "language",
    "max_questions",
    "required_tool_calls",
    "forbidden_tool_calls",
    "forbidden_tool_operations",
    "should_handoff",
    "should_attempt_handoff",
    "should_stop",
    "should_disqualify",
    "human_review",
}
FIXTURE_KEYS = {"tool", "operation", "status", "note"}

REQUIRED_PATHS = [
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "ATTRIBUTION.md",
    "CONTRIBUTING.md",
    ".gitignore",
    "requirements-dev.txt",
    "core/CORE-BEHAVIOR-CONTRACT.md",
    "core/CONFLICT-RESOLUTION.md",
    "core/CONVERSATION-STATE.md",
    "core/conversation-state.schema.json",
    "core/SYSTEM-PROMPT-SNIPPET.md",
    "product-passport/README.md",
    "product-passport/TEMPLATE.md",
    "product-passport/passport.schema.json",
    "product-passport/examples/direct-sale-nimbus-notes.json",
    "product-passport/examples/direct-sale-nimbus-notes.md",
    "product-passport/examples/appointment-karkyra-consult.json",
    "product-passport/examples/appointment-karkyra-consult.md",
    "tools/README.md",
    "tools/schemas/tool-envelope.schema.json",
    "tools/schemas/example-envelopes.json",
    "tools/contracts/passport-lookup.md",
    "tools/contracts/calendar-availability.md",
    "tools/contracts/calendar-booking.md",
    "tools/contracts/payments-invoicing.md",
    "tools/contracts/crm-memory.md",
    "tools/contracts/human-handoff.md",
    "tools/contracts/messaging-media.md",
    "tests/README.md",
    "tests/SCENARIO-FORMAT.md",
    "tests/RUBRIC.md",
    "tests/COVERAGE.md",
    "tests/fixtures/README.md",
    "research/source-register.md",
    "research/claim-evidence-matrix.md",
    "research/decisions-and-tradeoffs.md",
    "research/open-source-audit.md",
    "scripts/README.md",
    ".github/workflows/validate.yml",
]

ERRORS: list[str] = []
WARNINGS: list[str] = []
CHECKS = 0


def record(check: str, message: str) -> None:
    ERRORS.append(f"[{check}] {message}")


def warn(check: str, message: str) -> None:
    WARNINGS.append(f"[{check}] {message}")


def bump(n: int = 1) -> None:
    global CHECKS
    CHECKS += n


def load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        record("json", f"{path.relative_to(ROOT)}: {exc}")
        return None


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None, text
    if not isinstance(frontmatter, dict):
        return None, text
    return frontmatter, parts[2]


def check_required_paths() -> None:
    for rel in REQUIRED_PATHS:
        bump()
        if not (ROOT / rel).is_file():
            record("required-file", f"missing {rel}")


def check_skills() -> None:
    skill_root = ROOT / "skills" / "sales"
    if not skill_root.is_dir():
        record("skills", "skills/sales/ is missing")
        return

    found = sorted(p.parent.name for p in skill_root.glob("*/SKILL.md"))
    bump()
    if found != sorted(EXPECTED_SKILLS):
        record(
            "skills",
            f"expected 9 skills {EXPECTED_SKILLS}, found {found}",
        )

    known = set(found)
    for directory in sorted(skill_root.iterdir()):
        if not directory.is_dir():
            continue
        skill_md = directory / "SKILL.md"
        bump()
        if not skill_md.is_file():
            record("skills", f"{directory.relative_to(ROOT)} has no SKILL.md")
            continue

        text = skill_md.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text)
        rel = skill_md.relative_to(ROOT)
        if frontmatter is None:
            record("skill-frontmatter", f"{rel}: missing or invalid YAML frontmatter")
            continue

        name = str(frontmatter.get("name", "")).strip()
        description = str(frontmatter.get("description", "")).strip().strip("'\"")
        if name != directory.name:
            record("skill-name", f"{rel}: name '{name}' does not match directory '{directory.name}'")
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name):
            record("skill-name", f"{rel}: invalid name '{name}'")
        if not description:
            record("skill-description", f"{rel}: description is empty")
        elif len(description) > 60:
            record("skill-description", f"{rel}: description is {len(description)} chars (limit 60)")
        for key in ("version", "author", "license"):
            bump()
            if key not in frontmatter:
                record("skill-metadata", f"{rel}: missing frontmatter '{key}'")
        metadata = frontmatter.get("metadata")
        hermes_meta = metadata.get("hermes") if isinstance(metadata, dict) else None
        if not isinstance(hermes_meta, dict):
            record("skill-metadata", f"{rel}: missing metadata.hermes")
        else:
            if hermes_meta.get("category") != "sales":
                record("skill-metadata", f"{rel}: metadata.hermes.category must be 'sales'")
            if not hermes_meta.get("tags"):
                record("skill-metadata", f"{rel}: metadata.hermes.tags is empty")
            for related in hermes_meta.get("related_skills", []) or []:
                if related not in known:
                    record("skill-links", f"{rel}: related skill '{related}' does not exist")

        body_chars = len(body)
        bump()
        if body_chars > 24_000:
            record("skill-size", f"{rel}: body is {body_chars:,} chars (soft budget 24,000)")

        for section in SKILL_SECTIONS:
            bump()
            if not re.search(rf"^{re.escape(section)}\s*$", body, re.MULTILINE):
                record("skill-section", f"{rel}: missing section '{section}'")

        for match in re.finditer(r"(?<![\w./-])(references/[\w./-]+\.md)", body):
            ref = match.group(1)
            bump()
            if not (directory / ref).is_file():
                record("skill-reference", f"{rel}: broken reference '{ref}'")

        if re.search(r"\b(?:Nimbus|Karkyra|nimbus|karkyra)\b", text):
            record("skill-hardcoding", f"{rel}: contains a fictional example brand")
        if re.search(r"\b960\b|[0-9]+\s?(?:USD|EUR|KGS)\b", text):
            record("skill-hardcoding", f"{rel}: contains a concrete price or currency amount")

    references = sorted((ROOT / "skills").rglob("references/*.md"))
    bump()
    if not references:
        warn("skills", "no references/ files found; expected language, cadence, and escalation material")


def check_passports() -> None:
    schema_path = ROOT / "product-passport" / "passport.schema.json"
    schema = load_json(schema_path)
    if schema is None:
        return
    try:
        validator = Draft202012Validator(schema)
        validator.check_schema(schema)
    except jsonschema.SchemaError as exc:
        record("passport-schema", f"invalid schema: {exc.message}")
        return

    examples = sorted((ROOT / "product-passport" / "examples").glob("*.json"))
    bump()
    if len(examples) != 2:
        record("passport-examples", f"expected 2 JSON passport examples, found {len(examples)}")

    for path in examples:
        data = load_json(path)
        if data is None:
            continue
        bump()
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
        for exc in errors:
            location = ".".join(str(p) for p in exc.absolute_path) or "<root>"
            record("passport-example", f"{path.relative_to(ROOT)}: {location}: {exc.message}")
        md_path = path.with_suffix(".md")
        bump()
        if not md_path.is_file():
            record("passport-examples", f"{path.relative_to(ROOT)}: missing companion {md_path.name}")
        else:
            md = md_path.read_text(encoding="utf-8")
            if "[verified" in md or "TODO" in md or "TBD" in md:
                record("passport-examples", f"{md_path.relative_to(ROOT)}: contains an unreplaced placeholder")
            if "fictional" not in md.lower():
                warn("passport-examples", f"{md_path.relative_to(ROOT)}: no explicit fictional disclaimer")

    template = (ROOT / "product-passport" / "TEMPLATE.md").read_text(encoding="utf-8")
    bump()
    if "approval" not in template.lower():
        record("passport-template", "TEMPLATE.md has no approval checklist")


def check_tool_schemas() -> None:
    schema_path = ROOT / "tools" / "schemas" / "tool-envelope.schema.json"
    schema = load_json(schema_path)
    if schema is None:
        return
    try:
        validator = Draft202012Validator(schema)
        validator.check_schema(schema)
    except jsonschema.SchemaError as exc:
        record("tool-schema", f"invalid schema: {exc.message}")
        return

    examples_path = ROOT / "tools" / "schemas" / "example-envelopes.json"
    data = load_json(examples_path)
    if not isinstance(data, dict):
        return
    requests = data.get("requests", [])
    responses = data.get("responses", [])
    bump()
    if len(requests) < 7:
        record("tool-examples", f"expected at least 7 request examples, found {len(requests)}")
    bump()
    if len(responses) < 7:
        record("tool-examples", f"expected at least 7 response examples, found {len(responses)}")
    for kind, items in (("request", requests), ("response", responses)):
        for index, item in enumerate(items):
            bump()
            for exc in validator.iter_errors(item):
                location = ".".join(str(p) for p in exc.absolute_path) or "<root>"
                record("tool-example", f"{kind}[{index}] {location}: {exc.message}")


def check_scenarios() -> None:
    scenario_dir = ROOT / "tests" / "scenarios"
    files = sorted(scenario_dir.glob("*.yaml"))
    bump()
    if not files:
        record("scenarios", "no scenario files found")
        return

    all_ids: list[str] = []
    category_counts: dict[str, int] = {}
    passport_ids = {p.stem for p in (ROOT / "product-passport" / "examples").glob("*.json")}
    known_tools = TOOL_NAMES

    for path in files:
        bump()
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            record("scenario-yaml", f"{path.relative_to(ROOT)}: {exc}")
            continue
        if not isinstance(data, dict):
            record("scenario-yaml", f"{path.relative_to(ROOT)}: top level must be a mapping")
            continue

        category = data.get("category")
        if category != path.stem:
            record("scenario-category", f"{path.relative_to(ROOT)}: category '{category}' must match filename")
        if data.get("schema_version") != "1.0.0":
            record("scenario-schema", f"{path.relative_to(ROOT)}: schema_version must be 1.0.0")

        scenarios = data.get("scenarios")
        if not isinstance(scenarios, list):
            record("scenario-yaml", f"{path.relative_to(ROOT)}: scenarios must be a list")
            continue
        category_counts[str(category)] = len(scenarios)

        for index, scenario in enumerate(scenarios):
            label = f"{path.name}[{index}]"
            bump()
            if not isinstance(scenario, dict):
                record("scenario-shape", f"{label}: scenario must be a mapping")
                continue

            sid = scenario.get("id")
            if not isinstance(sid, str) or not re.fullmatch(r"[A-Z]{1,2}\d{2}", sid):
                record("scenario-id", f"{label}: invalid id {sid!r}")
                continue
            label = f"{sid} ({path.name})"
            all_ids.append(sid)

            missing = SCENARIO_KEYS - scenario.keys()
            extra = scenario.keys() - SCENARIO_KEYS
            if missing:
                record("scenario-fields", f"{label}: missing {sorted(missing)}")
            if extra:
                record("scenario-fields", f"{label}: unknown {sorted(extra)}")

            if not isinstance(scenario.get("title"), str) or not scenario["title"].strip():
                record("scenario-title", f"{label}: title is empty")
            if scenario.get("difficulty") not in DIFFICULTIES:
                record("scenario-difficulty", f"{label}: invalid difficulty {scenario.get('difficulty')!r}")
            if scenario.get("locale") not in LOCALES:
                record("scenario-locale", f"{label}: invalid locale {scenario.get('locale')!r}")
            passport = scenario.get("passport")
            if passport != "none" and passport not in passport_ids:
                record("scenario-passport", f"{label}: unknown passport '{passport}'")

            tags = scenario.get("tags")
            if not isinstance(tags, list) or len(tags) < 2:
                record("scenario-tags", f"{label}: needs at least two tags")
            else:
                for tag in tags:
                    if not isinstance(tag, str) or not re.fullmatch(r"[a-z0-9_]+", tag):
                        record("scenario-tags", f"{label}: invalid tag {tag!r}")

            context = scenario.get("context")
            if not isinstance(context, dict):
                record("scenario-context", f"{label}: context must be a mapping")
            else:
                extra_context = context.keys() - CONTEXT_KEYS
                if extra_context:
                    record("scenario-context", f"{label}: unknown context keys {sorted(extra_context)}")
                if context.get("stage") not in STAGES:
                    record("scenario-context", f"{label}: invalid stage {context.get('stage')!r}")
                if not isinstance(context.get("known_facts", {}), dict):
                    record("scenario-context", f"{label}: known_facts must be a mapping")
                if not isinstance(context.get("consent", {}), dict):
                    record("scenario-context", f"{label}: consent must be a mapping")

            turns = scenario.get("turns")
            if not isinstance(turns, list) or not turns:
                record("scenario-turns", f"{label}: turns must be a non-empty list")
            else:
                for turn_index, turn in enumerate(turns):
                    if not isinstance(turn, dict):
                        record("scenario-turns", f"{label}: turn {turn_index} must be a mapping")
                        continue
                    if turn.get("role") not in {"buyer", "event"}:
                        record("scenario-turns", f"{label}: turn {turn_index} has invalid role")
                    if not isinstance(turn.get("text"), str) or not turn["text"].strip():
                        record("scenario-turns", f"{label}: turn {turn_index} has empty text")

            fixtures = scenario.get("fixtures")
            if not isinstance(fixtures, list):
                record("scenario-fixtures", f"{label}: fixtures must be a list")
            else:
                for fixture in fixtures:
                    if not isinstance(fixture, dict):
                        record("scenario-fixtures", f"{label}: fixture must be a mapping")
                        continue
                    extra = fixture.keys() - FIXTURE_KEYS
                    if extra:
                        record("scenario-fixtures", f"{label}: unknown fixture keys {sorted(extra)}")
                    if fixture.get("tool") not in known_tools:
                        record("scenario-fixtures", f"{label}: unknown tool {fixture.get('tool')!r}")
                    if not isinstance(fixture.get("status"), str):
                        record("scenario-fixtures", f"{label}: fixture status is required")

            expected = scenario.get("expected")
            if not isinstance(expected, dict):
                record("scenario-expected", f"{label}: expected must be a mapping")
                continue
            missing_expected = REQUIRED_EXPECTED - expected.keys()
            extra_expected = expected.keys() - EXPECTED_KEYS
            if missing_expected:
                record("scenario-expected", f"{label}: missing {sorted(missing_expected)}")
            if extra_expected:
                record("scenario-expected", f"{label}: unknown {sorted(extra_expected)}")

            if expected.get("language") not in LOCALES:
                record("scenario-expected", f"{label}: invalid language {expected.get('language')!r}")
            max_questions = expected.get("max_questions")
            if not isinstance(max_questions, int) or isinstance(max_questions, bool) or max_questions < 0:
                record("scenario-expected", f"{label}: max_questions must be an integer >= 0")
            for key in (
                "must_include_all",
                "must_include_any",
                "must_not_include",
                "must_not_regex",
                "required_tool_calls",
                "forbidden_tool_calls",
                "forbidden_tool_operations",
            ):
                value = expected.get(key, [])
                if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                    record("scenario-expected", f"{label}: {key} must be a list of strings")
            for tool in expected.get("required_tool_calls", []) or []:
                if tool not in known_tools:
                    record("scenario-expected", f"{label}: unknown required tool '{tool}'")
            for tool in expected.get("forbidden_tool_calls", []) or []:
                if tool not in known_tools:
                    record("scenario-expected", f"{label}: unknown forbidden tool '{tool}'")
            for operation in expected.get("forbidden_tool_operations", []) or []:
                if ":" not in operation or operation.split(":", 1)[0] not in known_tools:
                    record("scenario-expected", f"{label}: invalid forbidden operation '{operation}'")
            for pattern in expected.get("must_not_regex", []) or []:
                try:
                    re.compile(pattern, re.IGNORECASE)
                except re.error as exc:
                    record("scenario-expected", f"{label}: invalid regex {pattern!r}: {exc}")
            for key in ("should_handoff", "should_attempt_handoff", "should_stop", "should_disqualify", "human_review"):
                if not isinstance(expected.get(key), bool):
                    record("scenario-expected", f"{label}: {key} must be boolean")

            if scenario.get("locale") in {"ky", "mixed"} and expected.get("human_review") is not True:
                warn("scenario-review", f"{label}: Kyrgyz/mixed scenario is not flagged human_review")

            focus = scenario.get("rubric_focus")
            if not isinstance(focus, list) or len(focus) < 2:
                record("scenario-rubric", f"{label}: rubric_focus needs at least two dimensions")
            else:
                unknown = set(focus) - RUBRIC_DIMENSIONS
                if unknown:
                    record("scenario-rubric", f"{label}: unknown rubric dimensions {sorted(unknown)}")

    bump()
    duplicate_ids = [sid for sid, count in Counter(all_ids).items() if count > 1]
    if duplicate_ids:
        record("scenario-id", f"duplicate ids: {sorted(duplicate_ids)}")

    bump()
    if len(all_ids) < 40:
        record("scenario-count", f"only {len(all_ids)} scenarios; the requirement is at least 40")
    if len(all_ids) != EXPECTED_TOTAL:
        record("scenario-count", f"found {len(all_ids)} scenarios; coverage docs declare {EXPECTED_TOTAL}")

    bump()
    if category_counts != EXPECTED_CATEGORIES:
        record("scenario-count", f"category counts {category_counts} do not match {EXPECTED_CATEGORIES}")

    coverage_path = ROOT / "tests" / "COVERAGE.md"
    if coverage_path.is_file():
        coverage = coverage_path.read_text(encoding="utf-8")
        missing = [sid for sid in all_ids if sid not in coverage]
        bump()
        if missing:
            record("coverage", f"scenario ids missing from COVERAGE.md: {missing}")
        for category in EXPECTED_CATEGORIES:
            bump()
            if CATEGORY_LABELS[category].lower() not in coverage.lower():
                warn("coverage", f"category '{CATEGORY_LABELS[category]}' is not named in COVERAGE.md")


def check_state_schema() -> None:
    path = ROOT / "core" / "conversation-state.schema.json"
    schema = load_json(path)
    if schema is None:
        return
    try:
        Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError as exc:
        record("state-schema", f"{exc.message}")


def iter_markdown_files() -> Iterable[Path]:
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        yield path


def strip_fenced_blocks(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def check_links() -> None:
    pattern = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
    for path in iter_markdown_files():
        text = strip_fenced_blocks(path.read_text(encoding="utf-8"))
        for target in pattern.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            if target.startswith("//"):
                continue
            clean = target.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            bump()
            resolved = (path.parent / clean).resolve()
            if not resolved.exists():
                record("link", f"{path.relative_to(ROOT)}: broken link '{target}'")
            elif not str(resolved).startswith(str(ROOT)):
                warn("link", f"{path.relative_to(ROOT)}: link escapes repository '{target}'")


def check_placeholders_and_secrets() -> None:
    text_suffixes = {".md", ".json", ".yaml", ".yml", ".py", ".sh"}
    secret_patterns = [
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
        re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    ]
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in text_suffixes:
            continue
        relative = path.relative_to(ROOT)
        if relative.parts[0] == "scripts":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        bump()
        if re.search(r"\bTODO\b|\bFIXME\b|\bTBD\b", text):
            warn("placeholder", f"{path.relative_to(ROOT)}: contains TODO/FIXME/TBD")
        for pattern in secret_patterns:
            if pattern.search(text):
                record("secret", f"{path.relative_to(ROOT)}: matches {pattern.pattern}")


def check_gitignore() -> None:
    path = ROOT / ".gitignore"
    if not path.is_file():
        return
    content = path.read_text(encoding="utf-8")
    for entry in ("__pycache__/", "*.pyc", ".env", "tests/responses/"):
        bump()
        if entry not in content:
            warn("gitignore", f"missing recommended entry '{entry}'")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate repository structure, schemas, and scenarios.")
    parser.add_argument("--quiet", action="store_true", help="print only failures and the summary")
    args = parser.parse_args()

    if not (ROOT / "core").is_dir() or not (ROOT / "tests").is_dir():
        print(f"ERROR: {ROOT} does not look like the repository root", file=sys.stderr)
        return 2

    check_required_paths()
    check_skills()
    check_passports()
    check_tool_schemas()
    check_scenarios()
    check_state_schema()
    check_links()
    check_placeholders_and_secrets()
    check_gitignore()

    if not args.quiet:
        for warning in WARNINGS:
            print(f"WARN  {warning}")

    for error in ERRORS:
        print(f"FAIL  {error}")

    print()
    print(f"{CHECKS} checks; {len(ERRORS)} errors; {len(WARNINGS)} warnings")
    if ERRORS:
        print("Repository validation FAILED")
        return 1
    print("Repository validation passed (structural only; no model or tool was called)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
