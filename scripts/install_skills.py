#!/usr/bin/env python3
"""Install the nine skills into a Hermes profile, with a dry run by default.

Default target: ~/.hermes  (skills go to ~/.hermes/skills/sales/<name>/)
For one specific agent (Hermes profile), target that profile home instead:
    --target ~/.hermes/profiles/<name>  ->  ~/.hermes/profiles/<name>/skills/sales/<name>/
Nothing is written unless --apply is passed.

The universal skills depend on shared documents (the core behavior contract,
the tool contracts, the passport schema, and the research notes). Hermes only
serves files inside a skill directory, so this installer copies those shared
documents into each installed skill under `references/shared/` and rewrites the
repository-relative links in each skill to point at that bundle. The result is a
self-contained skill directory that still resolves its dependencies when the
repository checkout is gone.

Existing skill directories are skipped unless --force is passed. When a
directory is replaced, it is copied to a timestamped backup first.

This script installs instruction files and an activation template only. It does
not install or configure tool adapters, credentials, cron jobs, or a model.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
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

# Directories bundled into every skill under references/shared/. Keep this
# intentionally narrow: durable reference material, not tests or tooling.
BUNDLE_DIRS = ["core", "tools", "product-passport", "research"]
BUNDLE_ROOT = Path("references") / "shared"

LINK_PATTERN = re.compile(r"(!?\[[^\]]*\]\()([^)\s]+)((?:\s+['\"][^'\"]*['\"])?\))")


def validate_source() -> bool:
    missing = [name for name in EXPECTED if not (SOURCE / name / "SKILL.md").is_file()]
    if not missing:
        return True
    print(f"ERROR: missing skill files: {', '.join(missing)}", file=sys.stderr)
    return False


def repo_relative_target(source_file: Path, target: str) -> str | None:
    """Return the repo-relative path for a local link, or None if not bundled."""
    if target.startswith(("http://", "https://", "mailto:", "tel:", "#", "//")):
        return None
    clean = target.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return None
    resolved = (source_file.parent / clean).resolve()
    try:
        relative = resolved.relative_to(ROOT)
    except ValueError:
        return None
    if not resolved.is_file():
        return None
    if relative.parts[0] not in BUNDLE_DIRS:
        return None
    return relative.as_posix()


def rewrite_links(text: str, source_file: Path, installed_file: Path, skill_root: Path) -> str:
    """Rewrite bundled repo-relative links to point at references/shared/."""

    def replace(match: re.Match[str]) -> str:
        prefix, target, suffix = match.group(1), match.group(2), match.group(3)
        relative = repo_relative_target(source_file, target)
        if relative is None:
            return match.group(0)
        fragment = ""
        if "#" in target:
            fragment = "#" + target.split("#", 1)[1]
        destination = skill_root / BUNDLE_ROOT / relative
        rewritten = Path(os.path.relpath(destination, installed_file.parent)).as_posix()
        return f"{prefix}{rewritten}{fragment}{suffix}"

    return LINK_PATTERN.sub(replace, text)


def iter_rewritable_files(skill_dir: Path):
    shared_root = skill_dir / BUNDLE_ROOT
    for path in sorted(skill_dir.rglob("*.md")):
        if not path.is_file():
            continue
        if shared_root in path.parents or path == shared_root:
            continue
        yield path


# Historical audits and internal repository theatre are not runtime dependencies.
BUNDLE_EXCLUDE = {"audits"}


def copy_shared_bundle(skill_dir: Path) -> int:
    destination = skill_dir / BUNDLE_ROOT
    destination.mkdir(parents=True, exist_ok=True)
    count = 0
    for name in BUNDLE_DIRS:
        source = ROOT / name
        if not source.is_dir():
            continue
        target = destination / name
        shutil.copytree(
            source,
            target,
            ignore=lambda directory, names: [n for n in names if n in BUNDLE_EXCLUDE],
        )
        count += sum(1 for _ in target.rglob("*") if _.is_file())
    return count


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def directory_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(item.read_bytes())
    return digest.hexdigest()


def git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and commit else None


def core_contract_version() -> str | None:
    """Read the declared version from the core behavior contract, if present."""
    path = ROOT / "core" / "CORE-BEHAVIOR-CONTRACT.md"
    if not path.is_file():
        return None
    match = re.search(r"\*\*Version:\*\*\s*([0-9]+\.[0-9]+\.[0-9]+)", path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def shared_manifest() -> dict:
    """Version and hash the shared resources so an evaluation can pin them."""
    tracked = [
        "core/CORE-BEHAVIOR-CONTRACT.md",
        "core/SYSTEM-PROMPT-SNIPPET.md",
        "core/conversation-state.schema.json",
        "product-passport/passport.schema.json",
        "tools/schemas/tool-envelope.schema.json",
    ]
    files = {}
    for relative in tracked:
        path = ROOT / relative
        if path.is_file():
            files[relative] = sha256(path)
    return {
        "core_contract_version": core_contract_version(),
        "system_prompt_snippet_sha256": files.get("core/SYSTEM-PROMPT-SNIPPET.md"),
        "files": files,
    }


def build_manifest(skill_dirs: dict[str, Path], target: Path) -> dict:
    return {
        "manifest_version": "1.0.0",
        "installed_at": dt.datetime.now().isoformat(timespec="seconds"),
        "source_repository": str(ROOT),
        "source_commit": git_commit(),
        "target": str(target),
        "bundle_dirs": BUNDLE_DIRS,
        "shared": shared_manifest(),
        "skills": {
            name: {
                "path": str((Path("skills") / "sales" / name).as_posix()),
                "sha256": directory_hash(path),
                "files": sum(1 for _ in path.rglob("*") if _.is_file()),
            }
            for name, path in sorted(skill_dirs.items())
        },
    }


ACTIVATION = """# Activation

