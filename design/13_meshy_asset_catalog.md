# 13. КАТАЛОГ 3D-МОДЕЛЕЙ для Meshy (Gemini → image-to-3D), бюджет ~1000 кредитов

> Пайплайн: **(1)** берёшь промпт ниже → генеришь картинку в **Gemini** (генерация изображений) →
> **(2)** грузишь картинку в **Meshy → Image to 3D** → **(3)** для людей делаешь **Rig** по единому
> рецепту (раздел 6), чтобы анимации не «плыли». Промпты — на английском (image-модели так дают
> чище), пояснения — по-русски.

---

## 0. Как собрать финальный промпт

Финальный промпт для Gemini = **SUBJECT** (строка у каждой модели) **+ STYLE_BLOCK** (раздел 2)
**+ POSE_BLOCK** (раздел 3 — только для людей).

То есть: копируешь строку модели, дописываешь блок стиля, для персонажей ещё блок позы. Один объект
= одна картинка = одна модель в Meshy.

---

## 1. Бюджет кредитов

⚠️ **Допущение** (Meshy периодически меняет цены — сверь в своём тарифе и подставь свои числа):
- **Image to 3D** (геометрия + текстура): ~**10 кредитов** за генерацию.
- **Rig (авториг гуманоида)**: ~**10 кредитов** за персонажа.
- **Ретраи**: первая генерация часто кривая → закладываем в среднем **×1.5** на Image to 3D.

Формула на модель: `стоимость = image_to_3d × 1.5 (+ rig, если человек)`.

| Категория | Кол-во | Кредитов/шт (с ретраями) | Итого |
|---|---|---|---|
| Гуманоиды (image-to-3D ×1.5 + rig) | 16 | ~25 | **400** |
| Окружение/пропсы (image-to-3D ×1.4) | 30 | ~14 | **420** |
| **Подытог** | 46 | | **~820** |
| Буфер на ретраи/варианты | | | **~180** |
| **ВСЕГО** | | | **~1000** |

**Главный вывод:** 16 персонажей + 30 объектов окружения комфортно влезают в 1000 с запасом на
переделки. Если твоя цена за Image to 3D ниже (бывает 5 кр.) — останется на варианты/ретекстуры.

**Как растянуть кредиты (важно!):**
- **Перекрашивай в движке, а не в Meshy.** Generic-прохожего (H13/H14) и рабочего (H16) генери ОДИН раз, а толпу делай сменой цвета материала в Three.js — это бесплатно. Не трать кредиты на «ретекстур».
- **Переиспользуй модульное.** Один Altbau/Plattenbau/контейнер можно ставить много раз, масштабировать, разворачивать — это бесплатно.
- **Не ригуй то, что не двигается.** Рига — только гуманоидам. Здания/пропсы — статичные меши.
- Пропсы с тегом *(опц.)* делай в последнюю очередь — если останутся кредиты.

---

## 2. STYLE_BLOCK — вставляй в КАЖДЫЙ промпт

```
Stylized low-poly 3D game asset, clean flat-shaded render, simple geometric forms,
appealing muted color palette, soft even studio lighting, no harsh shadows.
Single subject only, centered, fully in frame (not cropped), isolated on a plain
light-grey background (#d9d9d9). No other objects, no scenery, no people in the
background, no text, no logos, no watermark. Clean sharp silhouette, high clarity,
optimized for image-to-3D conversion.
```
Для пропсов/зданий добавляй в конец: `3/4 front view, slight top-down angle.`

---

## 3. POSE_BLOCK — вставляй ТОЛЬКО в промпты людей (после STYLE_BLOCK)

> Это ключ к одинаковому риггингу: одинаковая поза + одинаковые пропорции у всех → авториг ставит
> одинаковый скелет → анимации переносятся на всех и никто не «плывёт».

```
Full body visible head to feet, standing in a neutral A-pose: arms straight and
angled about 30 degrees away from the torso, hands open and empty, legs
shoulder-width apart, perfectly symmetrical, straight-on front view, facing the
camera directly, neutral facial expression, looking forward. Consistent stylized
human proportions, about 7 heads tall, the SAME body scale as every other character
in this set. Arms and legs fully separated from the torso (no merged limbs). No held
items, no bag, no objects fused to the body; a hat, cap or headscarf on the head is
fine. Plain shoes. This is a character base mesh in T/A-pose for auto-rigging.
```

