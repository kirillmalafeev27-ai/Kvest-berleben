"""Parser — свободный текст игрока → интент из ЗАКРЫТОГО словаря (v0.1 §1).

Stub: сопоставление по русским ключам из verbs.yaml. Claude: тот же закрытый каталог
в системном промпте, строгий JSON, temperature 0.
"""
from __future__ import annotations

import json
import re

from .content_loader import Content
from .llm import LLM


PARSER_SYSTEM = """Ты — парсер намерений для текстовой игры про иммигранта в Берлине.
Сопоставь свободный ввод игрока с ОДНИМ глаголом из закрытого каталога. Не придумывай
действий и целей вне переданных списков. Верни СТРОГО валидный JSON:
{"verb": <из verbs>, "target": <id из targets или null>, "method": <из методов глагола или null>,
 "honesty": "truthful|half_truth|lie|omission", "tone": "polite|neutral|aggressive|submissive|sarcastic|desperate|charming|cold",
 "props": {}, "confidence": 0..1}
Если ввод не маппится — verb:"observe", confidence ниже 0.4. Только JSON, без пояснений."""


class IntentParser:
    def __init__(self, content: Content, llm: LLM):
        self.c = content
        self.llm = llm

    def parse(self, text: str, present_targets: list[str]) -> dict:
        if self.llm.available:
            try:
                return self._parse_claude(text, present_targets)
            except Exception:
                pass  # деградация к stub
        return self._parse_stub(text, present_targets)

    # ---------- STUB ----------
    def _parse_stub(self, text: str, present_targets: list[str]) -> dict:
        t = text.lower().strip()
        best_verb, best_score = None, 0
        for verb, spec in self.c.verbs.items():
            for kw in spec.get("ru", []):
                if kw in t:
                    score = len(kw)
                    if score > best_score:
                        best_verb, best_score = verb, score
        verb = best_verb or "observe"
        confidence = 0.85 if best_verb else 0.3

        method = self._detect_method(verb, t)
        honesty = self._detect_from(self.c.honesty_kw, t, default="truthful")
        tone = self._detect_from(self.c.tone_kw, t, default="neutral")
        target = self._detect_target(t, present_targets)

        props: dict = {}
        m = re.search(r"(\d{1,4})\s*(?:€|евро|euro)?", t)
        if m and verb in ("bribe", "give", "trade", "borrow"):
            props["amount"] = int(m.group(1))
        # частые маркеры
        if any(w in t for w in ["зайц", "без билет"]):
            verb, method = "move", "transit_fare_dodge"
        return {
            "verb": verb, "target": target, "method": method,
            "honesty": honesty, "tone": tone, "props": props,
            "confidence": confidence, "raw": text,
        }

    def _detect_method(self, verb: str, t: str) -> str | None:
        methods = self.c.verbs.get(verb, {}).get("methods", [])
        if not methods:
            return None
        # эвристики метода по ключам
        hint = {
            "money": ["деньг", "взятк", "€", "евро", "плачу"],
            "labor": ["донести", "помочь физически", "потаскать", "руками"],
            "buy": ["покупа", "плачу за"], "sell": ["продаю", "сбыва"], "haggle": ["торгу"],
            "illegal_shift": ["вчёрн", "вчерн", "без договор", "на стройк"],
            "legal_shift": ["легальн", "по договор"], "gig": ["курьер", "гиг", "подвезти"],
            "forged": ["фейк", "поддел", "липов"], "genuine": ["настоящ", "свои документ"],
            "pity": ["умоля", "жалоб", "войти в положен", "отчаянн"],
            "violence": ["изобью", "врежу", "силой"], "report_to_authority": ["жалобу", "заяв", "полиц"],
            "through_fixer": ["через человек", "решал", "фиксер"],
            "transit_fare_dodge": ["зайц", "без билет"], "transit_paid": ["билет", "оплачива проезд"],
            "firm": ["твёрдо", "наотрез"], "polite": ["вежлив"], "rude": ["грубо", "посыла"],
        }
        for meth in methods:
            for kw in hint.get(meth, []):
                if kw in t:
                    return meth
        return None

    def _detect_from(self, table: dict, t: str, default: str) -> str:
        # пословное совпадение по началу слова — чтобы «Виктору» не давало tone=aggressive («ору»)
        words = re.findall(r"\w+", t)
        for key, kws in table.items():
            for kw in kws:
                if not kw:
                    continue
                if " " in kw:
                    if kw in t:
                        return key
                elif any(w.startswith(kw) or kw.startswith(w) and len(w) >= 4 for w in words):
                    return key
        return default

    def _detect_target(self, t: str, present_targets: list[str]) -> str | None:
        for tid in present_targets:
            npc = self.c.npc(tid)
            name = npc.get("name", "").lower().strip("«»\"")
            if name and name.split()[0] in t:
                return tid
        return present_targets[0] if len(present_targets) == 1 else None

    # ---------- CLAUDE ----------
    def _parse_claude(self, text: str, present_targets: list[str]) -> dict:
        verbs = list(self.c.verbs.keys())
        user = json.dumps({
            "input": text, "verbs": verbs, "targets": present_targets,
            "methods_by_verb": {v: self.c.verbs[v].get("methods", []) for v in verbs},
        }, ensure_ascii=False)
        raw = self.llm.complete(PARSER_SYSTEM, user, temperature=0.0, max_tokens=300)
        js = raw[raw.find("{"): raw.rfind("}") + 1]
        data = json.loads(js)
        data.setdefault("props", {})
        data["raw"] = text
        return data
