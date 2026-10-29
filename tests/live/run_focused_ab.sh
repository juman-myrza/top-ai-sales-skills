#!/usr/bin/env bash
set -euo pipefail

# Focused A/B evaluation for the two guardrails introduced in PRs #6 and #7.
# The same current harness and same scenario file are copied into both worktrees;
# only the core contract/skills/passports at the tested commit differ.
ROOT="$(git rev-parse --show-toplevel)"
CURRENT_HEAD="$(git -C "$ROOT" rev-parse HEAD)"
BASELINE_STATUS_COMMIT="${BASELINE_STATUS_COMMIT:-a52574a872c2d8aaccde47a9fdab239a46bfe467}"
CANDIDATE_STATUS_COMMIT="${CANDIDATE_STATUS_COMMIT:-6ceb35caf939af227f533edec861d69b48517bb8}"
BASELINE_SUPPORT_COMMIT="${BASELINE_SUPPORT_COMMIT:-6ceb35caf939af227f533edec861d69b48517bb8}"
CANDIDATE_SUPPORT_COMMIT="${CANDIDATE_SUPPORT_COMMIT:-$CURRENT_HEAD}"

if ! git -C "$ROOT" diff --quiet || ! git -C "$ROOT" diff --cached --quiet; then
  echo "Refusing to run with tracked, uncommitted changes. Commit or stash them first." >&2
  exit 2
fi

SCENARIO_SOURCE="$ROOT/tests/live/offer-status-scenarios.yaml"
if [[ ! -f "$SCENARIO_SOURCE" ]]; then
  echo "Missing focused scenario pack: $SCENARIO_SOURCE" >&2
  exit 2
fi
if [[ -z "${OPENROUTER_API_KEY:-}" && ! -f "$HOME/.hermes/.env" ]]; then
  echo "Set OPENROUTER_API_KEY or add it to ~/.hermes/.env first." >&2
  exit 2
fi

OUT_ROOT="$ROOT/tests/live/results/focused-ab"
mkdir -p "$OUT_ROOT"
WORK_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/daniyar-focused-ab.XXXXXX")"
WORKTREES=()

cleanup() {
  for worktree in "${WORKTREES[@]:-}"; do
    git -C "$ROOT" worktree remove --force "$worktree" >/dev/null 2>&1 || true
  done
  rm -rf "$WORK_ROOT"
}
trap cleanup EXIT

prepare_worktree() {
  local commit="$1"
  local target="$2"
  git -C "$ROOT" worktree add --detach "$target" "$commit" >/dev/null
  WORKTREES+=("$target")
  mkdir -p "$target/tests/live"
  cp "$ROOT/tests/live/run_live_eval.py" "$target/tests/live/run_live_eval.py"
  cp "$ROOT/tests/live/prompt_build.py" "$target/tests/live/prompt_build.py"
  cp "$ROOT/tests/live/score_live_eval.py" "$target/tests/live/score_live_eval.py"
  cp "$SCENARIO_SOURCE" "$target/tests/live/offer-status-scenarios.yaml"
}

run_trials() {
  local worktree="$1"
  local label="$2"
  local arm="$3"
  shift 3
  local -a scenario_ids=("$@")
  local trial out_dir responses score_file

  for trial in 1 2 3; do
    out_dir="$OUT_ROOT/$label/$arm/trial-$trial"
    mkdir -p "$out_dir"
    echo "Running $label / $arm / trial $trial: ${scenario_ids[*]}"
    (
      cd "$worktree"
      python3 tests/live/run_live_eval.py \
        --arm "$arm" \
        --scenarios tests/live/offer-status-scenarios.yaml \
        --only "${scenario_ids[@]}" \
        --out "$out_dir" \
        --trial "$trial"
    )
    responses="$(find "$out_dir" -maxdepth 1 -type f -name "responses-trial${trial}-*.jsonl" -print -quit)"
    if [[ -z "$responses" ]]; then
      echo "No raw response file was created in $out_dir" >&2
      return 1
    fi
    score_file="$out_dir/checks.json"
    python3 "$worktree/tests/live/score_live_eval.py" \
      --responses "$responses" \
      --scenarios "$worktree/tests/live/offer-status-scenarios.yaml" \
      --json-out "$score_file"
    python3 - "$score_file" <<'PY'
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(f"Score: {data.get('passed', 0)}/{data.get('scenario_count', 0)} passed; "
      f"{data.get('failed', 0)} failed. Full score: {sys.argv[1]}")
PY
  done
}

BASE_STATUS="$WORK_ROOT/baseline-status"
MID="$WORK_ROOT/pr6-middle"
CAND_SUPPORT="$WORK_ROOT/candidate-support"

prepare_worktree "$BASELINE_STATUS_COMMIT" "$BASE_STATUS"
prepare_worktree "$CANDIDATE_STATUS_COMMIT" "$MID"
prepare_worktree "$CANDIDATE_SUPPORT_COMMIT" "$CAND_SUPPORT"

run_trials "$BASE_STATUS" "paused-plan" "baseline" \
  OS-RU-PAUSED-TRAINING OS-KY-PAUSED-TRAINING
run_trials "$MID" "paused-plan" "candidate" \
  OS-RU-PAUSED-TRAINING OS-KY-PAUSED-TRAINING

run_trials "$MID" "support-guarantee" "baseline" \
  OS-RU-SUPPORT-GUARANTEE OS-KY-SUPPORT-GUARANTEE
run_trials "$CAND_SUPPORT" "support-guarantee" "candidate" \
  OS-RU-SUPPORT-GUARANTEE OS-KY-SUPPORT-GUARANTEE

echo
echo "Focused A/B evaluation completed."
echo "Inspect raw outputs, run metadata, and checks under: $OUT_ROOT"
echo "No production profile, passport source, or deployment was modified."
