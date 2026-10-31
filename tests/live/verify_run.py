#!/usr/bin/env python3
"""Reproduce a recorded run's prompt hash from its recorded git commit.

Each run writes ``run-*.json`` with ``repo_commit`` and ``prompt_sha256``. This
script rebuilds the system prompt from the files as they exist at that commit
(via ``git show``) and checks that the SHA-256 matches. It proves that the
committed artifacts correspond to a specific commit, independent of any dirty
working tree, so a reviewer can tie the report to the code it evaluated.

Usage:
    python3 tests/live/verify_run.py tests/live/results/baseline/run-*.json
    python3 tests/live/verify_run.py --all

Exit codes:
    0  every checked run reproduced its prompt hash
    1  a mismatch or a missing commit
    2  the script could not run (git unavailable, bad arguments)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from prompt_build import build  # noqa: E402


def git_show(ref: str, rel: str) -> str:
    completed = subprocess.run(
        ["git", "show", f"{ref}:{rel}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise FileNotFoundError(f"{ref}:{rel} not found ({completed.stderr.strip()[:120]})")
    return completed.stdout


def check_run(run_path: Path) -> tuple[bool, str]:
    meta = json.loads(run_path.read_text(encoding="utf-8"))
    ref = meta.get("repo_commit")
    recorded = meta.get("prompt_sha256")
    if not ref or not recorded:
        return False, f"{run_path.name}: missing repo_commit or prompt_sha256"
    try:
        parts = prompt_parts_for_ref(ref)
        prompt = build(parts, lambda rel: git_show(ref, rel))
    except FileNotFoundError as exc:
        return False, f"{run_path.name}: {exc}"
    actual = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    if actual != recorded:
        return (
            False,
            f"{run_path.name}: prompt hash mismatch at {ref[:12]}\n"
            f"    recorded {recorded}\n    rebuilt  {actual}",
        )
    return True, f"{run_path.name}: OK ({ref[:12]}, {recorded[:12]})"


def prompt_parts_for_ref(ref: str) -> list[str]:
    """Like prompt_parts() but enumerating blobs at a git ref, not on disk."""
    parts = [
        "core/CORE-BEHAVIOR-CONTRACT.md",
        "core/CONFLICT-RESOLUTION.md",
        "core/CONVERSATION-STATE.md",
    ]
    listing = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if listing.returncode != 0:
        raise FileNotFoundError(f"cannot list tree for {ref}")
    paths = listing.stdout.splitlines()
    parts.extend(
        sorted(p for p in paths if p.startswith("skills/sales/") and p.endswith("/SKILL.md"))
    )
    parts.extend(
        sorted(p for p in paths if p.startswith("skills/sales/") and "/references/" in p and p.endswith(".md"))
    )
    parts.extend(
        sorted(
            p
            for p in paths
            if p.startswith("tenants/daniyar/passports/offers/") and p.endswith(".json")
        )
    )
    return parts


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify recorded run prompt hashes against their commits.")
    parser.add_argument("runs", nargs="*", type=Path, help="run-*.json files to verify")
    parser.add_argument("--all", action="store_true", help="verify every run under tests/live/results/")
    args = parser.parse_args()

    if args.all:
        runs = sorted((HERE / "results").rglob("run-*.json"))
    else:
        runs = args.runs
    if not runs:
        print("ERROR: pass run-*.json files or --all", file=sys.stderr)
        return 2

    ok = True
    for run in runs:
        passed, message = check_run(run)
        print(("OK   " if passed else "FAIL ") + message)
        ok = ok and passed
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
