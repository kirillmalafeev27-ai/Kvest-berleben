# 06. ЛОКАЦИИ И 3D-АССЕТЫ

Принцип: каждая локация подобрана так, чтобы под неё **легко находилась готовая low-poly
3D-модель** (Sketchfab, Synty, Kenney, Unity Asset Store, Unreal Marketplace, Quaternius,
itch.io). Мы намеренно используем **обобщённые архетипы зданий/объектов**, а «берлинскость»
добиваем не уникальной геометрией, а **цветом, вывесками, реквизитом, освещением и текстом**
рассказчика. Это и дёшево по ассетам, и спасает производительность (см. `07`).

## 6.1. Где брать ассеты (и как искать)

| Источник | Чем хорош | Ключи поиска |
|---|---|---|
| **Synty Studios POLYGON** | целые стилизованные паки одного стиля — почти всё ниже закрыто | `POLYGON City`, `POLYGON Town`, `POLYGON Street Racer`, `POLYGON Apartment`, `POLYGON Office`, `POLYGON Construction` |
| **Kenney.nl** | бесплатно, CC0, кубично-чисто | `Kenney City Kit (Commercial/Roads/Suburban)`, `Kenney Furniture Kit`, `Kenney Mini Market` |
| **Quaternius** | бесплатно, low-poly, модульно | `Quaternius Modular Buildings`, `Quaternius Ultimate Furniture` |
| **Sketchfab** | штучные модели, фильтр Downloadable + low-poly | см. ключи у каждой локации ниже |
| **Unity/Unreal маркеты** | модульные city-киты, метро, стройка | `low poly modular city`, `low poly subway`, `low poly construction site` |

**Базовый принцип закупки:** взять **один-два связных пака одного стиля** (рекомендуется Synty
POLYGON City + Town + Apartment + Office как костяк) → докупать штучные модели только под
уникальный реквизит (дёнер-станок, кальян, иконы в церкви, прилавки рынка). Единый стиль одного
вендора = визуальная цельность без ручной перерисовки.

## 6.2. Реестр локаций (Нойкёльн-прототип + расширение)

Формат: **id** — игровое имя — реальный референс → функция → ключевой реквизит → **🔎 ключи поиска ассетов**.

### Жильё
- **`hostel_komet`** — Хостел «Komet» — берлинский бэкпэкер-хостел → база «Соискателя», сосед Виктор → двухъярусные кровати, шкафчики, общий стол.
  🔎 `low poly hostel dorm room`, `low poly bunk bed`, `POLYGON Apartment interior`
- **`plattenbau_flat`** — Квартира в Платтенбау — Марцан/Хеллерсдорф, панельки ГДР → жильё восточных линий (Война, Студент) → типовая кухня, балкон, узкий коридор.
  🔎 `low poly soviet apartment block`, `low poly Plattenbau / panel building`, `low poly GDR apartment interior`
- **`altbau_flat`** — Квартира в Альтбау — западный доходный дом, высокие потолки, лепнина → «немецкий Берлин», WG → большие окна, паркет, кафельная печь.
  🔎 `low poly old european apartment`, `low poly Berlin Altbau`, `POLYGON apartment`
- **`refugee_heim`** — Общежитие/Heim — контейнерный городок или перестроенное здание → старт «Беженца» → ряды коек, общая кухня, контейнеры-модули.
  🔎 `low poly refugee camp container`, `low poly shipping container housing`, `low poly bunk dormitory`
- **`overcrowded_flat`** — Перенаселённая квартира — барак от бригады → линия «Заработок» → матрасы на полу, сумки, теснота.
  🔎 (переиспользовать `plattenbau_flat` + `low poly mattress`, `low poly cardboard boxes`)
- **`einliegerwohnung`** — Квартирка фрау Шмидт — пристройка/полуподвал → награда ветки альтруизма → уютная, старомодная, с вязаными салфетками.
  🔎 `low poly cozy old apartment`, `low poly granny living room`

### Государство и институты
- **`buergeramt`** — Bürgeramt Neukölln — районная управа → Anmeldung, узел N1 → зал ожидания, табло номеров, стеклянные стойки, пластиковые стулья.
  🔎 `low poly government office`, `low poly waiting room`, `low poly DMV / bureau interior`, `POLYGON Office`
