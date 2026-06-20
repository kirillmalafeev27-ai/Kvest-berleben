# 05. ПУЛ СОБЫТИЙ (YAML, готов к загрузке)

События в схеме из `../05` (§5.1). Это машинно-читаемая проекция сцен из `02`–`04`: одна сцена →
одно событие. Движок не знает их поимённо — применяет схему (планировщик `../05` §5.3, режиссёр
§5.4). Узлы N1–N9 помечены `once: true` + высокий `priority`; их флаги-исходы читает развязка.

Соглашения значений:
- `entry_conditions`: `all`/`any`/`none` — предикаты над `day`, `flags`, `axes`, `skills`, `money`, `location_in`, `faction_standing`, `leaning`, `timers`.
- `weight: success|fail` в outcome — означает «выбирается по результату skill_check».
- `delta_hints` — подсказка Analyst (он скорректирует, код клампит).
- id локаций — из `../06` §6.4. id интентов — из v0.1 §1.3.

---

## Узлы-«стрелки» (dilemma, once)

```yaml
- id: node_buergeramt              # N1 — сцена s_buergeramt
  title: "Окошко Bürgeramt"
  category: dilemma
  priority: 85
  once: true
  trigger: scheduled              # становится due на день 2
  entry_conditions: { all: [ {day_gte: 2}, {flag_not: "did_anmeldung"} ], none: [ {flag: "node_buergeramt_done"} ] }
  stakes: medium
  setup:
    scene_facts:
      - "Зал ожидания, табло номеров. За стойкой — фрау Беккер."
      - "Ближайший термин на Anmeldung — через 8 недель."
      - "Без Anmeldung заблокированы счёт, легальная работа, нормальная SIM."
    present_targets: [npc_frau_becker]
    player_state_hints: [deutsch_skill, money, status_timer]
  branches:
    - id: honest_wait
      match_intents: [{verb: inquire_status}, {verb: talk, honesty: truthful, tone: polite}]
      skill_check: { skill: deutsch, vs: 30, soft: true }
      outcomes:
        - weight: 1.0
          result: "Беккер: 'Leider. Не я придумала правила.' Намекает, что иногда отменяют."
          effects: { set_flag: ["node_buergeramt_done", "becker_honest"] }
          delta_hints: { TRUTH: +1, LAW: +1 }
          official_note: { dossier: shared_clerks, note: "обратился честно, вежливо" }
          followups: [arc_lena_loophole]
    - id: lie_urgency
      match_intents: [{verb: deceive, honesty: lie}, {verb: persuade, method: emotional_appeal, honesty: lie}]
      skill_check: { skill: deutsch, vs: 40, plus: { obman: 0.5 } }
      outcomes:
        - weight: success
          result: "Верит, записывает на ближайшую отмену."
          effects: { set_flag: ["node_buergeramt_done", "got_early_slot"] }
          delta_hints: { TRUTH: -4 }
          official_note: { dossier: shared_clerks, note: "ссылался на срочность (непроверено)" }
        - weight: fail
          result: "'Hier steht etwas anderes.' Холодно делает пометку."
          effects: { set_flag: ["node_buergeramt_done", "becker_distrust"] }
          delta_hints: { TRUTH: -4 }
          official_note: { dossier: shared_clerks, note: "ПЫТАЛСЯ ВВЕСТИ В ЗАБЛУЖДЕНИЕ" }   # выстрел на N9
    - id: aggressive
      match_intents: [{verb: threaten}, {verb: talk, tone: aggressive}]
      outcomes:
        - weight: 1.0
          result: "Беккер замыкается, грозит вызвать охрану. Строго по букве."
          effects: { set_flag: ["node_buergeramt_done", "becker_distrust"] }
          delta_hints: { AGGRO: +4, PRIDE: +2, LAW: -1 }
          rumor_tags: [{tag: "скандалист", faction: clerks, intensity: 0.5}]
          official_note: { dossier: shared_clerks, note: "агрессивное поведение" }
    - id: bribe_clerk
      match_intents: [{verb: bribe, method: money}]
      outcomes:
        - weight: 1.0
          result: "Холодный отказ. Пометка."
          effects: { set_flag: ["node_buergeramt_done", "becker_distrust"] }
          delta_hints: { TRUTH: -2, LAW: -3 }
          official_note: { dossier: shared_clerks, note: "ПЫТАЛСЯ ДАТЬ ВЗЯТКУ" }            # опасно на N9
    - id: seek_workaround
      match_intents: [{verb: book_appointment, method: through_fixer}]
      outcomes:
        - weight: 1.0
          result: "Уходишь искать обход — Олег/Али на горизонте."
          effects: { set_flag: ["node_buergeramt_done"], set_leaning: { gray: +1 } }
          delta_hints: { LAW: -1 }
  fallback_branch: { result: "Беккер: 'Der nächste, bitte.' Тянуть нельзя.", reopen: true }
```

