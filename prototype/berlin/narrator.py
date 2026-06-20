"""Narrator — описывает мир и исход. Получает РЕЗУЛЬТАТ (не выбирает его).

Stub: собирает текст из фактов сцены и текста исхода, добавляет голос NPC.
Claude: те же факты + распарсенный исход + стиль-карточка NPC, temperature ~0.8,
с запретом выдумывать предметы/цены/обещания вне переданного (v0.1 §4.2).
"""
from __future__ import annotations

from .content_loader import Content
from .llm import LLM

NARRATOR_SYSTEM = """Ты — рассказчик текстовой игры про иммигранта в Берлине. Тон: тёплая
меланхолия, «честно, но не чернуха». Тебе передают факты сцены, выбранный движком исход и
стиль-карточку NPC. Опиши ровно этот исход в 2–4 предложениях, в голосе указанного NPC.
ЗАПРЕЩЕНО: выдумывать предметы, цены, обещания NPC и любые факты вне переданного списка."""


class Narrator:
    def __init__(self, content: Content, llm: LLM):
        self.c = content
        self.llm = llm

    def scene_intro(self, ev: dict) -> str:
        facts = ev.get("facts", [])
        intro = ev.get("intro", "")
        loc = self.c.loc_name(ev.get("location", ""))
        head = f"— {ev.get('title','')} —  [{loc}]"
        body = "\n".join(facts)
        if intro:
            body += ("\n\n" + intro)
        return f"{head}\n{body}"

    def outcome(self, ev: dict, outcome: dict, applied_deltas: dict, npc_id: str | None) -> str:
        text = outcome.get("text", "...")
        if self.llm.available:
            try:
                return self._outcome_claude(ev, outcome, npc_id)
            except Exception:
                pass
        return text

    def steer(self, ev: dict, intent: dict, base_text: str, hint: str, npc_id: str | None) -> str:
        """Внутримировая реакция на действие ВНЕ сценарных веток + мягкий возврат к сюжету.
        Stub: готовый base_text + hint. Claude: живая дефлексия по фактам сцены."""
        if not self.llm.available:
            return f"{base_text}\n{hint}".strip()
        npc = self.c.npc(npc_id) if npc_id else {}
        user = (
            f"ФАКТЫ СЦЕНЫ: {ev.get('facts')}\n"
            f"ИГРОК ПОПЫТАЛСЯ (вне доступных опций): verb={intent.get('verb')}, "
            f"текст='{intent.get('raw','')}'\n"
            f"СТИЛЬ NPC: {npc.get('name','')} — {npc.get('register','')}\n"
            f"ДОСТУПНЫЕ ПО СУТИ ХОДЫ: {hint}\n"
            "Опиши в 1–3 предложениях, как мир/NPC внутри сюжета реагирует на эту выходку "
            "(не выходя за факты, не выдавая предметов/обещаний), и МЯГКО верни игрока к реальному "
            "выбору сцены. Не ломай погружение, не пиши меню."
        )
        return self.llm.complete(NARRATOR_SYSTEM, user, temperature=0.7, max_tokens=220).strip()

    def reflection(self, axes: dict) -> str | None:
        """Редкое текстовое «отражение» характера (оси числами не показываем)."""
        if axes.get("T", 0) <= -40:
            return "(Ты замечаешь: тебе всё реже верят — даже когда говоришь правду.)"
        if axes.get("A", 0) >= 40:
            return "(В общине о тебе говорят: «этот — помогает».)"
        if axes.get("P", 0) >= 40:
            return "(О тебе говорят: «гордый. не гнётся».)"
        if axes.get("L", 0) <= -40:
            return "(Нужные люди уже знают, к кому обращаться по «тёмным» делам.)"
        return None

    def _outcome_claude(self, ev: dict, outcome: dict, npc_id: str | None) -> str:
        npc = self.c.npc(npc_id) if npc_id else {}
        user = (
            f"ФАКТЫ СЦЕНЫ: {ev.get('facts')}\n"
            f"ИСХОД (опиши ровно это): {outcome.get('text')}\n"
            f"СТИЛЬ NPC: {npc.get('name','')} — {npc.get('register','')}; "
            f"словечки: {npc.get('tics', [])}; языки: {npc.get('languages', [])}"
        )
        return self.llm.complete(NARRATOR_SYSTEM, user, temperature=0.8, max_tokens=300).strip()
