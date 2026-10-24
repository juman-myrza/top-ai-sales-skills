# Scripts

Seven small tools for validating, testing, rendering, and installing the repository. None of them calls a language model, a sales tool, or a production API. Only `install_skills.py --apply` writes outside a temporary directory.

The repository root also ships `install.sh` and `uninstall.sh`: thin POSIX wrappers around `install_skills.py` and the install manifest. They default to a dry run, support `--apply`, and can bootstrap from a clone when piped (`curl … | sh -s -- --apply`). The round-trip is checked by [`test_install_uninstall.sh`](test_install_uninstall.sh). See the [README install and uninstall sections](../README.md#install).

Install development dependencies once:

```bash
python3 -m pip install -r requirements-dev.txt
```

| Script | Reads | Writes | Calls Hermes |
|---|---|---|---|
| [`validate_repository.py`](validate_repository.py) | repository | nothing | no |
| [`evaluate_responses.py`](evaluate_responses.py) | scenarios + JSONL responses | optional JSON summary to stdout | no |
| [`render_scenarios.py`](render_scenarios.py) | scenarios | optional file | no |
| [`test_checker.py`](test_checker.py) | scenarios | nothing | no |
| [`test_installed_artifact.py`](test_installed_artifact.py) | skills, validator | temporary directory | no |
| [`test_hermes_loading.py`](test_hermes_loading.py) | skills | temporary `HERMES_HOME` | yes, `hermes skills list` |
| [`install_skills.py`](install_skills.py) | skills, validator | target Hermes home, only with `--apply` | no |
| [`test_install_uninstall.sh`](test_install_uninstall.sh) | root wrappers | temporary home | no |
| `../install.sh` | repo, manifest | target home (via `install_skills.py --apply`) | no |
| `../uninstall.sh` | install manifest | target home (only with `--apply`) | no |

---

## `validate_repository.py`

Structural and schema validation. This is the gate used by CI and by the installer.

```bash
python3 scripts/validate_repository.py
python3 scripts/validate_repository.py --quiet
```

Checks:

- required files exist;
- exactly nine skill directories with matching `name`, valid descriptions, metadata, required sections, reference links, and size budget;
- skills do not contain fictional example brands or concrete currency amounts;
- passport examples validate against `product-passport/passport.schema.json`;
- tool envelopes validate against `tools/schemas/tool-envelope.schema.json`;
- all scenario YAML parses, IDs are unique, category counts match the declared 57, and expectations are well-formed;
- every scenario ID appears in `tests/COVERAGE.md`;
- local Markdown links resolve;
- obvious secret patterns are absent;
- `.gitignore` contains recommended entries.

Exit codes: `0` passed (warnings allowed), `1` errors, `2` missing dependency or wrong root.

Passing means the files are internally consistent. It does **not** mean the agent behaves well, the passport facts are true, or an integration works.

---

## `evaluate_responses.py`

Compares recorded agent responses with the deterministic expectations in the scenario corpus.

```bash
python3 scripts/evaluate_responses.py \
  --responses tests/responses/run-2026-10-23.jsonl

# Check the checker itself: hand-written fixture, partial coverage allowed
python3 scripts/evaluate_responses.py \
  --responses tests/fixtures/smoke-responses.jsonl \
  --allow-partial

# Machine-readable output
python3 scripts/evaluate_responses.py \
  --responses tests/responses/run.jsonl \
  --json
```

Response record format (one JSON object per line):

```json
{
  "scenario_id": "P01",
  "response": "agent text",
  "tool_calls": [
    {"tool": "passport.lookup", "operation": "lookup", "status": "ok"}
  ],
  "handoff": false,
  "handoff_attempted": false,
  "stopped": false
}
```

Options:

- `--responses` — JSONL file (required).
- `--scenarios` — alternative scenario directory.
- `--allow-partial` — do not fail when some scenarios have no record.
- `--json` — emit a summary object instead of human-readable text.

Checks per scenario: required and forbidden substrings/regexes, question count, required and forbidden tool calls/operations, handoff and stop flags, disqualification language, and optional language markers.

Exit codes: `0` all checked records pass, `1` a check failed or records are missing without `--allow-partial`, `2` input error.

The checker is intentionally shallow. It cannot judge tone, empathy, strategic quality, or a false claim the scenario did not anticipate. Use it with the [rubric](../tests/RUBRIC.md), not instead of it.

---

## `render_scenarios.py`

Renders the YAML corpus for humans or for an external evaluation harness.

```bash
# Human-readable Markdown to stdout
python3 scripts/render_scenarios.py

# JSONL for another tool, expectations included
python3 scripts/render_scenarios.py \
  --format jsonl \
  --include-expected \
  --out /tmp/opencode/scenarios.jsonl
```

Options:

- `--scenarios` — alternative scenario directory.
- `--format markdown|jsonl` — default `markdown`.
- `--out` — output file; default stdout.
- `--include-expected` — include deterministic expectations in JSONL. Intended for offline analysis, not for exposing the answer key to an evaluated agent.

By default, JSONL omits expectations so the output can be fed to a responder.

---

## `test_hermes_loading.py`

Verifies that Hermes discovers all nine skills. It copies the skills into a **temporary** `HERMES_HOME` and runs:

```bash
hermes skills list --source local
```

```bash
python3 scripts/test_hermes_loading.py
python3 scripts/test_hermes_loading.py --require   # fail if Hermes is absent
python3 scripts/test_hermes_loading.py --keep      # keep temp home for debugging
```

Options:

- `--hermes PATH` — explicit Hermes executable.
- `--timeout SECONDS` — default 300. First startup may install Python dependencies.
- `--require` — fail when Hermes is absent instead of skipping.
- `--keep` — keep the temporary home and print its path.

The script never reads or writes `~/.hermes`, never starts an agent, and never calls a model. It requires network access only if Hermes decides to prepare dependencies. A pass proves discovery in the tested Hermes version, not that the skills influence model behavior.

Exit codes: `0` all discovered, or skipped when Hermes is absent without `--require`; `1` discovery or command failure; `2` invalid arguments or wrong skill count.

---

## `install_skills.py`

Copies the nine skills into a Hermes home. **Dry run by default.**

```bash
# Show the plan; write nothing
python3 scripts/install_skills.py

# Install into the default ~/.hermes
python3 scripts/install_skills.py --apply

# Install into an isolated test home
python3 scripts/install_skills.py --target /tmp/opencode/hermes-test --apply
```

Options:

- `--target PATH` — Hermes home; default `~/.hermes`. Skills go to `<target>/skills/sales/<name>/`.
- `--apply` — actually write. Without it, nothing is created.
- `--force` — replace existing skill directories. Without it, existing directories are skipped.
- `--no-backup` — skip the timestamped backup when replacing.
- `--skip-validate` — skip the repository validation gate. Not recommended.

Safety behavior:

- refuses to install inside the repository itself;
- runs `validate_repository.py` before writing unless `--skip-validate` is passed;
- stages the copy and backs up replaced directories by default;
- installs instruction files only. It does **not** configure tool adapters, credentials, cron jobs, a model, or a channel.

Exit codes: `0` success or completed dry run, `1` validation or install failure, `2` invalid source or target.

---

## CI

[`.github/workflows/validate.yml`](../.github/workflows/validate.yml) runs on pushes and pull requests:

1. installs `requirements-dev.txt`;
2. runs `validate_repository.py`;
3. runs the response checker against the smoke fixture with `--allow-partial`;
4. renders the scenario corpus to JSONL as a parser check.

CI does not install Hermes, call a model, or test any external integration. The isolated loading test is meant to be run locally against a known Hermes version.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `ERROR: PyYAML is required` | Run `pip install -r requirements-dev.txt` |
| `SKIPPED Hermes executable not found` | Hermes is not on `PATH`; pass `--hermes` or use `--require` to fail |
| Hermes discovery times out | First run may prepare dependencies; increase `--timeout` |
| Installer says `skip (exists; use --force)` | A skill directory already exists; inspect it before forcing |
| Validation fails on a local link | A relative Markdown link points to a missing file |
| Checker reports `missing response` | Add a JSONL record or pass `--allow-partial` |

Do not "fix" a failure by deleting a check or loosening a safety rule. Fix the artifact.