```yaml
- id: node_first_job               # N2 — сцена s_first_job
  title: "Доска у Карима"
  category: dilemma
  priority: 80
  once: true
  trigger: scheduled
  entry_conditions: { all: [ {day_gte: 3}, {money_lt: 1000}, {flag_not: "has_income"} ] }
  stakes: high
  setup:
    scene_facts:
      - "Доска: 'Стройка — спросить Богдана'; 'Кафе Мехмета — мойщик, нужно понравиться'; 'Курьер — Али, интернет-кафе'."
    present_targets: [npc_karim]
  branches:
    - id: construction
      match_intents: [{verb: work, method: illegal_shift}]
      effects: { set_flag: ["has_income", "knows_bogdan"], set_leaning: { crime: +2, community_cross: +1 } }
      delta_hints: { LAW: -2, PRIDE: +1 }
      followups: [arc_bogdan_shift]
    - id: kebab
      match_intents: [{verb: ask_help, target: npc_mehmet}, {verb: befriend, target: npc_mehmet}]
      skill_check: { skill: social_humility, vs: 35, plus: { pride_low: 0.5 } }
      outcomes:
        - weight: success
          result: "Мехмет: 'Завтра в семь. Опоздаешь — не приходи.'"
          effects: { set_flag: ["has_income", "works_mehmet"], set_leaning: { legal: +1, community_cross: +2 } }
          delta_hints: { ALTRU: +1 }
          followups: [arc_mehmet_trust]
        - weight: fail
          result: "'Приходи, когда дозреешь.'"
          effects: {}
    - id: courier_gray
      match_intents: [{verb: work, method: gig}, {verb: talk, target: npc_ali}]
      effects: { set_flag: ["has_income"], set_leaning: { gray: +2 } }
      delta_hints: { LAW: -1 }
      followups: [arc_ali_courier]
    - id: hold_pride
      match_intents: [{verb: refuse}, {verb: search, props: {for: qualified_job}}]
      requires: { axis_gte: { PRIDE: 30 } }
      outcomes:
        - weight: 1.0
          result: "'Ты не за этим ехал.' Деньги тают быстрее."
          effects: { set_leaning: { legal: +1, bubble: +1 } }
          delta_hints: { PRIDE: +3 }
          followups: [pressure_money_tightens]
```

```yaml
- id: node_bogdan_underpaid        # N3 — сцена s_bogdan_underpaid
  title: "Недоплата"
  category: dilemma
  priority: 75
  once: true
  trigger: chain                   # после 3 смен (arc_bogdan_shift)
  entry_conditions: { all: [ {flag: "knows_bogdan"}, {counter_gte: {bogdan_shifts: 3}} ] }
  stakes: medium
  setup:
    scene_facts:
      - "Богдан суёт смятые купюры — половины обещанного не хватает."
    present_targets: [npc_bogdan]
  branches:
    - id: swallow
      match_intents: [{verb: refuse, method: polite}, {verb: rest}]
      outcomes:
        - weight: 1.0
          result: "Берёшь половину молча. Богдан даже не смотрит."
          effects: { money: "+half_wage", set_flag: "bogdan_marks_weak" }
          delta_hints: { PRIDE: -3 }
          rumor_tags: [{tag: "слабый, можно кидать", faction: black_employers, intensity: 0.5}]
    - id: demand
      match_intents: [{verb: persuade, tone: aggressive}, {verb: refuse, method: firm}]
      skill_check: { skill: hladnokrovie, vs: 35, plus: { pride_high: 0.5 } }
      outcomes:
        - weight: success
          result: "Богдан хмыкает: 'Зубы есть. Уважаю.' Достаёт остальное."
          effects: { money: "+full_wage", set_flag: "bogdan_respect" }
          delta_hints: { PRIDE: +3, AGGRO: +2 }
          rumor_tags: [{tag: "не дал себя кинуть", faction: street, intensity: 0.5}]
        - weight: fail
          result: "Богдан: 'Не нравится — вон биржа.' Половина и испорченные отношения."
          effects: { money: "+half_wage" }
          delta_hints: { PRIDE: +1, AGGRO: +2 }
    - id: threaten_violence
      match_intents: [{verb: threaten, method: violence}]
      outcomes:
        - weight: 1.0
          result: "Напряжение. Богдан отдаёт деньги, но ты нажил врага на стройке."
          effects: { money: "+full_wage", set_flag: "bogdan_enemy" }
          delta_hints: { AGGRO: +5, LAW: -2 }
    - id: via_victor
      match_intents: [{verb: ask_help, target: npc_victor}]
      requires: { flag: "knows_victor" }
      outcomes:
        - weight: 1.0
          result: "Виктор 'решает'. Деньги возвращаются. Но теперь ты должен Виктору."
          effects: { money: "+full_wage", set_flag: "owes_victor", set_leaning: { crime: +1 } }
          delta_hints: { LAW: -2 }
          followups: [arc_victor_debt]            # выстрел в Акте II/III
```

