# Follow-Up Cadence and Message Templates

**Status:** implementation reference. All cadence values are placeholders that the business must set in the product passport. Nothing here is a recommended universal schedule.

---

## 1. Policy fields the passport must define

| Field | Example shape | Why it matters |
|---|---|---|
| `follow_up.allowed` | `true` / `false` | Some offers or channels prohibit proactive contact |
| `follow_up.basis` | `buyer_requested`, `agreed_next_step`, `existing_customer`, `buyer_initiated_inquiry`, `marketing_consent` | Defines what counts as permission |
| `follow_up.channels` | ordered list | Prevents channel hopping |
| `follow_up.quiet_hours` | local start/end + timezone | Protects the buyer's time |
| `follow_up.allowed_days` | e.g. Mon–Fri | Avoids weekend messages where inappropriate |
| `follow_up.max_attempts_per_reason` | integer | Prevents nagging |
| `follow_up.max_attempts_per_conversation` | integer | Caps the whole thread |
| `follow_up.min_interval_hours` | integer | Prevents rapid bumps |
| `follow_up.close_out_after_days` | integer (days) | Defines when to stop |
| `follow_up.marketing_consent_required` | boolean | Transactional consent is not marketing consent |
| `follow_up.opt_out_keywords` | list per language | Must include Russian and Kyrgyz variants |

Appointment recovery uses the booking contract's `no_show_policy` (`fulfillment.booking.no_show_policy`), not a separate follow-up field.

If a field is `unknown`, the safe behavior is: send only buyer-requested follow-ups, and ask for a date if none was given.

---

## 2. Eligibility state machine

```
                 ┌─────────────────────┐
                 │  reason + consent?  │
                 └──────────┬──────────┘
                            │
              no ───────────┴─────────── yes
               │                            │
        do not send                 human owns thread?
                                            │
                                  yes ──────┴────── no
                                   │                 │
                            do not send       within cadence?
                                                      │
                                            no ───────┴────── yes
                                             │                 │
                                      wait/stop          has new value?
                                                                  │
                                                        no ───────┴────── yes
                                                         │                 │
                                                   do not send          send one
                                                                       message
                                                                           │
                                              ┌────────────────────────────┼────────────────────────────┐
                                              │                            │                            │
                                           yes                          later                         no
                                              │                            │                            │
                                     execute next step          schedule one date            close loop
```

Hard gates:

1. explicit opt-out → stop forever for that purpose;
2. human handoff active → no automated sales message;
3. no new value → no message;
4. attempt cap reached → close out, do not rename the reason;
5. safety/legal issue → integrity path, not follow-up.

---

## 3. Message anatomy

A follow-up has four parts and no more:

1. **Context** — why now, one line.
2. **Value** — the new fact, document, answer, or decision aid.
3. **Ask** — one specific next step.
4. **Exit** — a real way to pause or close.

Optional: a single verified deadline, only if the passport documents it and it is relevant to the buyer.

Never include:

- "I hope this finds you well" as the whole value;
- a fake "bumping this";
- a countdown that is not in the passport;
- a discount introduced only because the buyer was silent;
- a question that the buyer already answered;
- a request for a review, referral, or case study in the same message as a support issue.

---

## 4. Templates

Replace `[verified …]` from the passport. Do not send placeholders. Kyrgyz lines are drafts pending native review.

### 4.1 Buyer-requested follow-up (Russian)

> Добрый день! Вы просили вернуться к вопросу [verified topic] [date/time]. Подготовил [verified value: summary/answer/document]. [One ask]. Если сейчас не время — скажите, и я закрою вопрос.

### 4.2 Buyer-requested follow-up (Kyrgyz, draft)

> Салам! [Verified topic] боюнча [date/time] кайра кайрылууну сурангансыз. [Verified value] даярдадым. [One ask]. Азыр убакыт туура келбесе, айтыңыз — суроону жабам.

### 4.3 Agreed next step

> Мы договорились вернуться [date/time] к [verified next step]. [Verified status/value]. [One ask]. Если планы изменились — напишите, подстроюсь.

### 4.4 Document ready

