# 05. СИСТЕМА СОБЫТИЙ

Цель: события — это **данные, а не код**. Тогда LLM-исполнитель (и сама игра в рантайме)
сможет генерировать их пачками по схеме, а движок — единообразно их планировать, проверять
условия и резолвить. Это отвечает на «как создать систему событий, которые на игрока
сваливаются».

## 5.1. Анатомия события (схема)

Событие — декларативный объект. Ниже схема (YAML для читаемости; в БД — JSON).

```yaml
id: ubahn_control_01
title: "Контролёры в U-Bahn"
category: pressure            # ambient | pressure | reactive | arc | community | dilemma
arc_id: null                  # если часть цепочки — id арки
priority: 50                  # 0-100; чем выше, тем раньше в очереди дня

entry_conditions:             # ВСЕ должны выполниться (предикаты над стейтом)
  all:
    - location_in: [ubahn, sbahn]
    - flag: "moved_without_ticket"      # игрок только что прокатился зайцем
    - day_gte: 1
  any: []                     # хватит любого из списка
  none:                       # ни один не должен выполниться
    - flag: "ubahn_control_cooldown"

trigger: reactive             # scheduled(date) | pool(random) | reactive(after action) | chain(after event)
weight: 1.0                   # вес при сэмплинге из пула
cooldown_days: 3              # не повторять чаще
once: false                   # одноразовое ли (узлы N — часто true)

stakes: medium                # trivial | low | medium | high | extreme — подсказка Analyst по весу дельт

setup:                        # «факты сцены» для Narrator (жёстко; вне списка — выдумывать нельзя)
  scene_facts:
    - "Двое контролёров в штатском перекрыли выход на Hermannplatz."
    - "У игрока нет действительного билета."
    - "Штраф за безбилетный проезд — 60 €."
  present_targets: [npc_controller_a, npc_controller_b]
  player_state_hints: [money, deutsch_skill, ulitsa_skill, status_risk]

branches:                     # как игрок может реагировать (распознаётся через интенты парсера)
  - id: pay_fine
    match_intents: [{verb: trade, method: buy}, {verb: give, props:{reason: fine}}]
    requires: { money_gte: 60 }
    skill_check: null
    outcomes:
      - weight: 1.0
        result: "Штраф уплачен. -60 €. Контролёр кивает."
        effects: { money: -60 }
        delta_hints: { LAW: +1 }            # подчинился правилу постфактум
        rumor_tags: []
        followups: []

  - id: persuade_no_ticket
    match_intents: [{verb: persuade, method: pity}, {verb: deceive, honesty: lie}]
    skill_check: { skill: deutsch, vs: 40, plus: { persuasion: 0.5 } }
    outcomes:
      - weight: success
        result: "Контролёр машет рукой: 'Beim nächsten Mal!'. Пронесло."
        effects: {}
        delta_hints: { TRUTH: -3, AGGRO: 0 }
        rumor_tags: [{tag: "ловкий", faction: street, intensity: 0.3}]
      - weight: fail
        result: "Не верит. Штраф 60 €, плюс заметка о попытке обмана."
        effects: { money: -60 }
        delta_hints: { TRUTH: -3 }
        official_note: { dossier: shared_clerks, note: "пытался обмануть контроль" }

  - id: flee
    match_intents: [{verb: flee}]
    skill_check: { skill: ulitsa, vs: 50 }
    outcomes:
      - weight: success
        result: "Ныряешь в толпу, выскакиваешь на Karl-Marx-Straße. Сердце колотится."
        effects: {}
        delta_hints: { LAW: -2, AGGRO: +1 }
        skill_xp: { ulitsa: +3, hladnokrovie: +2 }
      - weight: fail
        result: "Хватают за рукав. Теперь и штраф, и подозрение. Проверка документов..."
        effects: { money: -60 }
        delta_hints: { LAW: -3 }
        followups: [doc_check_risk_01]      # если статус рисковый — цепочка-эскалация

  - id: aggro_scandal
    match_intents: [{verb: threaten}, {verb: talk, tone: aggressive}]
    outcomes:
      - weight: 1.0
        result: "Скандалишь. Пассажиры косятся. Контролёр вызывает наряд BVG."
        effects: { money: -60 }
        delta_hints: { AGGRO: +4, PRIDE: +2, LAW: -1 }
        rumor_tags: [{tag: "скандальный", faction: neighbors, intensity: 0.4}]

fallback_branch:              # если интент не подходит ни к одной ветке
  result: "Контролёр повторяет: 'Fahrschein, bitte.' Тянуть нельзя."
  reopen: true                # событие остаётся открытым, ждём валидный интент
```

