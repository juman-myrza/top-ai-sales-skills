#!/usr/bin/env sh
# Install the universal sales skills into a Hermes home.
#
# Dry run by default: nothing is written unless --apply is passed.
# This is a thin wrapper around scripts/install_skills.py. It exists so the
# repository can be installed from a checkout or bootstrapped from a clone.
#
# Usage:
#   ./install.sh --target ~/.hermes --apply
#   curl -fsSL https://raw.githubusercontent.com/juman-myrza/top-ai-sales-skills/main/install.sh \
#     | sh -s -- --apply
#
# Environment:
#   SALES_SKILLS_REPO   git URL used when bootstrapping (default: this repo)
#   SALES_SKILLS_REF    branch/tag used when bootstrapping (default: main)
#
# All other arguments are forwarded to scripts/install_skills.py, which supports
# --target, --apply, --force, --no-backup, and --skip-validate.

set -eu

REPO_URL="${SALES_SKILLS_REPO:-https://github.com/juman-myrza/top-ai-sales-skills.git}"
REF="${SALES_SKILLS_REF:-main}"

usage() {
    cat <<'EOF'
Install the universal sales skills into a Hermes home.

  install.sh [--target DIR] [--apply] [--force] [--no-backup] [--skip-validate]

Defaults:
  target   ~/.hermes
  mode     dry run (pass --apply to write)

Bootstrapping (curl | sh):
  --ref=BRANCH   branch, tag, or commit to clone (default: main)

The installer writes only inside the target home. It backs up replaced skill
directories unless --no-backup is passed. Validation needs Python 3.11+ with
PyYAML and jsonschema; pass --skip-validate to install without them.
EOF
}

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required (3.11 or newer)." >&2
    exit 2
fi

# Strip --ref=... from the arguments we forward; keep everything else as-is.
filtered=""
sep=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        --ref)
            echo "ERROR: use --ref=BRANCH (with an equals sign)." >&2
            exit 2
            ;;
        --ref=*)
            REF="${1#--ref=}"
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            filtered="${filtered}${sep}${1}"
            sep='
'
            ;;
    esac
    shift
done

if [ -n "$filtered" ]; then
    _old_ifs=$IFS
    IFS='
'
    set -f
    # shellcheck disable=SC2086
    set -- $filtered
    set +f
    IFS=$_old_ifs
else
    set --
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd || true)
repo_dir=""
cleanup_dir=""

if [ -n "$script_dir" ] && [ -f "$script_dir/scripts/install_skills.py" ]; then
    repo_dir="$script_dir"
else
    # Piped or copied elsewhere: clone the repository, because the installer
    # needs the whole checkout (shared core/, tools/, passport, schemas).
    if ! command -v git >/dev/null 2>&1; then
        echo "ERROR: git is required to bootstrap the installer when it is not run from a checkout." >&2
        echo "       Clone the repository manually, then run ./install.sh from its root." >&2
        exit 2
    fi
    cleanup_dir=$(mktemp -d "${TMPDIR:-/tmp}/sales-skills-install.XXXXXX")
    # shellcheck disable=SC2064
    trap 'rm -rf "$cleanup_dir"' EXIT INT TERM

    echo "Bootstrapping: $REPO_URL ($REF)"
    if ! git clone --depth 1 --branch "$REF" "$REPO_URL" "$cleanup_dir/repo" >/dev/null 2>&1; then
        echo "ERROR: could not clone $REPO_URL at ref '$REF'." >&2
        exit 1
    fi
    repo_dir="$cleanup_dir/repo"
fi

python3 "$repo_dir/scripts/install_skills.py" "$@"
