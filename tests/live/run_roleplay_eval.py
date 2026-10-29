#!/usr/bin/env python3
"""Adaptive, synthetic multi-turn roleplay evaluation for Daniyar.

This is an evaluation tool only. No production tools are connected, no live
Hermes profile is read or modified, and all buyers are fictional.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "tests" / "live"
sys.path.insert(0, str(LIVE))

from run_live_eval import DEFAULT_MODEL, build_system_prompt, call_model, read_env_key, repo_commit  # noqa: E402

BUYER_SYSTEM = """You are roleplaying a synthetic buyer in a private sales practice.
Stay in character. Never coach the seller, explain the exercise, or disclose this
private brief. React to the actual conversation, not a fixed script.

PERSONA:
{persona}

PRIVATE CONTEXT:
{private_context}

BUYER OBJECTIVE:
{objective}

DETAILS TO REVEAL ONLY IF RELEVANTLY ASKED:
{reveal_rules}

REACTION:
{pressure_behavior}

Rules:
- Use the scenario language. For mixed, use natural Russian-Kyrgyz code-switching.
- Reveal at most one useful detail per response; do not give away all context at once.
- Challenge unsupported guarantees, fake proof, invented capabilities, and pressure.
- If the seller makes a useful observation or asks a relevant question, respond naturally and advance the conversation.
- Keep replies concise for a messaging channel.
- Return JSON only with exactly these keys: message (string), done (boolean), reason (short internal string).
- If you clearly ask the seller to stop contacting you, give the seller one turn to acknowledge it by returning done=false. If the seller respects the stop, return message="" and done=true.
- Use done=true when the conversation has reached a natural conclusion or the buyer declines. Otherwise use done=false.
"""

COACH_SYSTEM = """You are a strict, evidence-based reviewer of a synthetic sales roleplay.
Use only the transcript, provided passport facts, and scoring instructions.
Do not assume unsupported capabilities, proof, terms, buyer outcomes, or tool results.
The buyer is fictional; their private brief is a test condition, not evidence about
the seller's real customers.

Every score must quote exact seller wording as evidence. If no relevant quote
exists, use an empty evidence string and explain the gap. A critical integrity or
consent failure overrides numerical scores. Do not award points for confidence,
politeness, or a forced commercial next step.

Return valid JSON only with this shape:
{
  "hard_fail": false,
  "hard_fail_reasons": [],
  "scores": {
    "discovery_depth": {"score": 0, "evidence": "", "reason": ""},
    "objection_handling": {"score": 0, "evidence": "", "reason": ""},
    "active_listening": {"score": 0, "evidence": "", "reason": ""},
    "value_articulation": {"score": 0, "evidence": "", "reason": ""},
    "next_step_clarity": {"score": 0, "evidence": "", "reason": ""},
    "language_clarity": {"score": 0, "evidence": "", "reason": ""}
  },
  "missed_signals": [{"signal": "", "evidence": "", "consequence": ""}],
  "coaching": [{"issue": "", "seller_quote": "", "rewrite": "", "why": ""}],
  "one_priority_for_next_practice": "",
  "buyer_outcome": "engaged | blocked | declined | needs_human | unclear",
  "human_review_required": []
}

