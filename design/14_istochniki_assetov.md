# 14. ИСТОЧНИКИ АССЕТОВ ИЗ СЕТИ + ИНВЕНТАРЬ АНИМАЦИЙ

> Закупочная карта для ОБЕИХ игр (BERLIN: ÜBERLEBEN и «Полночь в Колокольце»): проверенные
> ссылки на паки окружения/объектов и сверка скачанной библиотеки Mixamo с реестрами
> `scenario3d/06` (A##) и `../kolokolets/05` (K##) — что уже есть, что докачать.
> Персонажи-гуманоиды НЕ здесь: они закрыты батчем Meshy (9 GLB готовы).

---

## 0. Правила закупки (читать до скачивания)

1. **Лицензии.** CC0 — бери и пользуйся (Kenney, Quaternius, KayKit, часть Poly Pizza).
   CC-BY — можно в коммерцию, но **автор указывается**: заведи `CREDITS.md` и вписывай сразу
   при скачивании. **CC-BY-NC (NonCommercial) — НЕ БРАТЬ** вообще: на Sketchfab проверяй
   плашку лицензии у каждой модели перед кнопкой Download.
2. **Стили не мешать** (закон из `06`/`07`): на игру — один пак-костяк + точечные догрузки,
   перекрашенные под него. Берлин = Kenney City-серия; Колоколец = Kenney Fantasy Town Kit.
3. **Единая палитра дёшево:** все догруженные меши пересаживаются на один градиент-атлас
   (256×256 палитра-текстура, UV точками) — 20 минут в Blender на пак, и разнобой исчезает.
4. **Масштаб:** нормализация к нашим людям (рост 1.8u) — тем же батч-скриптом, что уже
   написан для GLB (`normalize-glb-batch.py` — он в твоей папке Mixamo/glb, расширить на пропсы).

---

## 1. Базовые библиотеки (костяк, всё бесплатно)

| Источник | Лицензия | Что берём | Ссылка |
|---|---|---|---|
| **Kenney — City Kit (Commercial)** | CC0 | 50 моделей: магазины-фасады, городские здания → улицы Берлина | kenney.nl/assets/city-kit-commercial |
| **Kenney — City Kit (Suburban)** | CC0 | 40 моделей: жилые дома → фоновые кварталы | kenney.nl/assets/city-kit-suburban |
| **Kenney — City Kit (Roads)** | CC0 | дороги/перекрёстки/тротуары (та же серия) | kenney.nl/assets (серия City Kit) |
| **Kenney — Fantasy Town Kit** | CC0 | **160 моделей уютного городка → ВЕСЬ Колоколец**: дома, черепица, рынки, колодец | kenney.nl/assets/fantasy-town-kit |
| **Kenney — Furniture Kit** | CC0 | 140 моделей мебели → все интерьеры обеих игр | kenney.nl/assets/furniture-kit |
| **Kenney — Food Kit** | CC0 | 200 моделей еды → кебабная, кафе, пекарня, ужин общины | kenney.nl/assets/food-kit |
| **Kenney — Nature Kit** | CC0 | 330 моделей: деревья, кусты, камни → Хазенхайде, холмы Колокольца | kenney.nl/assets/nature-kit |
| **KayKit — City Builder Bits** | CC0 | 32+ городских «кирпичика» → добивка берлинских улиц | kaylousberg.itch.io/city-builder-bits |
| **KayKit — Restaurant Bits** | CC0 | **140+ кухня/еда/стойки** → кебабная Мехмета, кафе Эмилии/Бруно, пекарня Греты | kaylousberg.itch.io/restaurant-bits (зеркало: github.com/KayKit-Game-Assets) |
| **KayKit — Furniture Bits** | CC0 | 50+ интерьерных мелочей | kaylousberg.itch.io/furniture-bits |
| **KayKit — Medieval Builder Pack** (legacy) | CC0 | сельско-средневековые дома → альтернативный стиль Колокольца | kaylousberg.itch.io/kaykit-medieval-builder-pack |
| **Quaternius** (весь сайт) | CC0 | 150+ природа, farm buildings, мебель, машины | quaternius.com |
| **Poly Pizza** (агрегатор CC0/CC-BY) | смотри у модели | точечный поиск чего угодно без логина | poly.pizza |
| *Платная опция:* **Synty POLYGON** | платно | City $19.99 · Town · Construction · Shops — если захочется «плотного» Берлина одним стилем | syntystore.com/products/polygon-city-pack |

> Synty — НЕ обязателен: таблицы ниже закрывают обе игры бесплатными паками. Это апгрейд
> «когда-нибудь потом», причём тогда придётся пересобрать стиль целиком (правило §0.2).

---

## 2. БЕРЛИН — закупка по сборкам (`scenario3d/01` §Локации)

| Сборка (E## каталога) | Чем закрываем из сети | Что остаётся Meshy/декалям |
|---|---|---|
| Улица: дома E01/E02 | City Kit Commercial + Suburban (фасады, углы) + City Builder Bits | граффити/вывески-декали (Späti, Döner, Apotheke) — сами |
| **U-Bahn: E05 вход + E06 вагон** | **ГОТОВОЕ: «Lowpoly Berlin U-Bahn» + «Lowpoly Berlin U-Bahn Station» (n-malmberg, Sketchfab, free)** — редкая удача, именно BVG-стилистика | валидатор-примитив; проверить лицензию при скачивании, вписать в CREDITS |
| Шпэти E03 | фасад из City Kit Commercial + холодильник/стеллажи из Furniture Kit | доска объявлений — декаль |
| Кебабная E04 + гриль E23 | фасад City Kit; интерьер Restaurant Bits (стойки, витрины, плиты); шаурма-конус: Sketchfab «Kebab (CC0)» (Olst) / «Kebab Cart LOWPOLY» (CC-BY) | вертикальный гриль, если каталожный вид важен → Meshy E23 |
| **Стройка E12–E14** | **itch.io «Low Poly Construction Pack» (LowPolyAssets, 80 моделей: леса, бетономешалка, кран, ограждения, каски — закрывает ВСЁ)** + запасной: «Construction Site Asset Pack» (vmatthew, Sketchfab) + «3D House Construction Site» (Majadroid, CC0) | ничего |
| Bürgeramt/LEA E15/E16 | Furniture Kit (стойки, стулья рядами, столы) + KayKit Furniture Bits | табло-декаль |
| Кафе E17/E18, бар E19 | Restaurant Bits (эспрессо-станция, стойки) + Furniture Kit | неон-декали бара |
| Хостел E20–E22 | **Bunk Bed от Quaternius — прямая ссылка poly.pizza/m/XpysaEDXJQ** + Furniture Kit (диван, кухня) | — |
| Рынок E07 | Fantasy Town Kit (прилавки! они стилистически нейтральны) + Food Kit (товар) | арабские вывески-декали |
| Уличные пропсы E24–E30 | City Kit Roads (фонари, урны, скамейки) + Nature Kit (деревья) + Quaternius Cars (хэтчбек) + City Builder Bits (велосипед есть в городских паках; запасной поиск: poly.pizza/search/bicycle) | **Ampelmännchen — только декаль/Meshy** (в сети такого нет) |
| Мелкие пропсы E31–E34 | Food Kit (кофе-стакан, еда) + Furniture Kit (ноутбук обычно есть; запасной: poly.pizza/search/laptop) + poly.pizza/search/suitcase | — |

**Вывод по Берлину:** весь реестр E01–E34 закрывается бесплатно, кроме трёх «фирменных»
вещей, где решает узнаваемость: Ampelmännchen (декаль), дёнер-гриль (Meshy, если Sketchfab-
варианты не понравятся), Späti-вывеска (декаль). Кредиты Meshy почти не нужны на окружение.

---

## 3. КОЛОКОЛЕЦ — закупка (`../kolokolets/05`)

| Нужно | Чем закрываем | Заметка |
|---|---|---|
| Городок целиком (дома, площадь, колодец, рынок) | **Kenney Fantasy Town Kit (160 моделей) — ядро стиля** | это буквально «Колоколец в коробке» |
| Часовая башня | башня из Fantasy Town Kit + надстройка-звонница | циферблат БЕЗ стрелок — декаль (стрелки появляются в финале) |
| **Механизм часов (финальный кадр!)** | Sketchfab: **«Clockwork» (tamminen, free, шестерни с loop-анимацией!)** + **«CC0 Gear» (plaggy)** — размножить инстансами | маятник-«сердце» — примитив с эмиссивом (задумано так) |
| **Колокол** | Sketchfab «Classic Bell 3D Model» (free) + тег bell-tower | проверить лицензию, CREDITS |
| Пекарня Греты, кафе Бруно | Restaurant Bits (140+ кухня/выпечка) + Food Kit (пироги!) | печь есть в Restaurant Bits |
| Мастерская Мии | Resource Bits + Prototype Bits (KayKit) + Furniture Kit (верстаки) | «самоварная ракета» — примитивы |
| Телескоп Мельхиора | poly.pizza/search/telescope (несколько CC0) | беседка — из Fantasy Town Kit |
| Фонарики (финал, сотни) | poly.pizza/search/lantern + инстансинг | эмиссив + нитка-сплайн |
| Почта Веры, велосипед | Fantasy Town Kit (тележки) + poly.pizza/search/bicycle | конверты — примитивы (задумано) |
| Природа холмов | Nature Kit (330) | — |

**Вывод по Колокольцу:** 100% бесплатно; второй батч Meshy из wishlist (`../kolokolets/05` §4)
нужен только если захочется уникальную башню-хиро. Финальный кадр механизма уже закрыт
готовым анимированным «Clockwork».

---

## 4. АНИМАЦИИ: инвентарь скачанного ↔ реестры A##/K##

### 4.1. Уже скачано и закрывает реестр (маппинг файлов из твоей папки Mixamo)

| Твой файл | Реестр | Куда идёт |
|---|---|---|
| Walking / Running / Walking Left Turn | A02 / A04 (+повороты) | локомоция |
| Walk W_ Briefcase | **A05-чемодан** | S01–S03, финал ④ (лучше, чем задумано!) |
| Standing Idle / Happy Idle / Sad Idle / Bored / Look Around / Yawn | A01 / A31 / A08 | идлы всех |
| Old Man Idle | A01-вариант | **Мельхиор/Абу Юсуф — персональный идл** |
| Sitting Idle / Stand To Sit / Sit To Stand / Getting Up | A11 / A13 / A14 / A52 | сидение |
| Laying Sleeping | A60 | сон |
| Standing Greeting / Waving / Quick Formal Bow | A16 | приветствия (+поклон Беккер!) |
| Shaking Hands 2 | A17 | сделки, знакомства |
| Head Nod Yes / Agreeing / Acknowledging | A18 | «да» |
| Shaking Head No / Annoyed Head Shake / Dismissing Gesture | A19 (+Богданово «иди отсюда») | «нет» |
| Shrugging | A20 | «ну-ну» |
| Talking At Watercooler / Standing Arguing / Yelling While Standing | A21 / A22 / A28 | разговор→спор→крик |
| Talking On Phone / Texting While Standing | A26 / A09 | телефон |
| Standing Using Touchscreen Tablet | A09-планшет | **мэр Амина** |
| Pointing Forward | A23 | указания |
| Taking Item / Picking Up Object | A24-взять / A35 | предметы (give — реверс/процедурно, как задумано) |
| Thinking / Surprised / Disappointed / Relieved Sigh / Thankful / Pouting / Bashful | A32 / A27 / A33 + детские эмоции Колокольца | эмо-палитра готова с запасом |
| Laughing / Sitting Laughing / Sitting Disbelief | A30 / A62-вариант | смех; «осел от новости» |
| Telling A Secret | — (бонус) | **лайфхак Беккер «я вам этого не говорила» — сцена BR!** |
| Nervously Look Around | A08-нерв | **стрём у машины Виктора (VD), укрытие на облаве** |
| Searching Pockets | — (бонус) | карманник S12; «где номерок?!» в Bürgeramt |
| Searching Files High / Using A Fax Machine | — (бонус) | **амбиент клерков Bürgeramt/LEA — зал оживает** |
| Leaning | — (бонус) | **Виктор у стены — его фирменная поза** |
| Cross Punch / Hit Reaction | A49 / A50 | конфликт N3 |
| Push | A42 | стройка/толчок |
| Digging | A41 | стройка-петля |
| Bartending | A45! | **налить-подать: бар, çay, кофе Эмилии — закрыт красиво** |
| Drinking | A57 | пиво/чай/кофе |
| Typing / Writing | A46 / A47 | отклики, подписи, протоколы |
| Opening / Closing | — (бонус) | двери/ставни/сундук Греты |
| Samba Dancing | A61 | эмерджентное «танцую» |
| Throw | K01 | мяч Тео |
| Clapping / Cheering While Sitting | K03 / K04-сидя | аплодисменты, полночь |
| Standing To Crouched | A53 | спрятаться (облава, прятки) |
| Male Standing Pose | — | референс-поза для проверки ретаргета |

**Итог: из 55 клипов реестра закрыто ~44, плюс 8 бонусов, которые я вписал в сцены выше.**
Библиотека уже больше минимума P0 — можно собирать Акт I хоть сейчас.

### 4.2. ДОКАЧАТЬ с Mixamo (по приоритету; имя = что вводить в поиск)

| Приоритет | Поиск в Mixamo | Реестр | Зачем | Если не найдётся |
|---|---|---|---|---|
| **P0** | `Sad Walk` | A03 | усталая походка после смен — используется каждый вечер Акта I | Walking ×0.85 + голова вниз |
| **P0** | `Hugging` | A65 | финалы ① (Мехмет, Эмилия), полночь Колокольца | Handshake + шаг ближе (хуже) |
| **P0** | `Praying` | A34 | коридор LEA (N9), надежда | Thinking |
| **P0** | `Carrying` (heavy box/object) | A05-мешок | стройка, reveal Эмилии (мешок на плече — ключевой кадр) | Walk W_ Briefcase не подходит для мешка; процедурный наклон |
| **P1** | `Sneaking` / `Sneak Walk` | A06 | прятки на облаве, тихие проходы | Standing To Crouched + медленный Walking |
| **P1** | `Excited` / `Fist Pump` | A29-стоя | слот в 7 утра, контракт подписан | Happy Hand Gesture (есть) |
| **P1** | `Falling` / `Knocked Down` | A51 | драка N3 | **ragdoll движка (уже реализован) — можно вообще не качать** |
| **P1** | `Climbing Ladder` | K08 | стремянка Тео, подъём в механизм | кат-склейка кадром |
| **P2** | `Eating` | A58 | дёнер-обед, застолья | Drinking с другим пропом |
| **P2** | `Knocking` (door) | A64 | дверь Шмидт, дома Колокольца | Cross Punch мягко у двери |
| **P2** | `Surrender` / `Hands Up` | A54 | облава-«сдаться» | Waving двумя руками замедленно |
| **P2** | `Sweeping` (⚠️ может вернуть подсечку из бокса — смотри превью) | A39/K12 | уборка, фоны недели | процедурная метла |
| **P2** | `Sitting Talking` | A12 | диалоги за столом | Sitting Idle + верхняя маска Talking |
| **P2** | `Catching` | K02 | мяч Тео (ловить) | Picking Up Object на уровне груди |

**Настройки при докачке** (как для всей библиотеки): FBX Binary, Without Skin, 30 fps,
для локомоций — галка **In Place**. ⚠️ Проверь уже скачанные Walking/Running: если они
уезжают из точки — перекачай с In Place, иначе персонаж будет «скользить» под контроллером.

### 4.3. Пайплайн (у тебя уже почти всё автоматизировано)

1. FBX → GLB + нормализация: твой `normalize-glb-batch.py` (в папке glb) — добавить в него
   пропсы и проверку Y-up/масштаба.
2. Ретаргет-эталон: `Idle berliner man`; контроль — `idle on elderly` (самая нестандартная
   фигура). Один раз проверил пару клипов — дальше вся библиотека ложится на всех.
3. Манифест `anim_id → файл` (словарь из `scenario3d/06` §2 и `kolokolets/05` §2) — чтобы
   движок и LLM-режиссёр ссылались на id, а не на имена файлов с пробелами и «(1)».

---

## 5. Порядок закупки (один вечер)

1. Kenney: Fantasy Town + City Commercial/Suburban/Roads + Furniture + Food + Nature (6 zip).
2. KayKit: Restaurant Bits + City Builder Bits + Furniture Bits (+ Medieval по вкусу).
3. itch.io: Low Poly Construction Pack.
4. Sketchfab (проверяя лицензию, заполняя CREDITS.md): Berlin U-Bahn + Station, Kebab (CC0),
   Clockwork, CC0 Gear, Classic Bell.
5. Poly Pizza: bunk bed (ссылка выше), telescope, lantern, suitcase, laptop, bicycle.
6. Mixamo: список §4.2 (P0 — 4 клипа, P1 — 4, P2 — по остатку терпения).
7. Всё через нормализатор → градиент-атлас → в движок.