**Ключевые поля:**
- `entry_conditions` — предикаты `all/any/none` над `day`, `location`, `flags`, `axes`, `skills`, `rumor_tags`, `faction_standing`, `resources`, `status/timers`. Это и есть «гейты» из `03`/`04`.
- `branches[].match_intents` — паттерны интентов (verb/method/honesty/tone/props) из словаря парсера (v0.1 §1.3). Резолвер матчит распарсенный интент игрока на ветку.
- `skill_check` — порог по навыку (+вклад смежного); исход success/fail взвешивается RNG с логируемым сидом (воспроизводимость, v0.1 §4.2.5).
- `delta_hints` — **подсказка** Analyst (не приказ): он учтёт контекст (голод, ставки, анти-фарм) и вернёт финальные дельты, код их клампит.
- `rumor_tags` / `official_note` — питают граф молвы и дело чиновников (v0.1 §2.4).
- `followups` — id событий-продолжений (механизм цепочек/арок).

## 5.2. Категории событий (пулы)

| Категория | Назначение | Частота |
|---|---|---|
| **ambient** | колорит, «жизнь района», мелкие соц-сцены без ставок | высокая, фоном |
| **pressure** | тикающее давление: деньги, бюрократия, тело, статус | по расписанию/триггерам |
| **reactive** | прямое последствие действия игрока (зайцем→контроль) | по триггеру |
| **arc** | шаг многоходовой сюжетной арки (виза, жильё, любовь, долг) | по цепочке |
| **community** | гейтятся репутацией во фракции; ужины, помощь, обязательства | по порогам |
| **dilemma** | узлы-«стрелки» N1–N9 и центральные дилеммы бэкграундов; высокие ставки | редко, веха |

## 5.3. Планировщик дня (Day Scheduler)

Каждый игровой «тик дня» (или смена локации) движок:

1. **Применяет pressure-таймеры** (списывает дневной расход, двигает сроки статуса/жилья, голод/усталость).
2. **Собирает кандидатов:** все события, чьи `entry_conditions` истинны и `cooldown`/`once` позволяют.
3. **Ставит обязательные** (scheduled на сегодня, активные `arc`-шаги, узлы N с выполненными условиями) — они идут вне сэмплинга, по `priority`.
4. **Сэмплирует пул** (ambient/community/random-pressure) по `weight`, с учётом «режиссёра» (5.4).
5. **Применяет пейсинг-правила:** не более N high/extreme-событий в день; гарантирует «дни-выдохи»; не ставит две катастрофы подряд.
6. **Отдаёт очередь дня** игроку как поток ситуаций; reactive-события вклиниваются по факту действий.

```
tick_day():
  apply_pressure()
  cand = [e for e in events if eval(e.entry_conditions) and not on_cooldown(e)]
  forced = [e for e in cand if e.trigger in (scheduled_today, arc_step, node_due)]
  pool   = [e for e in cand if e.category in (ambient, community, random_pressure)]
  pool   = director_adjust(pool, tension, resources)        # см. 5.4
  day_queue = sort_by_priority(forced) + weighted_sample(pool, k=pacing_budget())
  return enforce_pacing(day_queue)
```

## 5.4. «Режиссёр давления» (Director)

Мета-слой (как AI-режиссёр в Left 4 Dead, но про бюрократический ужас и нужду). Держит
**кривую напряжения**, чтобы давление не было ни монотонным, ни случайно-жестоким.

- Считает **tension** из: остаток денег, дни до статуса-дедлайна, голод/усталость/стресс, число недавних провалов.
- **Высокий tension → подмешивает relief** (событие-выдох: ужин общины, добрый жест чужого, маленькая победа, день в Хазенхайде) — не дать игроку сломаться без шанса.
- **Низкий tension / «слишком гладко» → подмешивает pressure** (письмо из ведомства, неожиданный расход, кидок) — не дать заскучать.
- Уважает **бэкграундовую дилемму**: периодически поднимает именно её конфликт (Студенту — счётчик Sperrkonto; Войне — новость с фронта; Заработку — давление слать деньги).
- Антифарм-связь: если игрок долбит один приём, режиссёр поднимает шанс контр-события (зайцем каждый день → контроль участился; врёшь всем → кто-то ловит на лжи).

## 5.5. Три проработанных события

### А. `pressure` — «Контролёры в U-Bahn»
Полностью расписано выше (5.1). Учебный пример всех веток и полей.

