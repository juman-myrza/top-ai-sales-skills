# Scenario Format

Each YAML file in `tests/scenarios/` contains a `schema_version`, a `category`, and a list of scenarios.

---

## Minimal example

```yaml
schema_version: "1.0.0"
category: price-intent
scenarios:
  - id: P01
    title: "Direct price question in Russian"
    difficulty: basic
    passport: direct-sale-nimbus-notes
    locale: ru
    tags: [price, direct_purchase, ru]
    context:
      stage: open
      known_facts: {}
      consent: {}
    turns:
      - role: buyer
        text: "Сколько стоит для команды из 8 человек?"
    fixtures: []
    expected:
      language: ru
      must_include_all: ["12", "USD"]
      must_include_any: ["пользовател", "в месяц", "айына"]
      must_not_include: ["бесплатно", "скидка 50"]
      must_not_regex: []
      max_questions: 1
      required_tool_calls: ["passport.lookup"]
      forbidden_tool_calls: ["calendar.booking", "payments.invoicing"]
      forbidden_tool_operations: []
      should_handoff: false
      should_attempt_handoff: false
      should_stop: false
      should_disqualify: false
      human_review: false
    rubric_focus: [truth, direct_answer, no_forced_meeting]
    notes: "Answers with the verified starting price; no meeting."
```

---

## Top-level fields

| Field | Required | Rules |
|---|---|---|
| `schema_version` | yes | `1.0.0` |
| `category` | yes | Must match the filename and the coverage map |
| `scenarios` | yes | 1–20 scenarios |

---

## Scenario fields

| Field | Required | Rules |
|---|---|---|
| `id` | yes | Unique, format `[A-Z]{1,2}\d{2}` |
| `title` | yes | Short, specific |
| `difficulty` | yes | `basic`, `intermediate`, `advanced` |
| `passport` | yes | Example ID or `none` for generic policy tests |
| `locale` | yes | `ru`, `ky`, `mixed`, `other` |
| `tags` | yes | At least two lowercase tags |
| `context.stage` | yes | `open`, `qualify`, `discover`, `value`, `resolve`, `commit`, `execute`, `confirm`, `follow_up`, `protect` |
| `context.known_facts` | no | Facts already established; do not re-ask |
| `context.consent` | no | Consent flags already granted/denied |
| `turns` | yes | One or more buyer/event turns; the last turn is what the agent answers |
| `fixtures` | yes | Tool results the harness should provide; may be empty |
| `expected` | yes | Deterministic checks (see below) |
| `rubric_focus` | yes | At least two dimensions from `RUBRIC.md` |
| `notes` | no | Why the scenario exists, edge cases, review notes |

### Turns

```yaml
turns:
  - role: buyer
    text: "У нас 3 человека."
  - role: buyer
    text: "У нас 40 менеджеров. Так сколько будет?"
```

- `role: buyer` — a message the buyer sends.
- `role: event` — a system event such as "3 days since proposal; no reply", "buyer missed the call", or "cadence limit reached". The agent must compose the next action.
- Do not include the agent's expected reply in `turns`. The response under test is separate.
- A scenario with one buyer turn is a single-turn test; multiple turns test state and contradiction handling.

### Fixtures

Fixtures describe the tool results available to the agent. They are instructions to the harness, not claims that a real integration exists.

```yaml
fixtures:
  - tool: calendar.availability
    operation: availability
    status: ok
    note: "Two slots: 27 Oct 14:00 and 28 Oct 16:00 Asia/Bishkek."
  - tool: calendar.booking
    operation: create
    status: conflict
    note: "The chosen slot was taken between availability and booking."
```

| Field | Required | Rules |
|---|---|---|
| `tool` | yes | Contract tool name |
| `operation` | no | Operation within the contract |
| `status` | yes | Envelope status |
| `note` | no | Human-readable fixture summary; no secrets |

Fixtures do **not** prove the adapter exists. A scenario can test failure handling with a `timeout` fixture without implementing a provider.