- **`auslaenderbehoerde`** — Ausländerbehörde (LEA) — ведомство по иностранцам → решение судьбы статуса (N9) → (визуально как `buergeramt`, мрачнее, длиннее коридоры).
  🔎 (переиспользовать `buergeramt` + `low poly long corridor`)
- **`jobcenter`** — Jobcenter — соцслужба → линии §24/легальные пути → стойки, очередь, плакаты.
  🔎 (переиспользовать `buergeramt`)
- **`bamf_office`** — Кабинет собеседования BAMF — линия «Беженец», Anhörung → стол, переводчик, диктофон, две стороны стола.
  🔎 `low poly interrogation room`, `low poly office desk interview`

### Работа и торговля
- **`mehmet_kebab`** — Кебабная Мехмета — дёнерная на Зонненаллее → подработка, хаб турецкой общины → вертикальный гриль-станок, витрина, пластиковые столы, неон-вывеска.
  🔎 `low poly kebab shop`, `low poly doner stand`, `low poly fast food restaurant interior`
- **`sonnenallee_market`** — Зонненаллее — «арабская улица», рынок → хаб слухов, арабская/турецкая община → прилавки овощей, золотая лавка, кальянная, пекарня, вывески на арабском.
  🔎 `low poly street market stalls`, `low poly bazaar`, `POLYGON Town market`, `low poly shisha lounge`
- **`baustelle`** — Стройка на Херманнштрассе — → работа вчёрную, Богдан, облава Zoll (N6) → леса, бетономешалка, вагончик-бытовка, краны, ограждение.
  🔎 `low poly construction site`, `POLYGON Construction`, `low poly scaffolding`, `low poly portacabin`
- **`internet_cafe`** — Интернет-кафе Али — → дешёвый интернет, фиксер-контакты, серое → ряды старых ПК, телефонные кабинки, вывеска call-shop.
  🔎 `low poly internet cafe`, `low poly call shop`, `low poly computer desk row`
- **`spaeti_karim`** — Шпэти дяди Карима — берлинский Späti (ночной ларёк) → еда в долг, доска объявлений, барометр уличной репутации → холодильники с напитками, журналы, пивные ящики, доска объявлений.
  🔎 `low poly convenience store`, `low poly kiosk shop`, `Kenney Mini Market`, `low poly corner shop interior`
- **`dong_xuan`** — Dong Xuan Center — вьетнамский оптовый рынок-ангар (Лихтенберг) → линия «Студент», вьетнамская теневая экономика → металлический ангар, ряды боксов, текстиль, общепит, нейл-салон.
  🔎 `low poly warehouse market`, `low poly wholesale hall`, `low poly indoor market stalls`
- **`russian_shop`** — Русский магазин — Charlottengrad / восток → русскоязычная община, продукты из дома → витрины с кириллицей, пельмени, гречка.
  🔎 (переиспользовать `spaeti_karim`/`low poly grocery store` + кириллические текстуры-вывески)
- **`arbeiterstrich`** — Биржа подённого труда — угол, где ждут «бригадиров» → линия «Заработок» → группа мужчин у дороги, фургоны.
  🔎 `low poly street corner`, `low poly people standing` (+ ассеты людей)

### Социальное и досуг
- **`bar_sandmann`** — Бар «Sandmann» — берлинская Kneipe → вечерняя социалка, Виктор-завсегдатай → барная стойка, неон, диваны, бильярд.
  🔎 `low poly bar interior`, `low poly pub`, `POLYGON City bar`
- **`cafe_third_wave`** — Кафе Эмилии — спешелти-кофейня, экспат-/крич-скоп → романтическая ветка, экспат-пузырь → деревянные столы, латте-арт, ноутбуки, растения.
  🔎 `low poly coffee shop`, `low poly hipster cafe`, `low poly cafe interior`
- **`hasenheide_park`** — Парк Хазенхайде — → днём бег/шахматы (relief), ночью риск/контур → деревья, скамейки, шахматный столик, фонари, тропинки.
  🔎 `low poly park`, `low poly trees pack`, `low poly park bench`, `POLYGON Nature`
- **`mosque_community`** — Мечеть / общинный центр — → арабская/турецкая община, поддержка → минарет, ковры, обувь у входа (геометрия минимальна, акцент текстурой).
  🔎 `low poly mosque`, `low poly islamic interior`, `low poly community center`