*(N4 — `arc_doctor_intro` / `arc_lena_loophole`; N5 — `node_emilia_asks`; N6 — `node_zoll_raid`;
N7 — `node_scheinehe_offer`; N8 — `node_newcomer_mirror`; N9 — `node_letter_lea`. Полные карточки
строятся по образцу выше из соответствующих сцен `03`/`04`.)*

```yaml
- id: node_emilia_asks             # N5 — сцена s_emilia_asks
  title: "Эмилия спрашивает прямо"
  category: dilemma
  priority: 70
  once: true
  trigger: chain
  entry_conditions: { all: [ {counter_gte: {emilia_meetings: 3}} ], location_in: [cafe_third_wave] }
  stakes: low
  setup:
    scene_facts: ["Эмилия садится напротив в перерыв: 'Чем ты тут занимаешься? Только по-честному.'"]
    present_targets: [npc_emilia]
  branches:
    - id: truth
      match_intents: [{verb: talk, honesty: truthful}]
      outcomes:
        - weight: 1.0
          result: "'Honest. Это сейчас редкость.' Теплеет искренне."
          effects: { set_flag: "emilia_trust", relationship: {emilia: +2} }
          delta_hints: { TRUTH: +2 }
    - id: lie
      match_intents: [{verb: deceive, honesty: lie}]
      outcomes:
        - weight: 1.0
          result: "Мило улыбается, но что-то отметила про себя."
          effects: { set_flag: "lied_to_emilia" }       # выстрел: s_emilia_construction_reveal
          delta_hints: { TRUTH: -2 }
          followups: [emilia_construction_reveal]
    - id: dodge
      match_intents: [{verb: refuse}, {verb: talk, tone: submissive}]
      outcomes:
        - weight: 1.0
          result: "Уходишь от ответа. Эмилия чуть отстраняется."
          delta_hints: { PRIDE: -1 }
```

---

## Давление и реакции (pressure / reactive)

```yaml
- id: ubahn_control                # сцена s_ubahn_control (см. ../05 §5.1 — полный образец)
  title: "Контролёры в U-Bahn"
  category: pressure
  priority: 50
  trigger: reactive
  cooldown_days: 3
  entry_conditions: { all: [ {location_in: [ubahn_station, ubahn_car]}, {flag: "moved_without_ticket"} ], none: [ {flag: "ubahn_control_cooldown"} ] }
  stakes: medium
  setup:
    scene_facts: ["Двое контролёров в штатском перекрыли выход.", "Действительного билета нет.", "Штраф 60 €."]
    present_targets: [npc_controller_a, npc_controller_b]
  branches:
    - id: pay
      match_intents: [{verb: give, props: {reason: fine}}, {verb: trade, method: buy}]
      requires: { money_gte: 60 }
      outcomes: [{ weight: 1.0, result: "Штраф уплачен.", effects: {money: -60}, delta_hints: {LAW: +1} }]
    - id: persuade
      match_intents: [{verb: persuade, method: pity}, {verb: deceive, honesty: lie}]
      skill_check: { skill: deutsch, vs: 40, plus: {persuasion: 0.5} }
      outcomes:
        - { weight: success, result: "'Beim nächsten Mal!' Пронесло.", delta_hints: {TRUTH: -2}, rumor_tags: [{tag: ловкий, faction: street, intensity: 0.3}] }
        - { weight: fail, result: "Не верит. Штраф 60 € + заметка.", effects: {money: -60}, delta_hints: {TRUTH: -3}, official_note: {dossier: shared_clerks, note: "попытка обмана контроля"} }
    - id: flee
      match_intents: [{verb: flee}]
      skill_check: { skill: ulitsa, vs: 50 }
      outcomes:
        - { weight: success, result: "Ныряешь в толпу. Сердце колотится.", delta_hints: {LAW: -2, AGGRO: +1}, skill_xp: {ulitsa: +3, hladnokrovie: +2} }
        - { weight: fail, result: "Хватают. Штраф + проверка документов...", effects: {money: -60}, delta_hints: {LAW: -3}, followups: [doc_check_risk] }
  fallback_branch: { result: "'Fahrschein, bitte.' Тянуть нельзя.", reopen: true }
```