**Правила, чтобы риг не сломался:**
- Никаких предметов в руках и сумок на теле → сумку/ноут/чемодан генерь отдельными пропсами (E32–E34).
- Все смотрят строго в камеру, симметрично, во весь рост, ноги видны.
- Одинаковый рост/пропорции (≈7 голов) у всех — иначе скелеты разъедутся.

---

## 4. ПЕРСОНАЖИ-ГУМАНОИДЫ (16) — SUBJECT + STYLE + POSE

| # | Кто | SUBJECT (англ., вставь + STYLE_BLOCK + POSE_BLOCK) |
|---|---|---|
| H01 | Протагонист | `A 28-year-old immigrant software developer, average build, short dark hair, light stubble, wearing a plain dark-grey zip hoodie, dark jeans and white sneakers, tired but determined expression.` |
| H02 | Виктор (серб) | `A 35-year-old Serbian man, stocky build, short cropped hair, three-day stubble, a warm sly half-smile, wearing a worn brown leather jacket over a grey t-shirt, dark jeans and scuffed boots.` |
| H03 | Мехмет (кебаб) | `A 50-year-old Turkish kebab-shop owner, sturdy build, greying short hair and moustache, wearing a white short-sleeve shirt and a dark-red apron, kind tired eyes.` |
| H04 | Фрау Шмидт | `A 78-year-old German woman, slim and slightly stooped, neat short white hair, wearing a beige buttoned cardigan over a pale-blue blouse, a long grey skirt and flat shoes, dignified reserved expression.` |
| H05 | Богдан (бригадир) | `A 45-year-old Eastern-European construction foreman, broad muscular build, buzz cut, weathered face, wearing an orange hi-vis vest over a grey long-sleeve shirt, dark work trousers, heavy boots and a yellow hard hat.` |
| H06 | Фрау Беккер (чиновница) | `A 50-year-old German civil-servant woman, average build, greyish-blonde hair tied back, reading glasses, wearing a muted teal blouse and dark trousers, tired neutral expression.` |
| H07 | Лена (волонтёрка) | `A 27-year-old German volunteer woman, slim, shoulder-length brown hair, friendly open face, wearing a mustard-yellow knit sweater, dark jeans and a lanyard badge.` |
| H08 | Али (фиксер) | `A 30-year-old Lebanese-German man, lean, short dark hair, neat beard, calm guarded expression, wearing a plain black zip hoodie and dark trousers.` |
| H09 | Карим (шпэти) | `A 45-year-old Arab corner-shop owner, average build, short dark hair, stubble, wearing a checked flannel shirt with rolled-up sleeves and dark trousers, gruff but warm expression.` |
| H10 | Эмилия (бариста) | `A 25-year-old German barista woman, slim, dark hair in a low bun under a grey beanie, small nose ring, wearing a denim apron over a striped long-sleeve shirt and black jeans, warm curious smile.` |
| H11 | Абу Юсуф (старейшина) | `A 60-year-old Syrian community elder and baker, slim, full grey beard, wearing a long beige traditional thobe and a knitted skullcap, calm dignified expression.` |
| H12 | Самира (консультантка) | `A 35-year-old Syrian woman, average build, wearing a deep-burgundy hijab and a neat dark-grey blazer over a long tunic, sharp intelligent expression.` |
| H13 | Прохожий М (база толпы) | `A generic 30-year-old Berliner pedestrian man, average build, short brown hair, plain neutral expression, wearing a plain mid-grey jacket, dark trousers and sneakers; neutral base model for color variations.` |
| H14 | Прохожая Ж (база толпы) | `A generic 30-year-old Berliner pedestrian woman, average build, shoulder-length brown hair, plain neutral expression, wearing a plain olive coat, dark trousers and flat shoes; neutral base model for color variations.` |
| H15 | Контролёр/полицейский | `A 40-year-old German transit ticket inspector, average build, short hair, stern neutral face, wearing a dark-navy uniform jacket with subtle plain insignia and dark trousers.` |
| H16 | Рабочий (база) | `A generic 35-year-old construction worker, average build, wearing an orange hi-vis jacket, grey trousers, work boots and a white hard hat, neutral expression; neutral base model for crowd reuse.` |

