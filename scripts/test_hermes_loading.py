#!/usr/bin/env python3
"""Verify that Hermes discovers the nine skills in an isolated home.

The script copies `skills/sales/*` into a temporary `HERMES_HOME` and runs
`hermes skills list --source local`. It never uses or writes the live
`~/.hermes` profile and never starts an agent or a model.

Hermes may prepare Python dependencies the first time it sees a new data
root. That can take a few minutes and requires network access.

Exit codes:
    0  all skills discovered, or Hermes absent and --require not set
    1  a skill was not discovered or the command failed
    2  invalid arguments / no skills to test
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills" / "sales"

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


def find_hermes(explicit: str | None) -> str | None:
    if explicit:
        return explicit if Path(explicit).exists() else None
    return shutil.which("hermes")


def main() -> int:
    parser = argparse.ArgumentParser(description="Load the skills with an isolated Hermes home.")
    parser.add_argument("--hermes", help="path to the hermes executable")
    parser.add_argument("--timeout", type=int, default=300, help="seconds to wait for Hermes (default 300)")
    parser.add_argument("--require", action="store_true", help="fail instead of skipping when Hermes is absent")
    parser.add_argument("--keep", action="store_true", help="keep the temporary HERMES_HOME")
    args = parser.parse_args()

    skills = [path for path in sorted(SKILLS_DIR.glob("*/SKILL.md"))]
    if len(skills) != len(EXPECTED):
        print(f"ERROR: expected {len(EXPECTED)} skills under {SKILLS_DIR}, found {len(skills)}", file=sys.stderr)
        return 2

    hermes = find_hermes(args.hermes)
    if hermes is None:
        message = "Hermes executable not found; isolated loading was NOT tested."
        if args.require:
            print(f"FAIL  {message}", file=sys.stderr)
            return 1
        print(f"SKIPPED  {message}")
        return 0

    temp_root = Path(tempfile.mkdtemp(prefix="hermes-skills-", dir=os.environ.get("TMPDIR", "/tmp/opencode")))
    home = temp_root
    destination = home / "skills" / "sales"
    destination.mkdir(parents=True)
    for skill_md in skills:
        shutil.copytree(skill_md.parent, destination / skill_md.parent.name)

    env = os.environ.copy()
    env.update(
        {
            "HERMES_HOME": str(home),
            "COLUMNS": "200",
            "NO_COLOR": "1",
            "TERM": "dumb",
            "PYTHONUNBUFFERED": "1",
        }
    )
    command = [hermes, "skills", "list", "--source", "local"]

    print(f"Isolated HERMES_HOME: {home}")
    print(f"Command: {' '.join(command)}")
    try:
        completed = subprocess.run(
            command,
            env=env,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"FAIL  Hermes did not finish within {args.timeout}s", file=sys.stderr)
        print(f"      temporary home kept at {home}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"FAIL  could not execute Hermes: {exc}", file=sys.stderr)
        return 1

    output = completed.stdout + "\n" + completed.stderr
    if completed.returncode != 0:
        print(f"FAIL  Hermes exited with {completed.returncode}", file=sys.stderr)
        print(output.strip()[:6000], file=sys.stderr)
        print(f"      temporary home kept at {home}", file=sys.stderr)
        return 1

    missing: list[str] = []
    for name in EXPECTED:
        line_match = re.search(
            rf"^\s*[│|]\s*{re.escape(name)}\s*[│|]\s*sales\s*[│|].*local",
            completed.stdout,
            re.MULTILINE,
        )
        if not line_match:
            missing.append(name)

    if missing:
        print(f"FAIL  not discovered: {', '.join(missing)}", file=sys.stderr)
        print(output.strip()[:6000], file=sys.stderr)
        print(f"      temporary home kept at {home}", file=sys.stderr)
        return 1

    print(f"OK  Hermes discovered all {len(EXPECTED)} skills in the isolated home")
    print("The live profile was not read or modified.")

    if args.keep:
        print(f"Kept temporary home: {home}")
    else:
        shutil.rmtree(temp_root, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
