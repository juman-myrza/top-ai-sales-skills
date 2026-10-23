#!/usr/bin/env python3
"""Install the skills into a temporary home and verify the installed artifact.

This catches the packaging defect from the 2026-10-23 audit: a skill installed
alone lost its linked core contract, tool contracts, and passport schema. The
test runs the real installer with ``--apply`` against a temporary directory,
then checks that every installed skill is self-contained.

It never touches the live ``~/.hermes`` profile and never calls a model.

Exit codes:
    0  the installed artifact is complete
    1  a check failed
    2  the installer or test could not run
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = [
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
REQUIRED_BUNDLE = [
    "core/CORE-BEHAVIOR-CONTRACT.md",
    "core/CONFLICT-RESOLUTION.md",
    "core/CONVERSATION-STATE.md",
    "core/conversation-state.schema.json",
    "product-passport/passport.schema.json",
    "product-passport/README.md",
    "tools/README.md",
    "tools/contracts/passport-lookup.md",
    "tools/contracts/calendar-availability.md",
    "tools/contracts/calendar-booking.md",
    "tools/contracts/payments-invoicing.md",
    "tools/contracts/crm-memory.md",
    "tools/contracts/human-handoff.md",
    "tools/contracts/messaging-media.md",
]
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
BUNDLE_ROOT = Path("references") / "shared"


def directory_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(item.read_bytes())
    return digest.hexdigest()


def strip_fences(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def check_links(skill_dir: Path) -> list[str]:
    failures: list[str] = []
    shared_root = skill_dir / BUNDLE_ROOT
    for path in sorted(skill_dir.rglob("*.md")):
        if shared_root in path.parents or path == shared_root:
            continue
        text = strip_fences(path.read_text(encoding="utf-8"))
        for target in LINK_PATTERN.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "tel:", "#", "//")):
                continue
            clean = target.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            if not (path.parent / clean).resolve().exists():
                failures.append(f"{path.relative_to(skill_dir.parent.parent)}: broken link {target!r}")
    return failures


def main() -> int:
    temp_root = Path(tempfile.mkdtemp(prefix="installed-artifact-", dir=os.environ.get("TMPDIR", "/tmp/opencode")))
    target = temp_root / "hermes-home"
    command = [
        sys.executable,
        str(ROOT / "scripts" / "install_skills.py"),
        "--target",
        str(target),
        "--apply",
        "--force",
        "--skip-validate",
        "--no-backup",
    ]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        print("FAIL  installer returned non-zero", file=sys.stderr)
        print(completed.stdout, file=sys.stderr)
        print(completed.stderr, file=sys.stderr)
        shutil.rmtree(temp_root, ignore_errors=True)
        return 2

    failures: list[str] = []
    skills_root = target / "skills" / "sales"
    for name in EXPECTED:
        skill_dir = skills_root / name
        if not skill_dir.is_dir():
            failures.append(f"missing installed skill: {name}")
            continue
        failures.extend(check_links(skill_dir))
        for relative in REQUIRED_BUNDLE:
            if not (skill_dir / BUNDLE_ROOT / relative).is_file():
                failures.append(f"{name}: missing bundled {relative}")

    if not (target / "activation" / "SYSTEM-PROMPT-SNIPPET.md").is_file():
        failures.append("activation/SYSTEM-PROMPT-SNIPPET.md is missing")
    if not (target / "ACTIVATION.md").is_file():
        failures.append("ACTIVATION.md is missing")

    manifest_path = target / "INSTALL-MANIFEST.json"
    if not manifest_path.is_file():
        failures.append("INSTALL-MANIFEST.json is missing")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for name in EXPECTED:
            entry = manifest.get("skills", {}).get(name)
            if not entry:
                failures.append(f"manifest missing entry for {name}")
                continue
            actual = directory_hash(skills_root / name)
            if entry.get("sha256") != actual:
                failures.append(f"{name}: manifest hash does not match installed files")

    shutil.rmtree(temp_root, ignore_errors=True)

    if failures:
        for failure in failures:
            print(f"FAIL  {failure}", file=sys.stderr)
        print(f"\nInstalled artifact check FAILED ({len(failures)} issue(s))")
        return 1

    print(f"OK  installed artifact is self-contained ({len(EXPECTED)} skills, {len(REQUIRED_BUNDLE)} bundled references each)")
    print("The live profile was not read or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
