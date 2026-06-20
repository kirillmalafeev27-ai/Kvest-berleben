"""Generative GM («Ведущий») — реагирует на ЛЮБОЙ свободный ввод по существу действия.

(state + сырой текст игрока) → (narration + структурные state_changes), которые движок
валидирует/клампит и применяет. Claude — полноценный генеративный ведущий по контракту ниже;
офлайн — приближение: классификация ввода по смыслу + заземлённая реакция, которая ДЕЙСТВУЕТ
на мир (двигает/тратит/открывает ниточку/гонит время), а не «наказывает и суёт меню».

См. design/11_generativnyy_mir.md.
"""
from __future__ import annotations

import json
import re

from .content_loader import Content
from .llm import LLM


GM_SYSTEM = """Ты — Ведущий (game master) текстовой игры о выживании иммигранта в Берлине.
Игрок вводит ЛЮБОЕ действие свободным текстом. Реагируй СООБРАЗНО действию, как реагировала бы
реальность. Правила:
1. Отвечай конкретно на то, что игрок написал.
2. Заземляй в реальность: игрок может ПОПЫТАТЬСЯ что угодно; грандиозное/невозможное встречает
   реалистичное трение, раскрывает характер, иногда открывает маленькую настоящую ниточку.
3. НИКОГДА не выдавай невозможного (президентом не стать; статус по щелчку не выдаётся).
4. НИКОГДА не ломай погружение и не показывай меню вариантов. Ситуация продолжается диегетически.
5. Уважай состояние игрока: не выдумывай деньги/предметы/статус. Ты ПРЕДЛАГАЕШЬ дельты — движок применит.
6. Держи давление живым (деньги, виза/срок, голод тикают — это двигатель сюжета).
7. Тон: «честно, но не чернуха», достоинство, без карикатур. Языки звучат (вкрапления с переводом).
Верни СТРОГО валидный JSON:
{"interpretation": str, "plausibility": "trivial|plausible|hard|impossible_now|fantastical",
 "narration": str (2-4 предложения, реакция мира именно на это),
 "state_changes": {"money": int, "location": str|null, "set_flags": [str], "unset_flags": [str],
                   "stress": int, "hunger": int, "fatigue": int, "time_advance_days": int,
                   "new_fact": str|null, "opens_thread": {"id": str, "summary": str}|null},
 "npc_reaction": str|null, "axis_hints": {"G":int,"T":int,"A":int,"L":int,"P":int}}
Только JSON, без пояснений."""


# ---- смысловые категории для офлайн-приближения ----
CATS = {
    "leave_country": ["сбежать из стран", "сбежать отсюда", "уехать из герман", "уехать из стран",
                      "свалить", "эмигрир", "покинуть стран", "убежать из бер", "домой насовсем",
                      "на границ", "в другую стран", "уехать навсегда", "бежать из стран", "сбегу из"],
    "grand_ambition": ["президент", "разбогат", "миллион", "открыть бизнес", "свой бизнес",
                       "стать звезд", "знаменит", "к власти", "депутат", "стать мэром", "править",
                       "великим", "захватить", "построить импери", "магнат"],
    "fantasy": ["взлет", "летать", "дракон", "супермен", "магия", "колдую", "телепорт", "бэтмен",
                "стану богом", "бессмерт", "путешеств во времен", "суперсил"],
    "call_home": ["звоню домой", "звоню родны", "звоню родител", "звоню маме", "звоню жене",
                  "звоню мужу", "звоню детям", "связаться с родны", "пишу домой"],
    "faith": ["молюсь", "молит", "помолит", "мечет", "церков", "обращаюсь к богу", "намаз", "ставлю свечу", "к богу"],
    "numb": ["напиться", "напьюсь", "выпить чтобы", "бухаю", "забыться", "наркот", "укурит", "залить горе"],
    "wander": ["гуляю по город", "брожу", "иду куда глаза", "осматриваю город", "слоняюсь", "просто иду гулять"],
    "hustle": ["хочу заработать", "найти работу", "ищу подработ", "нужны деньги", "where to work"],
    "despair": ["не хочу жить", "покончить", "сдаюсь совсем", "всё бессмысленно", "не могу больше"],
}