### Б. `dilemma` (узел N2) — «Первый заработок»
```yaml
id: node_first_job
title: "Доска объявлений у Карима"
category: dilemma
priority: 80
once: true
entry_conditions: { all: [ {day_gte: 3}, {money_lt: 1000}, {flag_not: "has_income"} ] }
stakes: high
setup:
  scene_facts:
    - "Доска у шпэти: 'Стройка, оплата в конце дня, спросить Богдана'."
    - "Объявление от руки: 'Кафе Мехмета — мойщик, нужно понравиться'."
    - "Листок: 'Курьер, гибкий график — Али, интернет-кафе'."
  present_targets: [npc_karim]
branches:
  - id: go_construction
    match_intents: [{verb: work, method: illegal_shift}]
    effects: { set_leaning: { crime: +2, community_cross: +1 }, set_flag: "knows_bogdan" }
    delta_hints: { LAW: -2, PRIDE: +1 }
    followups: [arc_bogdan_01]
  - id: go_kebab
    match_intents: [{verb: ask_help}, {verb: befriend, target: npc_mehmet}]
    requires_soft: { note: "нужно понравиться Мехмету — отдельная соц-проверка" }
    effects: { set_leaning: { legal: +1, community_cross: +2 } }
    delta_hints: { ALTRU: +1 }
    followups: [arc_mehmet_dishwasher_01]
  - id: go_courier_gray
    match_intents: [{verb: work, method: gig}, {verb: talk, target: npc_ali}]
    effects: { set_leaning: { gray: +2 } }
    delta_hints: { LAW: -1 }
    followups: [arc_ali_courier_01]
  - id: hold_out_pride
    match_intents: [{verb: refuse}, {verb: search, method: area, props:{for: "qualified_job"}}]
    requires_archetype_zone: { PRIDE_gt: 30 }
    effects: { set_leaning: { legal: +1, bubble: +1 } }
    delta_hints: { PRIDE: +3 }
    result: "Ты не за этим ехал. Захлопываешь блокнот. Деньги тают быстрее."
    followups: [pressure_money_tightens]
```
Перекраски по бэкграунду: для «Беженца» вместо стройки — «помыть посуду у своего за гроши»
(лояльность общине); для «Заработка» стройка — родная стихия (Труд-бонус); для «Студента»
курьерка конфликтует с лимитом часов (риск визе).

### В. `community` — «Ужин общины»
```yaml
id: comm_dinner_mehmet
title: "Приглашение на ужин"
category: community
priority: 60
entry_conditions: { all: [ {faction_standing: {turkish: gte, value: 20}}, {rumor_tag: "надёжный"} ] }
cooldown_days: 14
stakes: low
setup:
  scene_facts:
    - "Мехмет зовёт на семейный ужин в задней комнате кебабной."
    - "За столом — родня и Хасан, у которого сдаётся комната без формальностей."
branches:
  - id: attend_warm
    match_intents: [{verb: talk, method: casual}, {verb: offer_help}, {verb: befriend}]
    effects: { faction_standing: {turkish: +8}, unlock_event: comm_room_sublet }
    delta_hints: { ALTRU: +1, AGGRO: -1 }
    rumor_tags: [{tag: "свой человек", faction: turkish, intensity: 0.6}]
  - id: attend_transactional
    match_intents: [{verb: persuade, props:{claim: "need_room"}}, {verb: bribe}]
    effects: { faction_standing: {turkish: +2} }
    delta_hints: { ALTRU: -1, TRUTH: -1 }
    result: "Сразу про дело. Хасан холодеет: за столом так не принято."
```

## 5.6. Каталог заготовок событий (~40 сидов к прототипу)

Формат: `id — категория — условие → суть`. Это посевной список для LLM-генерации;
расширять до ~30–40 на акт. (★ — узлы-«стрелки» из `04`.)

**Бюрократия / статус (pressure, arc, dilemma)**
- ★`node_buergeramt_window` — dilemma — день 2 → термина нет: ждать/давить/врать/обход (N1).
- `appt_cancel_lifehack` — arc — Бюрократия>15 или совет Лены → лайфхак с отменами в 7 утра, мини-игра настойчивости.
- `letter_auslaenderbehoerde` — pressure — акт III → письмо, всплывает история TRUTH из дела (N9).
- `bamf_anhoerung` — dilemma — линия «Беженец», акт II/III → собеседование: правда vs «правильная история».
- `integration_course_test` — arc — линия «Воссоединение» → языковой экзамен, гейт продления.
- `sperrkonto_lowbalance` — pressure — линия «Студент» → остаток счёта критичен.
- `doc_check_risk` — reactive — рисковый статус + засветка → проверка документов (страшно для «Невидимки»).

**Деньги / работа (pressure, arc)**
- ★`node_first_job` — dilemma — день 3 (выше) (N2).
- ★`bogdan_underpaid` — arc — 3 смены → недоплата: проглотить/потребовать/угроза/Виктор (N3).
- `zoll_raid` — reactive — 5+ чёрных смен → облава: бежать/прятаться/фальшивка/сдаться (N6).
- `wage_in_cash_temptation` — dilemma — линия «Заработок»/«Студент» → смена сверх лимита/вчёрную: деньги vs риск.
- `laptop_sale_or_keep` — dilemma — линия «Соискатель», деньги<300 → продать ноут (потеря актива) vs держать.
- `remittance_pressure` — pressure — линия «Заработок» → семья просит перевод, давление не снять.
- `injury_no_insurance` — pressure — Труд высок, чёрная стройка → травма без страховки: катастрофа расходов.

