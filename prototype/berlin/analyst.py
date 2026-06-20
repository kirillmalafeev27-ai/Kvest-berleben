"""Analyst — превращает подсказки-дельты исхода в финальные сдвиги осей.

Правила (v0.1 §2.2): вес = ставки; считается выбор, а не успех; убывающая отдача
(антифарм); инерция (дальше от 0 — дороже откат); контекст смягчает; код клампит.
В stub-режиме источник дельт — `outcome.deltas`. При Claude — те же дельты можно
переоценить моделью, но код всё равно клампит результат.
"""
from __future__ import annotations

from .state import GameState, AXES


class Analyst:
    def __init__(self, economy: dict):
        m = economy.get("axes_model", {})
        self.clamp_per_event = m.get("clamp_per_event", 15)
        self.axis_min = m.get("axis_min", -100)
        self.axis_max = m.get("axis_max", 100)
        self.antifarm_base = m.get("antifarm_base", 0.5)
        self.inertia_threshold = m.get("inertia_threshold", 50)
        self.inertia_factor = m.get("inertia_factor", 0.6)

    def apply(self, st: GameState, intent: dict, outcome: dict, stakes: str) -> dict[str, int]:
        raw = outcome.get("deltas", {}) or {}
        if not raw:
            return {}

        # антифарм: k-е повторение глагола за день × base^k
        verb = intent.get("verb", "")
        k = st.day_action_counts.get(verb, 0)
        antifarm = self.antifarm_base ** k

        # контекст: голод смягчает штраф LAW за steal/beg
        hungry = st.hunger >= 50

        applied: dict[str, int] = {}
        for ax in AXES:
            d = raw.get(ax, 0)
            if not d:
                continue
            val = d * antifarm

            if hungry and ax == "L" and d < 0 and verb in ("steal", "beg"):
                val *= 0.5  # кража от голода < кражи ради наживы

            # инерция: дельта, толкающая ось обратно к 0, при |axis|>порога — слабее
            cur = st.axis(ax)
            if abs(cur) >= self.inertia_threshold and (cur > 0) != (val > 0):
                val *= self.inertia_factor

            # кламп величины за событие
            val = max(-self.clamp_per_event, min(self.clamp_per_event, val))
            di = int(round(val))
            if di == 0 and d != 0:
                di = 1 if d > 0 else -1  # не терять знак значимого выбора

            st.axes[ax] = max(self.axis_min, min(self.axis_max, cur + di))
            applied[ax] = di

        st.day_action_counts[verb] = k + 1
        return applied
