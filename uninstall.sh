#!/usr/bin/env sh
# Remove the universal sales skills that install.sh placed in a Hermes home.
#
# Dry run by default: nothing is removed unless --apply is passed.
# The uninstaller is manifest-driven. It reads INSTALL-MANIFEST.json and removes
# only the skill directories that manifest lists, plus the activation files and
# the manifest itself. It never touches other skills, the target root, or any
# backup directory unless --purge-backups is passed.
#
# Usage:
#   ./uninstall.sh --target ~/.hermes --apply
#   curl -fsSL https://raw.githubusercontent.com/juman-myrza/top-ai-sales-skills/main/uninstall.sh \
#     | sh -s -- --apply
#
# Environment:
#   HERMES_HOME   target home when --target is not given (default: ~/.hermes)

set -eu

TARGET="${HERMES_HOME:-$HOME/.hermes}"
APPLY=0
PURGE_BACKUPS=0

usage() {
    cat <<'EOF'
Remove the universal sales skills installed by install.sh.

  uninstall.sh [--target DIR] [--apply] [--purge-backups]

Defaults:
  target   ~/.hermes (or $HERMES_HOME)
  mode     dry run (pass --apply to remove)

The removal list comes from INSTALL-MANIFEST.json in the target. If the
manifest is missing, the script refuses to guess. Backups created by the
installer (.backup-*) are left in place unless --purge-backups is passed.
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --target)
            [ "$#" -ge 2 ] || { echo "ERROR: --target needs a directory." >&2; exit 2; }
            TARGET="$2"
            shift 2
            ;;
        --target=*)
            TARGET="${1#--target=}"
            shift
            ;;
        --apply)
            APPLY=1
            shift
            ;;
        --dry-run)
            APPLY=0
            shift
            ;;
        --purge-backups)
            PURGE_BACKUPS=1
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "ERROR: unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [ -z "$TARGET" ] || [ "$TARGET" = "/" ]; then
    echo "ERROR: refusing to operate on an empty or root target." >&2
    exit 2
fi
if [ ! -d "$TARGET" ]; then
    echo "Nothing to do: $TARGET does not exist."
    exit 0
fi

manifest="$TARGET/INSTALL-MANIFEST.json"
if [ ! -f "$manifest" ]; then
    echo "ERROR: no INSTALL-MANIFEST.json in $TARGET." >&2
    echo "       Refusing to guess what to remove. If the skills were installed" >&2
    echo "       without the manifest, remove them manually." >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required to read the install manifest." >&2
    exit 2
fi

names=$(python3 -c '
import json, sys
with open(sys.argv[1], encoding="utf-8") as handle:
    manifest = json.load(handle)
skills = manifest.get("skills", {})
for name in sorted(skills):
    print(name)
' "$manifest")

skills_root="$TARGET/skills/sales"

echo "Target:  $TARGET"
echo "Skills:  ${names:-<none listed>}"
echo "Mode:    $([ "$APPLY" -eq 1 ] && echo APPLY || echo 'DRY RUN (pass --apply to remove)')"
echo

if [ "$APPLY" -eq 0 ]; then
    echo "Would remove:"
    old_ifs=$IFS
    IFS='
'
    for name in $names; do
        case "$name" in
            ""|*/*|.*)
                echo "  skip (unsafe name): $name"
                continue
                ;;
        esac
        echo "  $skills_root/$name"
    done
    IFS=$old_ifs
    echo "  $TARGET/activation/"
    echo "  $TARGET/ACTIVATION.md"
    echo "  $TARGET/INSTALL-MANIFEST.json"
    echo
    echo "Dry run complete. No files were removed."
    exit 0
fi

old_ifs=$IFS
IFS='
'
for name in $names; do
    case "$name" in
        ""|*/*|.*)
            echo "skip (unsafe name): $name" >&2
            continue
            ;;
    esac
    dir="$skills_root/$name"
    if [ -d "$dir" ]; then
        rm -rf -- "$dir"
        echo "removed $dir"
    fi
done
IFS=$old_ifs

if [ -f "$TARGET/activation/SYSTEM-PROMPT-SNIPPET.md" ]; then
    rm -f -- "$TARGET/activation/SYSTEM-PROMPT-SNIPPET.md"
fi
rmdir "$TARGET/activation" 2>/dev/null || true
rm -f -- "$TARGET/ACTIVATION.md"
rm -f -- "$TARGET/INSTALL-MANIFEST.json"

# Remove now-empty sales/skills directories, but never the target itself.
rmdir "$skills_root" 2>/dev/null || true
rmdir "$TARGET/skills" 2>/dev/null || true

backups=$(find "$skills_root" -maxdepth 1 -type d \( -name '.backup-*' -o -name '.staging-*' \) 2>/dev/null || true)
if [ -n "$backups" ]; then
    if [ "$PURGE_BACKUPS" -eq 1 ]; then
        echo "$backups" | while IFS= read -r backup; do
            [ -n "$backup" ] && rm -rf -- "$backup" && echo "purged $backup"
        done
    else
        echo
        echo "Backups were left in place:"
        echo "$backups" | while IFS= read -r backup; do
            [ -n "$backup" ] && echo "  $backup"
        done
        echo "Pass --purge-backups to remove them."
    fi
fi

echo
echo "Uninstall complete."