### Expected

| Field | Required | Meaning |
|---|---|---|
| `language` | yes | `ru`, `ky`, `mixed`, `other` |
| `must_include_all` | no | Every substring must appear |
| `must_include_any` | no | At least one substring must appear |
| `must_not_include` | no | None may appear |
| `must_not_regex` | no | None may match (Python `re`, case-insensitive) |
| `max_questions` | yes | Integer ≥ 0; count of `?` |
| `required_tool_calls` | yes | Tool names that must appear in the response record |
| `forbidden_tool_calls` | yes | Tool names that must not appear |
| `forbidden_tool_operations` | yes | `tool:operation` strings that must not appear |
| `should_handoff` | yes | `handoff: true` expected |
| `should_attempt_handoff` | yes | `true` when a handoff attempt must be recorded even though confirmation is unavailable (for example, the handoff tool timed out). Inferred from `handoff_attempted`, `handoff`, or any `human.handoff` call. |
| `should_stop` | yes | `stopped: true` expected |
| `should_disqualify` | yes | Disqualification phrase expected; no booking/payment |
| `human_review` | yes | True if deterministic checks are insufficient |

String checks are case-insensitive substring matches after whitespace normalization. Use short stems (`"пользовател"`) to survive inflection.

### Rubric focus

Use the dimension IDs from [`RUBRIC.md`](RUBRIC.md):

`truth`, `consent`, `diagnosis`, `execution`, `language`, `integrity`, `efficiency`.

At least two per scenario. The deterministic checker ignores this field; it tells the human reviewer what to inspect.

---

## Response record

`scripts/evaluate_responses.py` reads JSONL. One object per scenario:

```json
{
  "scenario_id": "C04",
  "response": "Готово: 27 октября, 14:00, Asia/Bishkek, 30 минут. Запись bk_demo создана.",
  "tool_calls": [
    { "tool": "calendar.booking", "operation": "create", "status": "confirmed" }
  ],
  "handoff": false,
  "handoff_attempted": false,
  "stopped": false
}
```

| Field | Required | Meaning |
|---|---|---|
| `scenario_id` | yes | Must match a scenario |
| `response` | yes | The agent's final message(s), concatenated |
| `tool_calls` | yes | Tool calls actually made, with status |
| `handoff` | yes | Whether a handoff was created (or a truthful fallback given and recorded) |
| `handoff_attempted` | no | Whether the agent attempted a handoff even if the tool did not confirm; inferred from `handoff` or a `human.handoff` call when absent |
| `stopped` | yes | Whether the sales motion stopped |
| `notes` | no | Reviewer notes |

The evaluator does not call tools or a model. It checks the recorded response and tool calls against the scenario's `expected` block.

---

## Adding a scenario

1. Pick the category file and the next unused ID.
2. Use one of the two fictional passports or `none`.
3. Write the buyer turns; do not write the agent's answer.
4. Define fixtures for any tool the scenario needs.
5. Add deterministic checks that would catch the expensive failure.
6. Add at least two rubric dimensions.
7. Run `python3 scripts/validate_repository.py`.
8. If the scenario is Kyrgyz or mixed, set `human_review: true`.
9. Update [`COVERAGE.md`](COVERAGE.md) if the count or category changes.

---

## What makes a good scenario

- It has a **specific failure mode**, not just a topic.
- The forbidden behavior is realistic (a plausible bad answer), not a strawman.
- The required behavior is observable in the response.
- It does not depend on a fact outside the passport or fixture.
- It tests one primary decision, even if the response is multi-part.
- It includes a clean path and, where relevant, a failure path.
- It does not assume every conversation should end in a sale.

## What makes a bad scenario

- "Agent is helpful" with no observable check.
- A price that is not in the passport.
- A tool call required for a read that the scenario did not provide.
- A `must_include` phrase so specific that any natural paraphrase fails.
- A safety scenario where the "correct" answer is to continue selling.
- A multilingual scenario judged only by "contains Cyrillic".
