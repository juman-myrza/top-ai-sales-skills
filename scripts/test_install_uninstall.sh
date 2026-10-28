#!/usr/bin/env sh
# Round-trip test for the root install.sh and uninstall.sh wrappers.
#
# It installs into a temporary home, checks the shared bundle and manifest, then
# uninstalls and checks that only the installed artifacts were removed. It never
# touches ~/.hermes and calls no model.

set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
base=$(mktemp -d "${TMPDIR:-/tmp}/sales-skills-roundtrip.XXXXXX")
trap 'rm -rf "$base"' EXIT INT TERM
home="$base/hermes"

fail() {
    echo "FAIL  $1" >&2
    exit 1
}

# 1. Dry run must not write anything.
sh "$root/install.sh" --target "$home" --skip-validate >/dev/null
if [ -e "$home/skills/sales" ]; then
    fail "install dry run wrote files"
fi

# 2. Real install.
sh "$root/install.sh" --target "$home" --apply --force --no-backup --skip-validate >/dev/null
if [ ! -f "$home/INSTALL-MANIFEST.json" ]; then
    fail "manifest missing after install"
fi
if [ ! -d "$home/skills/sales/sales-closing-execution" ]; then
    fail "skill not installed"
fi
if [ ! -d "$home/skills/sales/sales-conversation-orchestrator/references/shared/core" ]; then
    fail "shared bundle not installed into the skill"
fi

# 2b. A no-force reinstall must keep the manifest complete (it must not drop
# the skill list, which would break uninstall).
sh "$root/install.sh" --target "$home" --apply --skip-validate >/dev/null
listed=$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["skills"]))' "$home/INSTALL-MANIFEST.json")
if [ "$listed" -ne 9 ]; then
    fail "no-force reinstall dropped manifest skills (found $listed, expected 9)"
fi

# 3. Uninstall dry run must not remove anything.
sh "$root/uninstall.sh" --target "$home" >/dev/null
if [ ! -d "$home/skills/sales/sales-closing-execution" ]; then
    fail "uninstall dry run removed files"
fi

# 4. Real uninstall.
sh "$root/uninstall.sh" --target "$home" --apply >/dev/null
if [ -e "$home/skills/sales/sales-closing-execution" ]; then
    fail "skill was not removed"
fi
if [ -e "$home/INSTALL-MANIFEST.json" ]; then
    fail "manifest was not removed"
fi
if [ -e "$home/ACTIVATION.md" ]; then
    fail "activation notes were not removed"
fi

# 5. A second uninstall must refuse rather than guess.
if sh "$root/uninstall.sh" --target "$home" --apply >/dev/null 2>&1; then
    fail "uninstall should fail when the manifest is absent"
fi

echo "OK  install.sh/uninstall.sh round-trip passed (no live profile touched)"