> Кого нет в списке (Доктор, Надя, Валид, Януш, пастор, тётушка Хоа, Оксана и т.д.) — собирай
> перекраской/мелкой правкой generic-прохожих (H13/H14) уже в движке, **без новых кредитов**.

---

## 5. ОКРУЖЕНИЕ И ПРОПСЫ (30) — SUBJECT + STYLE (+ `3/4 front view`)

### Здания (модульные, переиспользуемые)
| # | Объект | SUBJECT |
|---|---|---|
| E01 | Altbau (угловой дом) | `A low-poly 5-storey Berlin Altbau corner apartment building, simplified ornate facade, cream plaster, tall windows, a small ground-floor shop front.` |
| E02 | Plattenbau (панелька) | `A low-poly East-Berlin Plattenbau prefab apartment block, repetitive grid of windows and balconies, pale concrete-grey with faded pastel accents.` |
| E03 | Шпэти (киоск) | `A low-poly Berlin Späti corner kiosk storefront, small shop with a counter window, fridge inside, simple awning, abstract colorful drink ads.` |
| E04 | Кебабная (фасад) | `A low-poly Berlin döner kebab shop storefront, glass front, red-and-white awning, simple counter, warm interior glow.` |
| E05 | Вход в U-Bahn | `A low-poly Berlin U-Bahn subway entrance: a staircase going down with metal railings and a simple blue U sign on a pole.` |
| E06 | Вагон U-Bahn | `A single low-poly Berlin U-Bahn subway car, classic yellow BVG livery with grey doors and windows, clean stylized.` |
| E07 | Рыночный прилавок | `A low-poly street market stall with a striped canopy and crates of colorful vegetables and fruit, simplified shapes.` |
| E08 | Мечеть/центр | `A low-poly modest community mosque with a small dome and one slim minaret, sand-colored walls, simple and clean.` |
| E09 | Церковь в магазине | `A low-poly converted-storefront Pentecostal church: a plain shop building with a simple white cross above the door and a small banner.` |
| E10 | Heim-контейнер | `A low-poly white housing container unit (refugee shelter) with a door and two small windows, modular box.` |
| E11 | Dong Xuan (рынок-ангар) | `A low-poly large warehouse market hall, corrugated metal exterior, big roller doors, simple stylized.` |

### Стройка
| # | Объект | SUBJECT |
|---|---|---|
| E12 | Леса | `A low-poly construction scaffolding structure, metal poles and planks against a partially covered building, clean stylized.` |
| E13 | Бетономешалка | `A low-poly cement mixer machine, an orange drum on a wheeled frame, simple shapes.` |
| E14 | Бытовка | `A low-poly construction site portacabin office, a beige rectangular container with a door, two windows and small steps.` |

### Интерьерные пропсы
| # | Объект | SUBJECT |
|---|---|---|
| E15 | Стойка Bürgeramt | `A low-poly government office service counter with a glass divider, a small number-ticket display and an office chair, institutional grey.` |
| E16 | Ряд стульев (ожидание) | `A low-poly row of four connected plastic waiting-room chairs on a metal frame, muted blue seats.` |
| E17 | Стойка кафе | `A low-poly café counter with an espresso machine, a pastry display and two stools, warm wood and matte black.` |
| E18 | Столик кафе | `A low-poly small round café table with two simple wooden chairs.` |
| E19 | Барная стойка | `A low-poly cozy Berlin bar counter with bottles on a back shelf, beer taps and two bar stools, warm dim style.` |
| E20 | Двухъярусная кровать | `A low-poly metal hostel bunk bed, two tiers with simple mattresses and a small ladder.` |
| E21 | Кухонный блок | `A low-poly small apartment kitchenette: counter, sink, two upper cabinets and a small stove, pale and worn.` |
| E22 | Диван | `A low-poly worn two-seat fabric sofa, muted brown-green, simple cushions.` |
| E23 | Дёнер-гриль | `A low-poly vertical döner kebab rotisserie grill, a stacked meat cone on a metal stand, simple.` |