- **`storefront_church`** — Пятидесятническая церковь «в магазине» — → линия «Невидимка», безусловная поддержка → бывшая лавка с рядами стульев, крест, баннеры, динамики.
  🔎 `low poly church interior`, `low poly chairs rows`, `low poly storefront` (+ баннеры-текстуры)

### Транспорт и улица
- **`ubahn_station`** — Станция U-Bahn — → контроль контролёров (событие), перемещение → платформа, кафель, турникеты(нет — в Берлине их нет!), валидатор, табло.
  🔎 `low poly subway station`, `low poly metro platform`, `low poly underground train`
  ⚠️ Реализм: в берлинском метро **нет турникетов** — только валидаторы и контролёры в штатском. Не ставить турникеты.
- **`ubahn_car`** — Вагон U-Bahn — → сцена контроля → жёлто-красный вагон BVG (цвет!), поручни, сиденья.
  🔎 `low poly subway car interior`, `low poly metro train wagon`
- **`street_neukoelln`** — Улицы Нойкёльна — → перемещение, ambient → доходные дома, граффити, велодорожки, мусорные баки, кебабные, шпэти.
  🔎 `POLYGON City`, `low poly european street`, `Kenney City Kit`, `low poly modular street`
- **`airport_ber`** — Аэропорт BER / прилёт — → пролог «Соискателя»/«Студента» → зал прилёта, ленты багажа, таблички.
  🔎 `low poly airport interior`, `low poly arrivals hall`

## 6.3. «Берлинскость» дёшево: слой деталей поверх обобщённых моделей

Геометрию берём обобщённую, **узнаваемость наводим слоем деталей** (текстуры/декали/реквизит/свет):
- **Вывески и текст:** немецкие/арабские/турецкие/кириллические надписи как текстуры-декали (Spätkauf, Döner, Wechselstube, Apotheke, аптечный крест).
- **Цвет транспорта:** жёлто-красный BVG (U-Bahn/трамвай/автобус) — мгновенно «Берлин».
- **Граффити-декали** на любых стенах — фирменная берлинская фактура, копеечно по полигонам.
- **Реквизит-маркеры:** Pfand-бутылки у урн, велосипеды у каждого столба, Ampelmännchen-светофор, доска объявлений в шпэти, кальян на столе, дёнер-станок, мусорные контейнеры BSR (оранжевые).
- **Погода/свет/время суток:** серое бюрократическое утро vs неоновая прекарная ночь (день/night-cycle из v0.1 как драматургический инструмент).
- **Текст рассказчика** добивает остальное: запах, язык вокруг, кто во что одет — это «бесплатные» детали без геометрии.

## 6.4. Единый реестр id (для `entry_conditions.location_in`)

```
Жильё:        hostel_komet, plattenbau_flat, altbau_flat, refugee_heim, overcrowded_flat, einliegerwohnung
Институты:    buergeramt, auslaenderbehoerde, jobcenter, bamf_office
Работа/торг:  mehmet_kebab, sonnenallee_market, baustelle, internet_cafe, spaeti_karim, dong_xuan, russian_shop, arbeiterstrich
Социальное:   bar_sandmann, cafe_third_wave, hasenheide_park, mosque_community, storefront_church
Транспорт:    ubahn_station, ubahn_car, street_neukoelln, airport_ber
```
Группы локаций для условий: `{ubahn: [ubahn_station, ubahn_car]}`, `{state: [buergeramt, auslaenderbehoerde, jobcenter, bamf_office]}`, `{community_hub: [sonnenallee_market, spaeti_karim, mosque_community, storefront_church, dong_xuan]}`.

## 6.5. Заметки для реализации (бюджет ассетов)

- **Прототип (текстовый, v0.1 §4.3.1):** 3D не нужен — только id локаций и текст. Реестр выше уже его обслуживает.
- **3D-обёртка (v0.1 §4.3.4):** один район (Нойкёльн), ~12 ключевых интерьеров/экстерьеров из реестра, перемещение, смена времени суток.
- **Переиспользование — закон:** auslaenderbehoerde/jobcenter = перекрашенный buergeramt; russian_shop/overcrowded_flat = реквизит поверх базовых. Уникальная геометрия только там, где без неё нет узнавания (kebab-станок, рынок, метро-вагон, церковь, рынок-ангар).
- Все ассеты — **один стилевой пак-костяк** (Synty POLYGON City/Town/Apartment/Office) + штучные докупки. Не мешать разные стили (см. `07`).
