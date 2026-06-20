"""Director — кривая напряжения (design/05 §5.4). Считает tension и подмешивает
из пула либо выдох (relief), либо давление (pressure)."""
from __future__ import annotations

import random

from .state import GameState


class Director:
    def __init__(self, economy: dict):
        d = economy.get("director", {})
        self.w_money = d.get("weight_money", 0.4)
        self.w_days = d.get("weight_days", 0.3)
        self.w_stress = d.get("weight_stress", 0.3)
        self.relief_above = d.get("relief_above", 0.65)
        self.pressure_below = d.get("pressure_below", 0.30)
        self.start_money = economy.get("start", {}).get("money", 1400)
        self.start_visa = economy.get("start", {}).get("visa_days", 90)

    def tension(self, st: GameState) -> float:
        money_f = 1 - max(0.0, min(1.0, st.money / max(1, self.start_money)))
        days_f = 1 - max(0.0, min(1.0, st.visa_days / max(1, self.start_visa)))
        stress_f = max(0.0, min(1.0, st.stress / 100))
        t = self.w_money * money_f + self.w_days * days_f + self.w_stress * stress_f
        return round(t, 3)

    def choose(self, st: GameState, pool: list[dict], rng: random.Random) -> dict | None:
        if not pool:
            return None
        t = self.tension(st)
        if t >= self.relief_above:
            relief = [e for e in pool if e.get("category") == "ambient"]
            pool = relief or pool
        elif t <= self.pressure_below:
            pres = [e for e in pool if e.get("category") == "pressure"]
            pool = pres or pool
        weights = [max(0.01, e.get("weight", 1.0)) for e in pool]
        return rng.choices(pool, weights=weights, k=1)[0]