### Уличные пропсы (мелкие, переиспользуемые)
| # | Объект | SUBJECT |
|---|---|---|
| E24 | Урны (оранжевые BSR) | `A low-poly pair of city waste bins: one bright-orange round bin on a pole and one larger lidded bin, simple.` |
| E25 | Скамейка | `A low-poly wooden park bench with metal armrests.` |
| E26 | Дерево | `A single low-poly deciduous tree with a stylized rounded green canopy and a brown trunk.` |
| E27 | Фонарь | `A low-poly Berlin street lamp post, a tall slim dark-metal pole with one arm and a lamp head.` |
| E28 | Велосипед | `A low-poly city bicycle on its kickstand, simple frame, muted color.` |
| E29 | Светофор (Ampelmännchen) | `A low-poly pedestrian traffic-light pole showing the Berlin Ampelmännchen walk and stop figures, dark pole.` |
| E30 | Машина (припаркована) | `A low-poly compact European hatchback car, muted grey, simple clean shapes.` |

### Пропсы-предметы взаимодействия *(опц., если остались кредиты)*
| # | Объект | SUBJECT |
|---|---|---|
| E31 | Ноутбук | `A low-poly open laptop computer, slim dark-grey, simple.` |
| E32 | Чемодан | `A low-poly hard-shell rolling suitcase, muted color, handle up.` |
| E33 | Рюкзак | `A low-poly everyday backpack, muted color, simple.` |
| E34 | Кофейный стакан / дёнер | `A low-poly takeaway coffee cup and a wrapped döner, two tiny simple food props.` |

---

## 6. РИГГИНГ В MESHY: чтобы никто не «поплыл»

Причина «поплыли» — у каждого персонажа авториг ставит чуть разный скелет, и анимации с одного не
ложатся на другого. Лечится **единообразием на входе** + **единым скелетом**.

**Правила на этапе генерации (раздел 3 их уже задаёт):**
1. Все люди — в одинаковой **A-позе**, строго фронт, симметрично, во весь рост.
2. Одинаковые **пропорции и рост** (≈7 голов), одинаковый масштаб.
3. Никаких предметов в руках/на теле (только головной убор) — иначе риг цепляет лишнее.

**В Meshy (Rig & Animate):**
1. Сделал Image to 3D → проверил, что меш стоит ровно, лицом вперёд, во весь рост.
2. Открой **Rig** (авториг для гуманоидов) → Meshy сам ставит гуманоидный скелет → проверь точки суставов (плечи/локти/колени на месте) → Apply.
3. **Сначала отригуй ОДНОГО** «эталонного» персонажа (например H13 generic), убедись, что анимация играет чисто. Остальных ригуй **той же кнопкой/настройкой** — раз поза и пропорции одинаковы, скелет получится тот же.
4. Экспортируй **GLB с ригом**. Бери **один стандарт скелета на всех** (гуманоид Meshy / Mixamo-совместимый) — не меняй набор и имена костей между персонажами.

**Чтобы точно не разъехались (нормализация перед использованием):**
- Один up-axis (Y-up), один масштаб, одно направление «лица» (все смотрят в одну сторону, напр. +Z). Если кто-то задом наперёд — развернёшь до рига.
- Приведи всех к одному росту (напр. 1.8 юнита) — это и риг стабилизирует, и в сцене смотрится ровно.

**В Three.js (движок):**
- Скелеты одинаковые → **анимационные клипы общие**: одну анимацию (`idle/walk/punch/hit/fall`) проигрываешь на любом персонаже через `AnimationMixer`. Это и есть защита от «поплыли».
- Если берёшь анимации с Mixamo — держи Mixamo-совместимые имена костей у всех (Meshy-риг это обычно умеет; проверь на эталоне).

---

## 7. Чек-лист красоты (чтобы не «убожество»)

- В STYLE_BLOCK уже зашиты: чистый flat-shaded вид, приятная приглушённая палитра, мягкий ровный свет, один объект на сером фоне без мусора — это даёт Meshy самый чистый вход.
- Если выходит «грязно»: перегенери картинку (вариативность Gemini), выбери самый **читаемый силуэт** и **симметричную** позу — Meshy любит чёткие силуэты.
- Не пихай мелкую детализацию/текст/узоры — low-poly их всё равно потеряет, а image-to-3D запутается.
- Держи **единый art-style** во всех промптах (один STYLE_BLOCK) — тогда персонажи и окружение будут смотреться как один сет.

**Итого:** 16 персонажей (единый риг) + 30 объектов окружения ≈ **820 кредитов + буфер ≈ 1000**.