**Жильё (arc, pressure)**
- `hostel_runs_out` — pressure — день 5 → матрас у знакомых (200/мес) / объявления (все хотят Anmeldung) / ещё ночь 35€.
- `room_sublet_no_anmeldung` — community — репутация общины → комната без формальностей (серый комфорт).
- `overcrowded_flat_conflict` — ambient/pressure — линия «Заработок» → 8 человек в двушке, бытовой конфликт.
- `landlord_schufa_wall` — pressure — попытка снять «по-белому» → стена Schufa/WBS/Anmeldung.

**Улица / контур (reactive, dilemma)**
- ★`ubahn_control` — pressure/reactive (выше) (часть N-логики).
- `wallet_on_pavement` — dilemma — случайное, день 3+ → 80€+студ.айди: присвоить/вернуть(→полезный контакт)/в полицию(а ты сам без Anmeldung).
- `criminal_contact_finds_you` — arc — LAW<−30 & Улица>25 → контур сам предлагает дело.
- `park_night_offer` — dilemma — Хазенхайде ночью → серый/наркозаработок: вход в подполье.
- `racial_profiling_stop` — reactive — линия «Невидимка»/«Беженец», «опасное место» → проверка по цвету кожи (тон: без чернухи, см. `08`).
- `pickpocketed` — reactive — невнимателен в толпе/ночью → у игрока крадут (мир «бьёт в ответ»).

**Социальное / отношения (community, arc)**
- `frau_schmidt_bags` — dilemma — день 4, у подъезда → помочь без обещания награды (тест ALTRU; ветка фрау Шмидт).
- ★`emilia_asks_directly` — arc — 3+ встречи → «чем ты тут занимаешься?»: правда/ложь/уход (N5, питает ④).
- ★`scheinehe_offer` — dilemma — акт II, деньги~0 & L−склонность → фиктивный брак (N7).
- `comm_dinner` — community (выше) → ужин, открывает субаренду.
- `church_service` — community — линия «Невидимка» → пятидесятническая церковь: безусловная поддержка, контр-Виктор.
- `victor_pulls_you_in` — arc — ходишь к Виктору → знакомство с контуром/«Доктором» (N4-серый).
- `lena_legal_path` — arc — ходишь к Лене → честная лазейка/консультация (N4-белый).
- `newcomer_mirror` — dilemma — ~день 60 → ты в роли Виктора для новичка (N8, красит эпилог).

**Тело / психика (pressure, ambient)**
- `hunger_spell` — pressure — голод высок → штраф к навыкам, риск «съесть» гордость (попросить/украсть еду).
- `news_from_front` — pressure — линия «Война» → новость с фронта: психо-удар, нужен relief.
- `call_home` — ambient/arc — линия «Война»/«Заработок» → звонок домой: ресурс и рана разом.
- `language_breakthrough` — arc — Deutsch пробивает 50 → relief-веха: открывается «немецкий Берлин».
- `exhaustion_collapse` — pressure — усталость+стресс на пике → событие-срыв, вынужденный простой.

**Выдохи / relief (ambient — для режиссёра)**
- `hasenheide_day` — ambient — день-выдох → бег/шахматисты/случайная тёплая встреча.
- `kind_stranger` — ambient — высокий tension → чужой делает маленькую доброту бесплатно.
- `small_win` — ambient — после серии провалов → мелкая удача (нашёл смену, угостили кофе).

## 5.7. Заметки для реализации

- Хранить события в **БД/файлах как данные** (одна запись = одна YAML/JSON-карточка). Движок их не «знает» поимённо — только применяет схему. Это позволяет LLM/дизайнеру лить контент без правки кода.
- **Резолвер** = чистая функция `(event, matched_branch, player_state, rng_seed) → outcome, effects, delta_hints, rumor/notes, followups`. Детерминирован при фиксированном сиде (v0.1 §4.2.5).
- **Валидатор контента** при загрузке: каждая ветка ссылается на существующие интенты/навыки/локации/фракции; у события достижимы `entry_conditions`; нет «сиротских» `followups`.
- Узлы N1–N9 пометить `once: true` и высоким `priority`; их флаги-исходы — входные условия концовок (`04`).
- Начать с **MVP-пула ~30 событий** (как в v0.1 §4.3.1) вокруг одной линии («Соискатель»), затем размечать перекраски тегами под другие бэкграунды.
- Локации, на которые ссылаются `entry_conditions.location_in`, — из `06` (единый реестр id локаций).
