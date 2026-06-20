# Схема контента прототипа (для авторов событий и LLM-генераторов)

Контент — данные (YAML). Движок не знает события поимённо, только применяет схему.
Эталоны: `events/soiskatel.yaml`, `events/soiskatel_act2.yaml`, `events/soiskatel_act3.yaml`.

## Линия выводится из имени файла
`events/<line>.yaml`, `events/<line>_act2.yaml`, `events/<line>_act3.yaml` → линия `<line>`.
Можно переопределить полем `line:` у события (`shared` = доступно всем линиям).
Линии: `soiskatel, bezhenec, vossoedinenie, student, voyna, zarabotok, nevidimka`.

## Объект события

```yaml
- id: unique_snake_id          # уникален во ВСЕХ файлах
  title: "Человекочитаемое имя"
  category: arc|pressure|reactive|dilemma|community|ambient
  act: 1|2|3
  node: N1..N9                  # опц., если это узел-«стрелка»
  priority: 0..100             # выше = раньше показывается
  once: true                   # опц., одноразовое (узлы/сюжет — обычно true)
  trigger: scheduled|chain|pool|reactive
  day: <int>                   # для scheduled — самый ранний день
  cooldown_days: <int>         # опц.
  weight: <float>              # для pool — вес сэмплинга
  entry: { all: [предикаты], any: [...], none: [...] }   # условия появления
  stakes: trivial|low|medium|high|extreme                # вес дельт для Analyst
  location: <loc_id>|any       # где может всплыть (или any)
  targets: [npc_id, ...]       # NPC в сцене (первый — «голос» для Narrator)
  facts: [ "факт 1", "факт 2" ]# что Narrator может упоминать (вне списка — нельзя)
  intro: "Реплика-завязка"     # опц.
  branches:
    - id: branch_id
      match: { verbs: [...], methods: [...], honesty: [...], tone: [...] }  # verbs ОБЯЗАТЕЛЕН
      requires: [предикаты]    # опц.: ветка доступна только при этих условиях
      skill_check: { skill: <name>, vs: <int>, plus: { other_skill: 0.5 } }  # опц.
      outcomes:
        - on: success|fail|always         # success/fail — если есть skill_check
          text: "Что произошло (Narrator опишет ровно это)."
          effects: { ... }                # см. ниже
          deltas: { G: +2, T: -3, A: 0, L: -1, P: +1 }   # подсказки осей (Analyst клампит)
          skill_xp: { deutsch: 4 }
          rumor: { tag: "...", faction: "...", intensity: 0.5 }
          followups: [event_id, ...]      # включить следующее событие
          leads_to: "куда это ведёт (для отладки)"
  fallback: { text: "Если интент не подошёл", reopen: true }
```

## Предикаты (entry / requires)
`day_gte, day_lte, visa_lte` (visa_days = главный таймер линии),
`flag, flag_not, any_flag:[...], all_flags:[...]`,
`money_lt, money_gte`, `location, location_in:[...]|<group>`,
`counter_gte:{name:n}`, `axis_gte:{G:n}`, `axis_lte:{}`, `skill_gte:{deutsch:n}`,
`leaning_gte:{crime:n}`, `faction_gte:{turkish:n}`, `rumor:"tag"`.

## Эффекты (outcome.effects)
`money:int`, `set_flags:[...]`, `unset_flags:[...]`, `inc:{counter:n}`,
`faction:{name:n}`, `leaning:{name:n}`, `rumor:{tag,faction,intensity}`,
`dossier:"заметка в общее дело чиновников"`, `stress:int`, `hunger:int`, `fatigue:int`,
`advance_day:true`.

## Закрытый словарь глаголов (verbs) — только эти 28
`observe, inspect_self, talk, persuade, deceive, threaten, bribe, beg, befriend,
ask_help, offer_help, flirt, apologize, refuse, trade, work, steal, borrow, give,
apply, submit_docs, book_appointment, inquire_status, move, attack, flee, hide,
search, rest`
honesty: `truthful|half_truth|lie|omission` · tone: `polite|neutral|aggressive|submissive|sarcastic|desperate|charming|cold`
методы — см. `verbs.yaml` (у каждого глагола свой набор).

## Локации (location / location_in) — только эти id
`airport_ber, street_neukoelln, ubahn_station, hostel_komet, refugee_heim, overcrowded_flat,
plattenbau_flat, altbau_flat, einliegerwohnung, buergeramt, auslaenderbehoerde, jobcenter,
bamf_office, mehmet_kebab, sonnenallee_market, baustelle, internet_cafe, spaeti_karim,
dong_xuan, russian_shop, arbeiterstrich, bar_sandmann, cafe_third_wave, hasenheide_park,
mosque_community, storefront_church`
группы: `state, ubahn, community_hub, housing`.

## NPC-карточка (`npcs/<line>.yaml`)
```yaml
npcs:
  npc_xxx:
    name: "Имя"
    faction: "arabic|turkish|slavic|...|clerks|volunteers|criminal|..."
    nationality: "..."
    axes_self: { G: 0, T: 0, A: 0, L: 0, P: 0 }
    languages: [ru, de, ar, tr, vi, uk, pl, en]
    register: "как говорит"
    tics: ["словечко1", "словечко2"]
    likes: [...]
    dislikes: [...]
```

## Узлы N1–N9 (роли «стрелок», содержание — своё на линию)
N1 первый контакт с системой · N2 первый заработок/выживание · N3 конфликт-проверка ·
N4 серый vs белый проводник · N5 отношения-зеркало · N6 облава/проверка ·
N7 быстрый серый шанс (брак/схема) · N8 зеркало-новичок · **N9 кульминация-резолв** (выбор концовки по связке).
N9 делай как в `soiskatel_act3.yaml: node_letter_lea` — ветки гейтятся `requires`, матчатся по порядку (первый подходящий = концовка), каждая ставит `set_flags: [ending_xxx, game_over]`.

## Концовки (флаги на N9)
`ending_legal` (легализация/защита) · `ending_gray` (серая стабильность) ·
`ending_underground` (подполье) · `ending_exit` (выход с достоинством) ·
`ending_deport` (депортация→новая глава). Плюс линий-специфичные при желании.

## Главный таймер линии (clock)
Число — `visa_days`, метка — `clock_label` (из `economy.yaml: lines.<line>`). В предикатах
используй `visa_lte`. Стартовые деньги/флаги/навыки линии — там же.

## ТОН (гард-рейлы, design/08) — обязательно
«Честно, но не чернуха»: на каждый мрак — деталь человечности. БЕЗ карикатур на национальности/
религии. Чиновники/полиция процедурны, не злодеи. Достоинство героя важнее жалости. Языки звучат
(вкрапления с переводом в скобках). Игрок волен быть кем угодно — мир отвечает последствиями, не моралью.

## Валидация (ОБЯЗАТЕЛЬНО прогнать перед сдачей)
```bash
cd prototype
python3 -c "from berlin.content_loader import Content; c=Content('content'); print('events:', len(c.events))"
python3 - <<'PY'
from berlin.content_loader import Content
c=Content('content')
for eid,ev in c.events.items():
    for br in ev.get('branches',[]):
        assert br.get('match',{}).get('verbs'), (eid, br.get('id'), 'no verbs')
        assert br.get('outcomes'), (eid, br.get('id'), 'no outcomes')
print('OK, валидно')
PY
```
И смоук-тест прохождения линии: `python3 play.py --line <line> --stub --debug` (несколько ходов).