```yaml
- id: hostel_runs_out              # сцена s_hostel_ends
  title: "Хостел кончается"
  category: pressure
  priority: 78
  once: true
  trigger: scheduled
  entry_conditions: { all: [ {day_gte: 5} ], location_in: [hostel_komet] }
  stakes: high
  setup:
    scene_facts: ["Оплаченные ночи вышли.", "Виктор: 'матрас у знакомых, 200/мес, без вопросов'.", "Комнаты по объявлениям требуют Anmeldung."]
    present_targets: [npc_victor]
  branches:
    - id: pay_more
      match_intents: [{verb: trade, method: buy}, {verb: rest, method: sleep}]
      requires: { money_gte: 35 }
      outcomes: [{ weight: 1.0, result: "Ещё ночь за 35 €. Решение отложено.", effects: {money: -35} }]
    - id: victor_mattress
      match_intents: [{verb: ask_help, target: npc_victor}]
      outcomes: [{ weight: 1.0, result: "Матрас у знакомых Виктора, 200/мес, без Anmeldung.", effects: {set_flag: "lives_with_victor", relationship: {victor: +1}}, delta_hints: {LAW: -1} }]
    - id: try_white_rent
      match_intents: [{verb: apply, props: {type: room}}, {verb: search, props: {for: room}}]
      outcomes: [{ weight: 1.0, result: "Стена: Anmeldung/Schufa/WBS. Отказ.", effects: {set_flag: "hit_housing_wall"} }]
```

```yaml
- id: money_tightens
  title: "Деньги тают"
  category: pressure
  priority: 40
  trigger: pool
  weight: 1.5
  cooldown_days: 4
  entry_conditions: { all: [ {money_lt: 300} ] }
  stakes: medium
  setup:
    scene_facts: ["Кошелёк пустеет. Дневной расход не остановить."]
  branches:
    - id: sell_laptop
      match_intents: [{verb: trade, method: sell, props: {item: laptop}}]
      requires: { flag: "has_laptop" }
      outcomes: [{ weight: 1.0, result: "Продал ноут. Деньги есть — актива удалёнки нет.", effects: {money: "+laptop_value", unset_flag: "has_laptop"}, delta_hints: {PRIDE: -2} }]
    - id: borrow_karim
      match_intents: [{verb: borrow, target: npc_karim}]
      skill_check: { skill: reputation_street, vs: 20 }
      outcomes:
        - { weight: success, result: "Карим даёт в долг по репутации.", effects: {money: +20, set_flag: "owes_karim"} }
        - { weight: fail, result: "'Заслужи сначала.'", effects: {} }
```

```yaml
- id: doc_check_risk               # эскалация после провала flee / для рисковых статусов
  title: "Проверка документов"
  category: reactive
  priority: 65
  trigger: chain
  entry_conditions: { any: [ {flag: "has_fake_anmeldung"}, {leaning_gte: {crime: 3}} ] }
  stakes: high
  setup:
    scene_facts: ["Полиция просит документы. Если статус/бумаги рисковые — это опасно."]
    present_targets: [npc_cop_profiling]
  branches:
    - id: show_fake
      match_intents: [{verb: submit_docs, method: forged}]
      requires: { flag: "has_fake_anmeldung" }
      skill_check: { skill: hladnokrovie, vs: 55 }
      outcomes:
        - { weight: success, result: "Прокатило. Холодный пот.", delta_hints: {LAW: -1} }
        - { weight: fail, result: "Фейк раскрыт. Это уже не штраф...", effects: {set_flag: "caught_with_fake"}, delta_hints: {LAW: -8}, followups: [node_letter_lea] }
    - id: comply_clean
      match_intents: [{verb: submit_docs, method: genuine}]
      requires: { flag_not: "has_fake_anmeldung" }
      outcomes: [{ weight: 1.0, result: "Документы в порядке (насколько есть). Отпускают.", delta_hints: {} }]
```