class GM:
    def __init__(self, content: Content, llm: LLM):
        self.c = content
        self.llm = llm

    # ---------- публичный вход ----------
    def react(self, st, intent: dict, scene: dict | None) -> dict:
        if self.llm.available:
            try:
                return self._react_claude(st, intent, scene)
            except Exception:
                pass
        return self._react_offline(st, intent, scene)

    # ---------- применение дельт (движок-авторитар: валидация/кламп) ----------
    def apply(self, st, ch: dict) -> list[str]:
        notes: list[str] = []
        if "money" in ch:
            d = max(-2000, min(2000, int(ch["money"])))
            if d < 0:
                d = max(d, -st.money)          # нельзя уйти ниже нуля выдумкой
            if d:
                st.money += d; notes.append(f"€{d:+d}")
        loc = ch.get("location")
        if loc and loc in self.c.locations:
            st.location = loc; notes.append(f"→ {self.c.loc_name(loc)}")
        for f in ch.get("set_flags", []) or []:
            st.set_flag(str(f))
        for f in ch.get("unset_flags", []) or []:
            st.unset_flag(str(f))
        for stat in ("stress", "hunger", "fatigue"):
            if stat in ch and ch[stat]:
                v = max(-50, min(50, int(ch[stat])))
                setattr(st, stat, max(0, min(100, getattr(st, stat) + v)))
        th = ch.get("opens_thread")
        if th and th.get("id"):
            st.set_flag("thread_" + re.sub(r"\W+", "_", str(th["id"]))[:40])
        nf = ch.get("new_fact")
        if nf:
            st.dossier.append(f"д.{st.day}: {nf}") if False else None  # факты — в лог, не в дело
        return notes

    # ---------- CLAUDE ----------
    def _react_claude(self, st, intent: dict, scene: dict | None) -> dict:
        snap = {
            "кто": f"{st.name}, линия {st.line}", "день": st.day,
            st.clock_label: st.visa_days, "деньги_eur": st.money, "локация": st.location,
            "голод": st.hunger, "стресс": st.stress,
            "флаги": st.flags[-12:], "недавнее": st.dossier[-4:],
            "ситуация": (scene or {}).get("facts"),
        }
        user = ("СОСТОЯНИЕ:\n" + json.dumps(snap, ensure_ascii=False)
                + "\n\nДЕЙСТВИЕ ИГРОКА (свободный текст): " + intent.get("raw", ""))
        raw = self.llm.complete(GM_SYSTEM, user, temperature=0.85, max_tokens=500)
        data = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
        data.setdefault("state_changes", {})
        data.setdefault("axis_hints", {})
        return data

    # ---------- ОФФЛАЙН (приближение) ----------
    def _classify(self, text: str, verb: str) -> str:
        t = text.lower()
        # побег: глагол бегства + «страна/Германия/отсюда» (гибко, не точной фразой)
        esc = any(k in t for k in ["сбеж", "сбегу", "убеж", "свал", "уехать", "уеду", "уезжаю",
                                   "эмигр", "покину", "валю отсюда", "драпа", "линяю", "бежать"])
        cw = any(k in t for k in ["стран", "герман", "берлин", "отсюда", "границ", "за рубеж",
                                  "в другую", "домой насовсем"])
        if (esc and cw) or any(k in t for k in CATS["leave_country"]):
            return "leave_country"
        for cat, kws in CATS.items():
            if any(k in t for k in kws):
                return cat
        if verb in ("attack",):
            return "violence"
        if verb in ("steal",):
            return "theft"
        if verb in ("threaten",):
            return "menace"
        if verb == "observe" and len(t) > 3:  # не распозналось парсером → импровиз
            return "improv"
        return "improv"

    def _react_offline(self, st, intent: dict, scene: dict | None) -> dict:
        text = intent.get("raw", ""); verb = intent.get("verb", "observe")
        cat = self._classify(text, verb)
        fn = getattr(self, f"_f_{cat}", self._f_improv)
        return fn(st, text)

    # --- фреймы (каждый ДЕЙСТВУЕТ на мир) ---
    def _passport_note(self, st) -> str:
        return {
            "soiskatel": "паспорт при тебе, но виза скоро превратит его в тыкву",
            "bezhenec": "паспорт сдан в BAMF — без него ты никуда",
            "nevidimka": "паспорта у тебя и нет",
            "voyna": "паспорт при тебе, но дома — то, от чего ты уехал",
        }.get(st.line, "паспорт при тебе, но без статуса это просто книжечка")

    def _f_leave_country(self, st, text):
        note = self._passport_note(st)
        return {
            "interpretation": "игрок хочет уехать/сбежать из страны",
            "plausibility": "plausible",
            "narration": (f"Сбежать из страны — ты впервые думаешь об этом всерьёз. До автовокзала "
                          f"ZOB пара остановок: автобус до Парижа ~29 €, до Варшавы ~19 €. Вот только "
                          f"{note}; а на границе всё равно спросят бумаги. Уехать можно хоть завтра — "
                          f"вопрос лишь, есть ли куда."),
            "state_changes": {"stress": 6, "set_flags": ["considered_exit"],
                              "opens_thread": {"id": "exit", "summary": "обдумываешь отъезд"}},
            "npc_reaction": None, "axis_hints": {"P": 1},
        }

    def _f_grand_ambition(self, st, text):
        t = text.lower()
        if any(k in t for k in ["богат", "миллион", "бизнес", "магнат", "деньги поднять"]):
            narr = ("Разбогатеть? В этом городе с этого мечтают все на твоей улице. Большие деньги тут "
                    "у тех, у кого бумаги, язык и связи, — а у тебя пока ни счёта, ни Anmeldung. Но "
                    "маленькое дело, кэшем, на доверии общины — с него реально начать.")
            thread = {"id": "small_business", "summary": "мысль о своём маленьком деле"}
        else:
            narr = ("Президентом/большим человеком, говоришь? *(кто-то рядом усмехается)* Ты тут даже "
                    "голосовать не можешь — не гражданин. Но злость, что толкнула на эту мысль, "
                    "настоящая. С неё начинаются не президенты, а те, кто сколачивает своих и качает "
                    "права в районе. Может, с этого и начать.")
            thread = {"id": "organize", "summary": "мысль организовать своих"}
        return {
            "interpretation": "грандиозная амбиция", "plausibility": "fantastical",
            "narration": narr, "state_changes": {"set_flags": ["big_ambition"], "opens_thread": thread},
            "npc_reaction": "сосед по очереди хмыкнул", "axis_hints": {"P": 2, "A": 1},
        }

    def _f_fantasy(self, st, text):
        return {
            "interpretation": "невозможное/фантастика", "plausibility": "fantastical",
            "narration": ("Ты расправляешь плечи, будто сейчас взлетишь. Серое берлинское небо не "
                          "впечатлено. Реальность здесь тяжёлая и липкая, как ноябрьская морось, — "
                          "и она никуда не девается."),
            "state_changes": {"stress": -2}, "npc_reaction": None, "axis_hints": {},
        }

    def _f_call_home(self, st, text):
        line_beat = {
            "voyna": ("Голос в трубке дрожит и держится одновременно. После звонка ты долго сидишь, "
                      "глядя в стену: стало и легче, и невыносимее."),
            "zarabotok": ("Дома ждут перевод. Ты обещаешь «на той неделе точно». Кладёшь трубку с "
                          "тяжестью, которую не снять."),
        }.get(st.line, "Родной голос на пару минут возвращает тебе тебя прежнего. Потом — снова Берлин.")
        return {
            "interpretation": "звонок домой", "plausibility": "trivial",
            "narration": line_beat,
            "state_changes": {"stress": -6}, "npc_reaction": None, "axis_hints": {"A": 1},
        }

    def _f_faith(self, st, text):
        return {
            "interpretation": "обращение к вере", "plausibility": "trivial",
            "narration": ("Несколько минут тишины и чего-то большего тебя. Снаружи город всё так же "
                          "равнодушен, но внутри становится чуть просторнее."),
            "state_changes": {"stress": -8}, "npc_reaction": None, "axis_hints": {},
        }

    def _f_numb(self, st, text):
        return {
            "interpretation": "заглушить тревогу", "plausibility": "plausible",
            "narration": ("Ты заливаешь тревогу — на вечер помогает, наутро хуже. Денег чуть меньше, "
                          "ясности тоже."),
            "state_changes": {"money": -8, "stress": -10, "fatigue": 12},
            "npc_reaction": None, "axis_hints": {},
        }

    def _f_wander(self, st, text):
        return {
            "interpretation": "бесцельная прогулка", "plausibility": "trivial",
            "narration": ("Ты бредёшь по Нойкёльну: дёнер, граффити, чужая речь со всех сторон. "
                          "Город не замечает тебя — и в этом есть странный покой. День, впрочем, тает."),
            "state_changes": {"fatigue": 8, "stress": -4}, "npc_reaction": None, "axis_hints": {},
        }

    def _f_hustle(self, st, text):
        return {
            "interpretation": "ищет заработок (вне сцены)", "plausibility": "plausible",
            "narration": ("Деньги нужны были ещё вчера. Доска у шпэти Карима, кебабная Мехмета, "
                          "стройка, серые гиги у Али — варианты есть, за каждым своя цена. Ноги сами "
                          "несут в сторону Зонненаллее."),
            "state_changes": {}, "npc_reaction": None, "axis_hints": {},
        }

    def _f_despair(self, st, text):
        return {
            "interpretation": "отчаяние/срыв (чувствительное)", "plausibility": "plausible",
            "narration": ("Накрывает так, что трудно дышать. Но ты не один: в общине, у волонтёров, "
                          "по телефону доверия есть те, кто вытаскивал и не из такого. Сегодня "
                          "достаточно просто дожить до завтра."),
            "state_changes": {"stress": -6}, "npc_reaction": None, "axis_hints": {},
        }

    def _f_violence(self, st, text):
        return {
            "interpretation": "насилие", "plausibility": "plausible",
            "narration": ("Ты срываешься. Кто-то шарахается, кто-то кричит. Берлин не прощает таких "
                          "вспышек — улица и люди это запомнят."),
            "state_changes": {"stress": 8, "rumor_skip": True},
            "npc_reaction": "вокруг напряглись", "axis_hints": {"G": 4, "L": -2},
        }

    def _f_theft(self, st, text):
        return {
            "interpretation": "кража", "plausibility": "hard",
            "narration": ("Рука тянется к чужому. Сердце колотится — в этом городе камер и глаз "
                          "больше, чем кажется. Один прокол — и ты уже не выживающий, а «дело»."),
            "state_changes": {"stress": 6}, "npc_reaction": None, "axis_hints": {"L": -3},
        }

    def _f_menace(self, st, text):
        return {
            "interpretation": "угроза", "plausibility": "plausible",
            "narration": ("Ты переходишь на угрозы. На секунду это даёт ощущение силы — и тут же "
                          "оборачивается против тебя: так в этом городе двери только захлопываются."),
            "state_changes": {}, "npc_reaction": "собеседник холодеет", "axis_hints": {"G": 3},
        }

    def _f_improv(self, st, text):
        para = text.strip().rstrip(".!?")
        if len(para) > 80:
            para = para[:77] + "..."
        nudge = self._pressure_nudge(st)
        return {
            "interpretation": "нестандартное действие", "plausibility": "plausible",
            "narration": (f"Ты пробуешь: «{para}». Берлин принимает это без удивления — он видал и не "
                          f"такое — и катится дальше. {nudge}"),
            "state_changes": {"fatigue": 3}, "npc_reaction": None, "axis_hints": {},
        }

    def _pressure_nudge(self, st) -> str:
        if st.money < 150:
            return "Только вот кошелёк почти пуст, и это не отменить."
        if st.visa_days <= 20:
            return f"А срок ({st.clock_label}) поджимает: осталось {st.visa_days}."
        if st.hunger >= 60:
            return "А есть хочется всё сильнее."
        return "А день идёт, и сам себя не проживёт."
