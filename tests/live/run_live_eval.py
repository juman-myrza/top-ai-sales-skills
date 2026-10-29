#!/usr/bin/env python3
"""Run live sales scenarios against a pinned OpenRouter model.

This is an evaluation harness, not a production adapter. It assembles the
current core contract, skills, and the two approved Daniyar passports into one
system prompt, then runs each scenario turn-by-turn. Raw responses, usage, and
the prompt hash are written to disk so a before/after comparison can be
audited.

The harness deliberately does not expose tools. The runtime note tells the
model that calendar, payment, handoff, messaging, and CRM tools are not
connected, so a claimed booking/payment/handoff is a truth failure rather than
a missing integration. This is disclosed in tests/live/README.md.

Usage:
    python tests/live/run_live_eval.py --arm baseline
    python tests/live/run_live_eval.py --arm candidate --out tests/live/results/candidate
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import yaml

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "tests" / "live"
sys.path.insert(0, str(LIVE))

from prompt_build import build, prompt_parts  # noqa: E402
DEFAULT_SCENARIOS = LIVE / "scenarios.yaml"
DEFAULT_MODEL = "deepseek/deepseek-v4.1-flash"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def read_env_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("OPENROUTER_API_KEY is not set and ~/.hermes/.env has no OPENROUTER_API_KEY")


def repo_commit() -> str:
    import subprocess

    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def build_system_prompt() -> tuple[str, str]:
    parts = prompt_parts(ROOT)
    prompt = build(parts, lambda rel: (ROOT / rel).read_text(encoding="utf-8"))
    return prompt, hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise SystemExit(f"expected a non-empty scenario list in {path}, got {len(scenarios) if isinstance(scenarios, list) else 'none'}")
    ids = [s.get("id") for s in scenarios]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate scenario ids")
    return scenarios


def call_model(
    api_key: str,
    model: str,
    system_prompt: str,
    messages: list[dict[str, str]],
    seed: int,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}, *messages],
        "temperature": temperature,
        "top_p": 1,
        "max_tokens": max_tokens,
        "seed": seed,
        "reasoning": {"effort": "none"},
        "usage": {"include": True},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/juman-myrza/top-ai-sales-skills",
        "X-Title": "top-ai-sales-skills live evaluation",
    }
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=180)
            if response.status_code in {429, 500, 502, 503, 504}:
                raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"].get("content") or ""
            if not content.strip():
                raise RuntimeError("empty model response")
            choice = data["choices"][0]
            return {
                "content": content.strip(),
                "model": data.get("model"),
                "provider": data.get("provider"),
                "response_id": data.get("id"),
                "finish_reason": choice.get("finish_reason"),
                "native_finish_reason": choice.get("native_finish_reason"),
                "usage": data.get("usage", {}),
                "created": data.get("created"),
            }
        except Exception as exc:  # noqa: BLE001 - retry boundary
            last_error = exc
            if attempt == 4:
                break
            time.sleep(2 ** attempt)
    raise RuntimeError(f"model call failed after retries: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live sales scenarios against OpenRouter.")
    parser.add_argument("--arm", required=True, choices=["baseline", "candidate"], help="label for this run")
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    parser.add_argument("--out", type=Path, default=None, help="output directory")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--only", nargs="*", default=None, help="optional scenario ids")
    parser.add_argument("--dry-run", action="store_true", help="print the prompt size and exit")
    parser.add_argument("--trial", type=int, default=1, help="trial number; changes the per-scenario seed base")
    args = parser.parse_args()

    system_prompt, prompt_hash = build_system_prompt()
    scenarios = load_scenarios(args.scenarios)
    if args.only:
        wanted = set(args.only)
        scenarios = [s for s in scenarios if s["id"] in wanted]
        if not scenarios:
            raise SystemExit("no scenarios matched --only")

    if args.dry_run:
        print(json.dumps({
            "model": args.model,
            "prompt_chars": len(system_prompt),
            "prompt_sha256": prompt_hash,
            "scenario_count": len(scenarios),
            "source_files": prompt_parts(ROOT),
        }, ensure_ascii=False, indent=2))
        return 0

    api_key = read_env_key()
    out_dir = args.out or (LIVE / "results" / args.arm)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    records_path = out_dir / f"responses-trial{args.trial}-{stamp}.jsonl"
    transcript_path = out_dir / f"transcript-trial{args.trial}-{stamp}.md"
    meta_path = out_dir / f"run-trial{args.trial}-{stamp}.json"

    meta = {
        "arm": args.arm,
        "trial": args.trial,
        "model": args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "reasoning_effort": "none",
        "prompt_sha256": prompt_hash,
        "prompt_chars": len(system_prompt),
        "repo_commit": repo_commit(),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "scenario_count": len(scenarios),
        "scenario_file": str(args.scenarios.relative_to(ROOT)),
        "tools_connected": [],
        "note": "No tools were connected. The prompt states this explicitly.",
    }

    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    with records_path.open("w", encoding="utf-8") as records, transcript_path.open("w", encoding="utf-8") as transcript:
        transcript.write(f"# Live evaluation transcript: {args.arm}\n\n")
        transcript.write(f"- Model: `{args.model}`\n- Temperature: `{args.temperature}`\n")
        transcript.write(f"- Prompt SHA-256: `{prompt_hash}`\n- Commit: `{meta['repo_commit']}`\n")
        transcript.write("- Tools connected: none\n\n")

        for index, scenario in enumerate(scenarios):
            sid = scenario["id"]
            messages: list[dict[str, str]] = []
            turns: list[dict[str, Any]] = []
            transcript.write(f"## {sid} — {scenario['title']} ({scenario['locale']})\n\n")
            for turn_index, buyer_text in enumerate(scenario["turns"]):
                messages.append({"role": "user", "content": buyer_text})
                transcript.write(f"**Buyer:** {buyer_text}\n\n")
                seed = 4200 + args.trial * 1000 + index * 10 + turn_index
                result = call_model(
                    api_key=api_key,
                    model=args.model,
                    system_prompt=system_prompt,
                    messages=messages,
                    seed=seed,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                )
                messages.append({"role": "assistant", "content": result["content"]})
                transcript.write(f"**Agent:** {result['content']}\n\n")
                usage = result.get("usage") or {}
                for key in total_usage:
                    total_usage[key] += int(usage.get(key) or 0)
                turns.append({
                    "buyer": buyer_text,
                    "assistant": result["content"],
                    "model": result.get("model"),
                    "provider": result.get("provider"),
                    "response_id": result.get("response_id"),
                    "finish_reason": result.get("finish_reason"),
                    "native_finish_reason": result.get("native_finish_reason"),
                    "usage": usage,
                })
                print(f"{sid} turn {turn_index + 1}: {len(result['content'])} chars", flush=True)
            record = {
                "scenario_id": sid,
                "title": scenario["title"],
                "locale": scenario["locale"],
                "category": scenario["category"],
                "focus": scenario.get("focus", []),
                "checks": scenario.get("checks", {}),
                "turns": turns,
                "final_response": turns[-1]["assistant"] if turns else "",
            }
            records.write(json.dumps(record, ensure_ascii=False) + "\n")
            records.flush()
            transcript.write("---\n\n")

    meta["finished_at"] = datetime.now(timezone.utc).isoformat()
    meta["usage"] = total_usage
    meta["estimated_cost_usd"] = round(
        total_usage["prompt_tokens"] * 0.000000045 + total_usage["completion_tokens"] * 0.0000005, 6
    )
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": str(records_path), "transcript": str(transcript_path), "meta": str(meta_path), "usage": total_usage}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