---

## Сообщество и выдохи (community / ambient)

```yaml
- id: community_dinner             # сцена s_community_dinner
  title: "Ужин общины"
  category: community
  priority: 60
  cooldown_days: 14
  trigger: pool
  entry_conditions: { all: [ {faction_standing: {turkish: gte, value: 20}}, {rumor_tag: "надёжный"} ] }
  stakes: low
  setup:
    scene_facts: ["Мехмет зовёт на семейный ужин.", "За столом — Хасан, у которого сдаётся комната без формальностей."]
    present_targets: [npc_mehmet]
  branches:
    - id: warm
      match_intents: [{verb: talk, method: casual}, {verb: offer_help}, {verb: befriend}]
      outcomes: [{ weight: 1.0, result: "Тепло. Хасан кивает — комната твоя.", effects: {faction_standing: {turkish: +8}, unlock_event: room_sublet}, delta_hints: {ALTRU: +1, AGGRO: -1}, rumor_tags: [{tag: "свой человек", faction: turkish, intensity: 0.6}] }]
    - id: transactional
      match_intents: [{verb: persuade, props: {claim: need_room}}, {verb: bribe}]
      outcomes: [{ weight: 1.0, result: "Сразу про дело — Хасан холодеет.", effects: {faction_standing: {turkish: +2}}, delta_hints: {ALTRU: -1, TRUTH: -1} }]
```

```yaml
- id: schmidt_bags                 # сцена s_schmidt_bags (семя арки Einliegerwohnung)
  title: "Сумки фрау Шмидт"
  category: dilemma
  priority: 55
  once: true
  trigger: scheduled
  entry_conditions: { all: [ {day_gte: 4} ], location_in: [street_neukoelln] }
  stakes: low
  setup:
    scene_facts: ["Фрау Шмидт роняет пакеты у подъезда. Награды не обещано."]
    present_targets: [npc_frau_schmidt]
  branches:
    - id: help_selfless
      match_intents: [{verb: offer_help, method: labor}]
      none_props: { expects_reward: true }
      outcomes: [{ weight: 1.0, result: "'Вы... ничего не просите. Странно.'", effects: {set_flag: "helped_schmidt_selfless"}, delta_hints: {ALTRU: +3} }]   # выстрел в Акте III
    - id: help_for_reward
      match_intents: [{verb: offer_help, props: {expects_reward: true}}]
      outcomes: [{ weight: 1.0, result: "Холодеет. 'Я так и думала.'", delta_hints: {ALTRU: +1} }]
    - id: ignore
      match_intents: [{verb: move}]
      outcomes: [{ weight: 1.0, result: "Собирает сама, медленно.", delta_hints: {ALTRU: -1} }]
```

```yaml
- id: relief_hasenheide            # выдох для режиссёра давления
  title: "День в Хазенхайде"
  category: ambient
  priority: 30
  trigger: pool
  weight: 1.0
  entry_conditions: { all: [ {director_tension_gte: 0.6} ], location_in: [hasenheide_park] }
  stakes: trivial
  setup:
    scene_facts: ["Бегуны, шахматисты на скамейках, солнце.", "Город на минуту перестаёт давить."]
  branches:
    - id: rest
      match_intents: [{verb: rest, method: idle}, {verb: observe}]
      outcomes: [{ weight: 1.0, result: "Передышка. Стресс спадает.", effects: {stress: -10}, delta_hints: {} }]
    - id: chess
      match_intents: [{verb: talk, method: casual}]
      outcomes: [{ weight: 1.0, result: "Партия в шахматы со стариком. Тёплая случайная встреча.", effects: {stress: -8}, delta_hints: {ALTRU: +1} }]
```

---

## Заметки для загрузки

- Все события выше валидируются на старте (`../05` §5.7): существование интентов/навыков/локаций/фракций, достижимость условий, отсутствие «сиротских» followups.
- Спецзначения эффектов (`+half_wage`, `+laptop_value`, `+full_wage`) движок резолвит из таблицы экономики (баланс — отдельная задача, v0.1 §4.3.3).
- `director_tension_gte` читается из режиссёра давления (`../05` §5.4).
- Пул намеренно покрывает спайн (узлы N) + по 2–3 события на категорию pressure/community/ambient — этого хватает на играбельный вертикальный срез Акта I и начала Акта II. Полный пул (~30–40, v0.1 §4.3.1) добивается по сценам `03`/`04`.
