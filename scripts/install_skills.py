#!/usr/bin/env python3
"""Install the nine skills into a Hermes profile, with a dry run by default.

Default target: ~/.hermes  (skills go to ~/.hermes/skills/sales/<name>/)
Nothing is written unless --apply is passed.

Existing skill directories are skipped unless --force is passed. When a
directory is replaced, it is copied to a timestamped backup first.

This script installs instruction files only. It does not install or configure
tool adapters, credentials, cron jobs, or a model.
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "skills" / "sales"
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


def validate_source() -> bool:
    missing = [name for name in EXPECTED if not (SOURCE / name / "SKILL.md").is_file()]
    if missing:
        print(f"ERROR: missing skill files: {', '.join(missing)}", file=sys.stderr)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Install sales skills into a Hermes home.")
    parser.add_argument(
        "--target",
        type=Path,
        default=Path.home() / ".hermes",
        help="Hermes home directory (default: ~/.hermes)",
    )
    parser.add_argument("--apply", action="store_true", help="write changes; default is a dry run")
    parser.add_argument("--force", action="store_true", help="replace existing skill directories")
    parser.add_argument("--no-backup", action="store_true", help="skip backups when replacing")
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="skip scripts/validate_repository.py before installing",
    )
    args = parser.parse_args()

    if not validate_source():
        return 2

    target = args.target.expanduser().resolve()
    if target == ROOT or ROOT in target.parents:
        print("ERROR: refusing to install inside the repository itself", file=sys.stderr)
        return 2
    destination = target / "skills" / "sales"

    if not args.skip_validate:
        validation = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_repository.py"), "--quiet"],
            cwd=ROOT,
            check=False,
        )
        if validation.returncode != 0:
            print("ERROR: repository validation failed; not installing", file=sys.stderr)
            return 1

    print(f"Target: {destination}")
    print("Mode: " + ("APPLY" if args.apply else "DRY RUN (pass --apply to write)"))

    actions: list[tuple[str, str]] = []
    for name in EXPECTED:
        exists = (destination / name).exists()
        action = "replace" if exists and args.force else "skip (exists; use --force)" if exists else "create"
        actions.append((name, action))
        print(f"  {action:<32} {name}")

    if not args.apply:
        print("\nDry run complete. No files were written.")
        return 0

    destination.mkdir(parents=True, exist_ok=True)
    stage = destination / f".staging-{uuid.uuid4().hex}"
    stage.mkdir()
    backup_root = None
    replaced = [name for name, action in actions if action == "replace"]
    if replaced and not args.no_backup:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_root = destination / f".backup-{stamp}"
        backup_root.mkdir()
        for name in replaced:
            shutil.copytree(destination / name, backup_root / name)
        print(f"Backup: {backup_root}")

    try:
        for name, action in actions:
            if action.startswith("skip"):
                continue
            shutil.copytree(SOURCE / name, stage / name)
        for name, action in actions:
            if action.startswith("skip"):
                continue
            final = destination / name
            if final.exists():
                shutil.rmtree(final)
            shutil.move(str(stage / name), str(final))
    except OSError as exc:
        print(f"ERROR: installation failed: {exc}", file=sys.stderr)
        if backup_root is not None:
            print(f"Backups are available at {backup_root}", file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(stage, ignore_errors=True)

    print(f"\nInstalled {sum(1 for _, action in actions if not action.startswith('skip'))} skill(s).")
    print("Check discovery with: hermes skills list --source local")
    print("The target profile still needs passport data and tool adapters before production use.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