These skills are inert instruction files. They do not connect a model, a
calendar, a payment provider, or a CRM by themselves. Complete these steps
before production use.

## 1. Load the always-on contract

Add the contents of [`activation/SYSTEM-PROMPT-SNIPPET.md`](activation/SYSTEM-PROMPT-SNIPPET.md)
to the agent's system prompt. It carries the truth, consent, tool-verification,
and refusal invariants. Do not paste the nine skill bodies into the system
prompt; load them as skills on demand.

## 2. Approve and connect one passport

The skills contain no business facts. Create one passport per offer from
[`product-passport/TEMPLATE.md`](skills/sales/sales-conversation-orchestrator/references/shared/product-passport/TEMPLATE.md),
validate it against the schema, mark it `approved`, and expose it through the
`passport.lookup` contract. The bundled copy of the passport schema and examples
lives under each skill's `references/shared/product-passport/` directory.

## 3. Do not skip the tool layer

Every booking, payment, message, follow-up schedule, CRM write, and handoff is
gated by a tool contract. Until an adapter exists, the agent must not claim the
action succeeded. The bundled contracts live under
`references/shared/tools/contracts/` in each skill.

## 4. Review the shared bundle

Each installed skill carries a copy of `core/`, `tools/`,
`product-passport/`, and `research/` under `references/shared/`. The links in
each `SKILL.md` were rewritten to point there at install time. If you edit a
shared document, update the source repository and reinstall; editing one
skill's copy will drift from the others.

## 5. Verify discovery

Run `hermes skills list --source local` against the target home. The repository
also provides `scripts/test_installed_artifact.py` to check that every installed
skill resolves its links and includes the shared contract.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Install sales skills into a Hermes home.")
    parser.add_argument(
        "--target",
        type=Path,
        default=Path.home() / ".hermes",
        help="Hermes home directory (default: ~/.hermes). For one profile, pass ~/.hermes/profiles/<name>",
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
    print(f"Shared bundle: {', '.join(BUNDLE_DIRS)} -> each skill's {BUNDLE_ROOT.as_posix()}/")
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

    installed: dict[str, Path] = {}
    try:
        for name, action in actions:
            if action.startswith("skip"):
                continue
            staged_skill = stage / name
            shutil.copytree(SOURCE / name, staged_skill)
            copy_shared_bundle(staged_skill)
            for file_path in iter_rewritable_files(staged_skill):
                original = file_path.read_text(encoding="utf-8")
                rewritten = rewrite_links(original, SOURCE / name / file_path.relative_to(staged_skill), file_path, staged_skill)
                if rewritten != original:
                    file_path.write_text(rewritten, encoding="utf-8")
            installed[name] = staged_skill

        for name, action in actions:
            if action.startswith("skip"):
                continue
            final = destination / name
            if final.exists():
                shutil.rmtree(final)
            shutil.move(str(stage / name), str(final))

        # Operator-facing artifacts live at the target root.
        activation_dir = target / "activation"
        activation_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "core" / "SYSTEM-PROMPT-SNIPPET.md", activation_dir / "SYSTEM-PROMPT-SNIPPET.md")
        (target / "ACTIVATION.md").write_text(ACTIVATION, encoding="utf-8")

        manifest = build_manifest({name: destination / name for name in installed}, target)
        (target / "INSTALL-MANIFEST.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        print(f"ERROR: installation failed: {exc}", file=sys.stderr)
        if backup_root is not None:
            print(f"Backups are available at {backup_root}", file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(stage, ignore_errors=True)

    print(f"\nInstalled {sum(1 for _, action in actions if not action.startswith('skip'))} skill(s).")
    print(f"Manifest: {target / 'INSTALL-MANIFEST.json'}")
    print(f"Activation notes: {target / 'ACTIVATION.md'}")
    print("Check discovery with: hermes skills list --source local")
    print("The target profile still needs passport data and tool adapters before production use.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