> Как обещал, отправил [document name] [id]. В нём [one verified point]. Посмотрите раздел [section] — если есть вопрос, отвечу здесь. Если документ не открывается, скажите, пришлю другой формат.

### 4.5 Proposal sent, decision date agreed

> Предложение [id] отправлено [date]. Вы планировали решение к [date]. [One verified point or answer to a known question]. Успели посмотреть? Если нужен разговор с [verified role], предложу реальное время.

### 4.6 Answer ready after escalation

> Вернулся с ответом по [verified question]. [Verified answer, with source/qualifier]. [One ask or next step]. Если этого достаточно, могу [verified next action].

### 4.7 No-show recovery

> Сегодня была запись на [date/time] с [verified role]. Вы не подключились. Хотите перенести? Есть [slot A] и [slot B] — проверены в календаре. Если вопрос больше не актуален, скажите, и я закрою его.

### 4.8 No-response close-out

> Не буду больше напоминать по этому вопросу. Если он вернётся, напишите сюда — помогу. Спасибо.

### 4.9 Post-purchase onboarding check-in

> Как проходит [verified onboarding step]? Если что-то не работает или непонятно, напишите — передам в поддержку. [Verified support channel]. Это сообщение не про апсейл; просто проверяю, что всё в порядке.

### 4.10 Re-engagement with marketing consent

> Вы разрешили присылать обновления по [verified topic]. Появилось [verified new fact: feature, date, document]. Если это больше не нужно — ответьте «стоп», и я отпишу.

### 4.11 Wrong person

> Похоже, я написал не тому человеку. Извините за беспокойство. Подскажите, пожалуйста, кто занимается [verified topic], или я закрою вопрос.

### 4.12 Buyer angry about the follow-up

> Вы правы, я написал без достаточного повода. Больше не буду. Если вопрос вернётся, вы можете написать сюда.

---

## 5. Response handling matrix

| Response | State update | Next action |
|---|---|---|
| `yes` | `decision: yes`, `consent` confirmed | Move to closing; execute only with a tool result |
| `no` | `decision: no`, `sequence: stopped` | One acknowledgment; no further sales |
| `not_now_with_date` | `follow_up.status: scheduled`, `follow_up.next_due_at` | One scheduled touch on that date |
| `not_now_without_date` | `follow_up.next_due_at: null` | Ask once for a date; otherwise close |
| `question` | Append to `open_questions` | Answer; do not treat as consent |
| `silence` | Increment attempts | Wait; then close per policy |
| `stop` | `opt_out: true`, `sequence: stopped` | Immediate stop; one neutral acknowledgment at most |
| `complaint` | `risk: complaint` | Acknowledge; human if needed; stop sales |
| `handoff_requested` | `handoff: requested` | Handoff; pause automation |
| `wrong_person` | `contact_status: wrong_person` | Ask for the right contact or close |
| `auto_reply` | `contact_status: unavailable` | Wait for the stated date; do not count as a response |

---

## 6. Copy review checklist

- [ ] The reason for the message is obvious in the first line.
- [ ] The message contains a fact, answer, document, or decision aid.
- [ ] There is at most one ask.
- [ ] The exit is real and will be honored.
- [ ] No invented deadline, discount, scarcity, or guilt.
- [ ] No "just checking in", "bumping", or "any update?".
- [ ] The language and register match the buyer.
- [ ] Names, amounts, dates, and document IDs are exact.
- [ ] The channel and timing are approved by the passport.
- [ ] The send result is confirmed by the messaging tool; a scheduled message is not described as sent.
- [ ] A scheduled message will be cancelled if the buyer opts out or replies before dispatch.
- [ ] A human-owned thread is not being interleaved.
- [ ] The attempt count and opt-out status are updated.

---

## 7. Metrics that do not corrupt behavior

Measure:

- reply rate by reason code;
- opt-out rate;
- complaint rate;
- time from buyer request to follow-up;
- percentage of follow-ups that contain a new value;
- close-out compliance (no message after stop).

Do not optimize only for meetings booked. That metric rewards pressure. Pair every growth metric with an opt-out and complaint guardrail.

No benchmark numbers are claimed here. Baselines must come from the business's own data.