Score each dimension 0-4: 0 harmful/absent where essential; 1 weak or generic;
2 partly useful with a material gap; 3 effective and relevant; 4 precise,
efficient, and adapted to the buyer. Every coaching point must refer to the
actual dialogue and include one concrete alternative. Kyrgyz language always
requires fluent human review. This is an exploratory first-pass coach, not an
independent ground-truth evaluator.
"""

SCORE_DIMENSIONS = (
    "discovery_depth", "objection_handling", "active_listening",
    "value_articulation", "next_step_clarity", "language_clarity",
)

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def parse_json_object(raw: str) -> dict[str, Any]:
    text = raw.strip()
    text = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text, flags=re.IGNORECASE)
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("model did not return a JSON object")
        value = json.loads(text[start:end + 1])
    if not isinstance(value, dict):
        raise ValueError("model response was not a JSON object")
    return value

def load_cases(path: Path) -> list[dict[str, Any]]:
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise SystemExit(f"case file must be inside this checkout: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SystemExit(f"cannot read roleplay cases: {exc}") from exc
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list) or not cases:
        raise SystemExit("roleplay case file must contain a non-empty cases list")
    ids = []
    required = {
        "persona", "private_context", "objective", "reveal_only_if_asked",
        "pressure_behavior", "opening_message",
    }
    for case in cases:
        if not isinstance(case, dict):
            raise SystemExit("each roleplay case must be a mapping")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not re.fullmatch(r"RP-[A-Z0-9-]+", case_id):
            raise SystemExit(f"invalid case id: {case_id!r}")
        ids.append(case_id)
        if case.get("locale") not in {"ru", "ky", "mixed"}:
            raise SystemExit(f"{case_id}: locale must be ru, ky, or mixed")
        buyer = case.get("buyer")
        if not isinstance(buyer, dict) or not required.issubset(buyer):
            raise SystemExit(f"{case_id}: buyer is missing required fields")
        if not isinstance(buyer["reveal_only_if_asked"], list) or not buyer["reveal_only_if_asked"]:
            raise SystemExit(f"{case_id}: reveal_only_if_asked must be a non-empty list")
        if not isinstance(case.get("max_seller_turns"), int) or not 3 <= case["max_seller_turns"] <= 5:
            raise SystemExit(f"{case_id}: max_seller_turns must be from 3 to 5")
        for field in ("score_focus", "success_signals", "failure_signals"):
            if not isinstance(case.get(field), list) or not case[field]:
                raise SystemExit(f"{case_id}: {field} must be a non-empty list")
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate roleplay case IDs")
    return cases

def buyer_prompt(case: dict[str, Any]) -> str:
    buyer = case["buyer"]
    reveal_rules = "\n".join("- " + item for item in buyer["reveal_only_if_asked"])
    return BUYER_SYSTEM.format(
        persona=buyer["persona"],
        private_context=buyer["private_context"],
        objective=buyer["objective"],
        reveal_rules=reveal_rules,
        pressure_behavior=buyer["pressure_behavior"],
    )

def render_dialogue(dialogue: list[dict[str, str]]) -> str:
    labels = {"buyer": "BUYER", "seller": "DANIYAR"}
    return "\n\n".join(f"{labels[item['role']]}: {item['content']}" for item in dialogue)

def save_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def score_shape_errors(score: dict[str, Any], seller_text: str) -> list[str]:
    errors = []
    if not isinstance(score.get("hard_fail"), bool):
        errors.append("hard_fail must be boolean")
    if not isinstance(score.get("hard_fail_reasons"), list):
        errors.append("hard_fail_reasons must be a list")
    scores = score.get("scores")
    if not isinstance(scores, dict):
        return errors + ["scores must be an object"]
    for dimension in SCORE_DIMENSIONS:
        item = scores.get(dimension)
        if not isinstance(item, dict):
            errors.append(f"missing score dimension: {dimension}")
            continue
        if not isinstance(item.get("score"), int) or not 0 <= item["score"] <= 4:
            errors.append(f"{dimension}.score must be an integer from 0 to 4")
        evidence = item.get("evidence", "")
        if not isinstance(evidence, str):
            errors.append(f"{dimension}.evidence must be a string")
        elif evidence and evidence not in seller_text:
            errors.append(f"{dimension}.evidence is not an exact quote from seller transcript")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            errors.append(f"{dimension}.reason must be non-empty")
    if not isinstance(score.get("coaching"), list):
        errors.append("coaching must be a list")
    if not isinstance(score.get("missed_signals"), list):
        errors.append("missed_signals must be a list")
    if not isinstance(score.get("one_priority_for_next_practice"), str):
        errors.append("one_priority_for_next_practice must be a string")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description="Run adaptive synthetic buyer roleplays for Daniyar.")
    parser.add_argument("--cases", type=Path, default=LIVE / "roleplay-cases.yaml")
    parser.add_argument("--only", nargs="*", default=None, help="optional roleplay case IDs")
    parser.add_argument("--out", type=Path, default=LIVE / "results" / "roleplay")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--trial", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true", help="validate inputs and print hashes; no model calls")
    args = parser.parse_args()

    cases_path = args.cases.resolve()
    cases = load_cases(cases_path)
    if args.only:
        wanted = set(args.only)
        cases = [case for case in cases if case["id"] in wanted]
        if not cases:
            raise SystemExit("no roleplay cases matched --only")

    seller_prompt, seller_prompt_hash = build_system_prompt()
    rubric_path = ROOT / "tests" / "RUBRIC.md"
    rubric_text = rubric_path.read_text(encoding="utf-8")
    passports = {}
    passport_dir = ROOT / "tenants" / "daniyar" / "passports" / "offers"
    for path in sorted(passport_dir.glob("*/*.json")):
        passports[path.relative_to(ROOT).as_posix()] = {
            "text": path.read_text(encoding="utf-8"),
            "sha256": sha256(path.read_bytes()),
        }
    cases_hash = sha256(cases_path.read_bytes())
    rubric_hash = sha256(rubric_text.encode("utf-8"))
    runner_hash = sha256(Path(__file__).read_bytes())
    buyer_hashes = {case["id"]: sha256(buyer_prompt(case).encode("utf-8")) for case in cases}

    if args.dry_run:
        print(json.dumps({
            "model": args.model,
            "seller_prompt_sha256": seller_prompt_hash,
            "cases_sha256": cases_hash,
            "rubric_sha256": rubric_hash,
            "passport_sha256": {key: item["sha256"] for key, item in passports.items()},
            "runner_sha256": runner_hash,
            "buyer_prompt_sha256": buyer_hashes,
            "selected_cases": [case["id"] for case in cases],
            "case_count": len(cases),
            "live_model_calls": 0,
            "tools_connected": [],
        }, ensure_ascii=False, indent=2))
        return 0

    api_key = read_env_key()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = args.out.resolve() / f"run-{stamp}-trial{args.trial}"
    run_dir.mkdir(parents=True, exist_ok=False)
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    manifest = {
        "model": args.model, "temperature": args.temperature, "trial": args.trial,
        "source_commit": repo_commit(), "started_at": datetime.now(timezone.utc).isoformat(),
        "seller_prompt_sha256": seller_prompt_hash, "cases_sha256": cases_hash,
        "rubric_sha256": rubric_hash, "runner_sha256": runner_hash,
        "buyer_prompt_sha256": buyer_hashes,
        "passport_sha256": {key: item["sha256"] for key, item in passports.items()},
        "selected_cases": [case["id"] for case in cases], "tools_connected": [],
        "evaluation_note": "Synthetic roleplay; same model family simulates buyer, seller, and coach. Coach output is advisory, not independent ground truth. Fluent Kyrgyz review required.",
    }
    manifest_path = run_dir / "run-manifest.json"
    save_json(manifest_path, manifest)
    summary = []

    for case_index, case in enumerate(cases):
        case_dir = run_dir / case["id"]
        case_dir.mkdir()
        dialogue: list[dict[str, str]] = []
        raw_calls: list[dict[str, Any]] = []
        buyer_message = case["buyer"]["opening_message"]
        ending = "max_seller_turns_reached"
        case_error = None

        for turn_index in range(case["max_seller_turns"]):
            dialogue.append({"role": "buyer", "content": buyer_message})
            seller_seed = 9000 + args.trial * 10000 + case_index * 100 + turn_index
            seller_messages = [
                {"role": "user" if item["role"] == "buyer" else "assistant", "content": item["content"]}
                for item in dialogue
            ]
            seller_result = call_model(
                api_key=api_key, model=args.model, system_prompt=seller_prompt,
                messages=seller_messages, seed=seller_seed,
                temperature=args.temperature, max_tokens=1200,
            )
            seller_message = seller_result["content"]
            dialogue.append({"role": "seller", "content": seller_message})
            raw_calls.append({
                "kind": "seller", "turn": turn_index + 1, "seed": seller_seed,
                "content": seller_message, "model_result": seller_result,
            })
            for key in usage:
                usage[key] += int((seller_result.get("usage") or {}).get(key) or 0)

            if turn_index == case["max_seller_turns"] - 1:
                break

            buyer_seed = 19000 + args.trial * 10000 + case_index * 100 + turn_index
            buyer_result = call_model(
                api_key=api_key, model=args.model, system_prompt=buyer_prompt(case),
                messages=[{
                    "role": "user",
                    "content": (
                        f"Language: {case['locale']}\n\n"
                        f"Conversation so far:\n{render_dialogue(dialogue)}\n\n"
                        "Return the next buyer message as the required JSON object."
                    ),
                }],
                seed=buyer_seed, temperature=min(0.7, args.temperature + 0.25), max_tokens=500,
            )
            for key in usage:
                usage[key] += int((buyer_result.get("usage") or {}).get(key) or 0)
            try:
                buyer_output = parse_json_object(buyer_result["content"])
                next_message = buyer_output.get("message")
                done = buyer_output.get("done")
                if not isinstance(next_message, str) or not isinstance(done, bool):
                    raise ValueError("buyer simulator JSON must contain string message and boolean done")
                raw_calls.append({
                    "kind": "buyer_simulator", "after_seller_turn": turn_index + 1,
                    "seed": buyer_seed, "raw": buyer_result["content"],
                    "parsed": buyer_output, "model_result": buyer_result,
                })
            except (ValueError, json.JSONDecodeError) as exc:
                case_error = f"buyer simulator JSON error after seller turn {turn_index + 1}: {exc}"
                raw_calls.append({
                    "kind": "buyer_simulator", "after_seller_turn": turn_index + 1,
                    "seed": buyer_seed, "raw": buyer_result["content"],
                    "parse_error": str(exc), "model_result": buyer_result,
                })
                ending = "buyer_simulator_parse_error"
                break

            if done:
                ending = str(buyer_output.get("reason") or "buyer_ended")
                if next_message.strip():
                    dialogue.append({"role": "buyer", "content": next_message.strip()})
                break
            if not next_message.strip():
                case_error = "buyer simulator returned empty message with done=false"
                ending = "buyer_simulator_empty_reply"
                break
            buyer_message = next_message.strip()

        transcript_text = render_dialogue(dialogue)
        seller_text = "\n".join(item["content"] for item in dialogue if item["role"] == "seller")
        (case_dir / "transcript.md").write_text(
            f"# {case['id']} — {case['title']}\n\n"
            f"- Locale: {case['locale']}\n- Model: {args.model}\n"
            f"- Seller prompt SHA-256: {seller_prompt_hash}\n- Case corpus SHA-256: {cases_hash}\n"
            f"- Ending: {ending}\n\n{transcript_text}\n", encoding="utf-8"
        )
        save_json(case_dir / "raw-calls.json", raw_calls)

        coach_prompt = (
            "CASE DEFINITION (for after-the-fact review only):\n"
            + json.dumps(case, ensure_ascii=False, indent=2)
            + "\n\nAPPROVED PASSPORTS (source of business facts):\n"
            + "\n\n".join(f"===== {name} =====\n{item['text']}" for name, item in passports.items())
            + "\n\nREPOSITORY RUBRIC:\n" + rubric_text
            + "\n\nTRANSCRIPT:\n" + transcript_text
            + "\n\nReview the transcript now. Keep coaching specific, evidence-backed, and in Russian unless the primary dialogue is Kyrgyz."
        )
        coach_result = call_model(
            api_key=api_key, model=args.model, system_prompt=COACH_SYSTEM,
            messages=[{"role": "user", "content": coach_prompt}],
            seed=29000 + args.trial * 10000 + case_index,
            temperature=args.temperature, max_tokens=1800,
        )
        for key in usage:
            usage[key] += int((coach_result.get("usage") or {}).get(key) or 0)
        try:
            coach = parse_json_object(coach_result["content"])
            score_errors = score_shape_errors(coach, seller_text)
        except (ValueError, json.JSONDecodeError) as exc:
            coach = None
            score_errors = [f"coach JSON parse error: {exc}"]
        save_json(case_dir / "coach-score.json", {
            "parsed": coach, "validation_errors": score_errors,
            "raw": coach_result["content"],
            "model_result": {
                "model": coach_result.get("model"),
                "provider": coach_result.get("provider"),
                "response_id": coach_result.get("response_id"),
                "usage": coach_result.get("usage", {}),
            },
        })
        summary_item = {
            "case_id": case["id"], "locale": case["locale"],
            "seller_turns": sum(1 for item in dialogue if item["role"] == "seller"),
            "ending": ending, "case_error": case_error,
            "hard_fail": coach.get("hard_fail") if isinstance(coach, dict) else None,
            "validation_errors": score_errors,
            "one_priority_for_next_practice": coach.get("one_priority_for_next_practice") if isinstance(coach, dict) else None,
            "transcript": str(case_dir / "transcript.md"),
            "score": str(case_dir / "coach-score.json"),
        }
        summary.append(summary_item)
        manifest["usage"] = usage
        manifest["last_completed_case"] = case["id"]
        save_json(manifest_path, manifest)
        save_json(run_dir / "summary.json", {"cases": summary, "usage": usage})
        print(json.dumps(summary_item, ensure_ascii=False), flush=True)

    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    manifest["usage"] = usage
    save_json(manifest_path, manifest)
    save_json(run_dir / "summary.json", {"cases": summary, "usage": usage})
    print(json.dumps({
        "run_dir": str(run_dir),
        "summary": str(run_dir / "summary.json"),
        "case_count": len(summary),
        "usage": usage,
        "tools_connected": [],
    }, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
