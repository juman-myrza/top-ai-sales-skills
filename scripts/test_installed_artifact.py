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
    # The profile owns passports/state/, and the mirror lives in the repo; the
    # installer must never write either.
    for forbidden in ("passports", "state", "tenants"):
        if (target / forbidden).exists():
            failures.append(f"install must not create <target>/{forbidden}")
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

    if not (target / "ACTIVATION.md").is_file():
        failures.append("ACTIVATION.md is missing")

    manifest_path = target / "INSTALL-MANIFEST.json"
    if not manifest_path.is_file():
        failures.append("INSTALL-MANIFEST.json is missing")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        shared = manifest.get("shared", {})
        if not shared.get("core_contract_version"):
            failures.append("manifest does not record shared.core_contract_version")
        for relative in ("core/CORE-BEHAVIOR-CONTRACT.md", "product-passport/passport.schema.json"):
            recorded = shared.get("files", {}).get(relative)
            if not recorded:
                failures.append(f"manifest does not record a hash for {relative}")
            elif recorded != hashlib.sha256((ROOT / relative).read_bytes()).hexdigest():
                failures.append(f"manifest hash for {relative} does not match the source repository")
        # OC-1 fallback: every skill must carry the identical canonical bundle.
        bundle = shared.get("bundle_files", {})
        if not isinstance(bundle, dict) or not bundle:
            failures.append("manifest does not record shared.bundle_files")
        elif shared.get("bundle_file_count") != len(bundle):
            failures.append("manifest shared.bundle_file_count does not match shared.bundle_files")
        else:
            for name in EXPECTED:
                skill_dir = skills_root / name
                if not skill_dir.is_dir():
                    continue
                installed_bundle = skill_dir / BUNDLE_ROOT
                installed_rel = (
                    {p.relative_to(installed_bundle).as_posix() for p in installed_bundle.rglob("*") if p.is_file()}
                    if installed_bundle.is_dir()
                    else set()
                )
                for relative in sorted(set(bundle) - installed_rel):
                    failures.append(f"{name}: missing bundled {relative}")
                for relative in sorted(installed_rel - set(bundle)):
                    failures.append(f"{name}: unexpected bundled file {relative}")
                for relative, expected_hash in sorted(bundle.items()):
                    copied = installed_bundle / relative
                    if copied.is_file():
                        actual_hash = hashlib.sha256(copied.read_bytes()).hexdigest()
                        if actual_hash != expected_hash:
                            failures.append(f"{name}: bundled {relative} differs from the canonical source")
        for name in EXPECTED:
            entry = manifest.get("skills", {}).get(name)
            if not entry:
                failures.append(f"manifest missing entry for {name}")
                continue
            actual = directory_hash(skills_root / name)
            if entry.get("sha256") != actual:
                failures.append(f"{name}: manifest hash does not match installed files")

    # OC-6: the sales skills must not require operator-only tools.
    forbidden_tool_words = (
        "terminal", "code_execution", "cronjob", "computer_use", "browser",
        "execute_code", "delegate_task",
    )
    shared_marker = BUNDLE_ROOT.as_posix()
    for path in sorted((target / "skills").rglob("*.md")):
        rel = path.relative_to(target / "skills").as_posix()
        if shared_marker in rel:  # the bundled references are not the skills' own text
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for word in forbidden_tool_words:
            if word in text:
                failures.append(f"{rel}: references operator-only tool {word!r}")

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
