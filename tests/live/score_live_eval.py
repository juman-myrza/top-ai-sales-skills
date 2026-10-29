#!/usr/bin/env python3
"""Apply deterministic checks to a live-evaluation response file.

The checks are shallow by design. They catch a wrong price, a forbidden
discount/guarantee, a missing next step, and a language/format violation. They
do not replace the rubric review in tests/live/SCORING.md.

Usage:
    python tests/live/score_live_eval.py \
      --responses tests/live/results/baseline/responses-*.jsonl \
      --scenarios tests/live/scenarios.yaml \
      --json-out tests/live/results/baseline/checks.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
NEGATION_TOKENS = ["не ", "нет ", "not ", "never ", "cannot ", "can't ", "without ", "без ", "эмес", "жок", "албайм", "берилбейт", "албаган"]

# Dominant-language heuristic. Kyrgyz is distinct from Russian by the letters
# ң, ө, ү (essentially absent in Russian) and by a set of high-frequency Kyrgyz
# function/content words. Russian is detected by high-frequency Russian words.
# This is a heuristic used to catch a full-language switch, not a certified
# language identifier; Kyrgyz/mixed verdicts still require a native reviewer.
KYRGYZ_LETTERS = set("ңөү")
KYRGYZ_WORDS = {
    "жана", "менен", "үчүн", "болот", "эмес", "канча", "багыт", "жок", "бир",
    "сиз", "биз", "кандай", "эмне", "керек", "азыр", "кийин", "болобу",
    "эмнени", "кайсы", "турат", "кылыш", "баштайлы", "макул", "салам",
    "рахмат", "кечиресиз", "түшүндүм", "жазыңыз", "биздин", "сиздин",
    "алар", "аны", "муну", "ушул", "ошол", "барбы", "жооп", "билдирүү",
    "кардар", "кана", "дагы", "бар", "болсо", "болуп", "аткан", "жатат",
    "көрөйүн", "сунуш", "макулдашылган", "көлөм", "баасы", "айлык", "колдоо",
}
RUSSIAN_WORDS = {
    "и", "в", "во", "не", "что", "это", "для", "как", "мы", "вы", "есть",
    "нужно", "хотим", "чтобы", "отвечал", "заявки", "клиентов", "вопрос",
    "можно", "да", "нет", "или", "на", "по", "с", "к", "у", "о", "же", "бы",
    "так", "вот", "всё", "все", "вам", "вас", "ваш", "мы", "наш", "цена",
    "стоимость", "сколько", "процесс", "агент", "внедрение", "поддержка",
}


def dominant_language(text: str) -> str:
    """Return 'ru', 'ky', or 'mixed' for a reply, by a documented heuristic."""
    low = normalize(text)
    tokens = re.findall(r"[а-яёңөү]+", low)
    ky_letters = sum(1 for ch in low if ch in KYRGYZ_LETTERS)
    ky_words = sum(1 for t in tokens if t in KYRGYZ_WORDS)
    ru_words = sum(1 for t in tokens if t in RUSSIAN_WORDS)
    ky_score = ky_letters * 3 + ky_words
    # Russian loanwords appear in Kyrgyz text too; weight Russian lower so a
    # Kyrgyz reply full of Russian business terms is still classified Kyrgyz.
    ru_score = ru_words
    if ky_score >= 3 and ky_score > ru_score:
        return "ky"
    if ru_score >= 3 and ru_score > ky_score * 1.5:
        return "ru"
    return "mixed"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip().casefold()


def contains(text: str, needle: str) -> bool:
    needle = normalize(needle)
    if re.fullmatch(r"\d+(?:[.,]\d+)?", needle):
        return re.search(rf"(?<!\d){re.escape(needle)}(?!\d)", text) is not None
    return needle in text


NEG_SUFFIX = re.compile(r"(байт|бейт|байм|бейм|байбыз|бейбиз|байсыз|бейсиз)$")


def has_negation(window: str) -> bool:
    """True if the window contains a negation, including Kyrgyz negative verb
    suffixes such as 'кылынбайт', 'бербейбиз', 'айтпайм'."""
    if any(token in window for token in NEGATION_TOKENS):
        return True
    return any(NEG_SUFFIX.search(word) for word in re.findall(r"[а-яёңөү]+", window))


def sentence_scope(text: str, index: int, end: int) -> str:
    """The sentence containing text[index:end]: from the sentence break before
    the match to the sentence break after it (sentence-ending punctuation or
    newline). Negation in the same sentence negates the phrase."""
    breaks = [m.start() for m in re.finditer(r"[.!?\n]", text[:index])]
    start = breaks[-1] + 1 if breaks else 0
    after = re.search(r"[.!?\n]", text[end:])
    end2 = end + after.start() if after else len(text)
    return text[start:end2]


def all_occurrences_negated(text: str, needle: str) -> bool:
    found = False
    start = 0
    while True:
        index = text.find(needle, start)
        if index == -1:
            return found
        found = True
        end = index + len(needle)
        window = sentence_scope(text, index, end)
        if not has_negation(window):
            return False
        start = end


def load_scenarios(path: Path) -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {s["id"]: s for s in data["scenarios"]}


def load_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def check_one(scenario: dict[str, Any], record: dict[str, Any]) -> list[str]:
    checks = scenario.get("checks", {}) or {}
    turns = record.get("turns", [])
    responses = [t.get("assistant", "") for t in turns if isinstance(t, dict)]
    full = normalize(" ".join(responses))
    final = normalize(responses[-1]) if responses else ""
    failures: list[str] = []

    for item in checks.get("must_include_all", []) or []:
        if not contains(full, item):
            failures.append(f"missing required phrase: {item!r}")

    for key in ("must_include_any", "must_include_any_2"):
        items = checks.get(key, []) or []
        if items and not any(contains(full, item) for item in items):
            failures.append(f"none of the allowed phrases appeared ({key}): {items}")

    for item in checks.get("must_not_include", []) or []:
        needle = normalize(item)
        if needle in full and not all_occurrences_negated(full, needle):
            failures.append(f"forbidden phrase appeared: {item!r}")

    for pattern in checks.get("must_not_regex", []) or []:
        match = re.search(pattern, " ".join(responses), re.IGNORECASE)
        if match:
            failures.append(f"forbidden regex matched: {pattern!r} -> {match.group(0)!r}")

    limit = checks.get("max_questions")
    if isinstance(limit, int):
        worst = max((r.count("?") for r in responses), default=0)
        if worst > limit:
            failures.append(f"asked {worst} questions in one turn; limit is {limit}")

    expected_language = checks.get("expect_reply_language")
    if expected_language and responses:
        observed = dominant_language(responses[-1])
        if expected_language == "ru" and observed == "ky":
            failures.append(f"reply is dominantly Kyrgyz; expected Russian (observed={observed})")
        elif expected_language == "ky" and observed == "ru":
            failures.append(f"reply is dominantly Russian; expected Kyrgyz (observed={observed})")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--scenarios", type=Path, default=ROOT / "tests" / "live" / "scenarios.yaml")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    scenarios = load_scenarios(args.scenarios)
    records = load_records(args.responses)
    results = []
    for record in records:
        sid = record.get("scenario_id")
        if sid not in scenarios:
            results.append({"scenario_id": sid, "passed": False, "failures": ["unknown scenario"]})
            continue
        failures = check_one(scenarios[sid], record)
        results.append({
            "scenario_id": sid,
            "category": scenarios[sid].get("category"),
            "locale": scenarios[sid].get("locale"),
            "passed": not failures,
            "failures": failures,
        })

    passed = sum(1 for r in results if r["passed"])
    summary = {
        "responses": str(args.responses),
        "scenario_count": len(scenarios),
        "recorded": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
