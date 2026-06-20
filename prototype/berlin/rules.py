"""Rules — авторитарный резолвер: условия входа, выбор ветки, скилл-чек, эффекты.

Резолв детерминирован при фиксированном сиде (v0.1 §4.2.5): RNG сидируется из
(state.seed, state.turn, event_id, branch_id).
"""
from __future__ import annotations

import random
from typing import Any

from .content_loader import Content
from .state import GameState


class Resolver:
    def __init__(self, content: Content):
        self.c = content

    # ---------- предикаты ----------
    def eval_pred(self, st: GameState, pred: dict) -> bool:
        for key, val in pred.items():
            if not self._one(st, key, val):
                return False
        return True

    def _one(self, st: GameState, key: str, val: Any) -> bool:
        if key == "day_gte":      return st.day >= val
        if key == "day_lte":      return st.day <= val
        if key == "visa_lte":     return st.visa_days <= val
        if key == "flag":         return st.has(val)
        if key == "flag_not":     return not st.has(val)
        if key == "any_flag":     return any(st.has(f) for f in val)
        if key == "all_flags":    return all(st.has(f) for f in val)
        if key == "money_lt":     return st.money < val
        if key == "money_gte":    return st.money >= val
        if key == "location":     return val == "any" or st.location == val
        if key == "location_in":
            members = self.c.group_members(val) if isinstance(val, str) else val
            return st.location in members
        if key == "counter_gte":  return all(st.counters.get(k, 0) >= v for k, v in val.items())
        if key == "axis_gte":     return all(st.axis(k) >= v for k, v in val.items())
        if key == "axis_lte":     return all(st.axis(k) <= v for k, v in val.items())
        if key == "skill_gte":    return all(st.skill(k) >= v for k, v in val.items())
        if key == "leaning_gte":  return all(st.leanings.get(k, 0) >= v for k, v in val.items())
        if key == "faction_gte":  return all(st.faction.get(k, 0) >= v for k, v in val.items())
        if key == "rumor":        return any(r["tag"] == val for r in st.rumors)
        return True  # неизвестный предикат не блокирует (мягкая деградация)

    def eval_conditions(self, st: GameState, cond: dict | None) -> bool:
        if not cond:
            return True
        if any(not self.eval_pred(st, p) for p in cond.get("all", [])):
            return False
        anys = cond.get("any", [])
        if anys and not any(self.eval_pred(st, p) for p in anys):
            return False
        if any(self.eval_pred(st, p) for p in cond.get("none", [])):
            return False
        return True

    # ---------- отбор событий ----------
    def eligible(self, st: GameState) -> list[dict]:
        out = []
        for ev in self.c.events.values():
            if ev.get("line") not in (st.line, "shared", None):
                continue
            if ev.get("once") and ev["id"] in st.fired_events:
                continue
            if st.cooldowns.get(ev["id"], 0) > st.day:
                continue
            loc = ev.get("location")
            if loc and loc not in ("any", None) and loc != st.location:
                # допускаем по entry.location_in, иначе требуем совпадения локации
                if not self._loc_ok_by_entry(st, ev):
                    continue
            trig = ev.get("trigger")
            if trig == "scheduled" and st.day < ev.get("day", 1):
                continue
            if not self.eval_conditions(st, ev.get("entry")):
                continue
            out.append(ev)
        return out

    def _loc_ok_by_entry(self, st: GameState, ev: dict) -> bool:
        for p in ev.get("entry", {}).get("all", []):
            if "location_in" in p and self._one(st, "location_in", p["location_in"]):
                return True
        return False

    def pick_forced(self, st: GameState) -> dict | None:
        """Обязательное событие сцены (scheduled/chain/node/reactive) с макс. приоритетом."""
        cands = [e for e in self.eligible(st)
                 if e.get("trigger") in ("scheduled", "chain", "reactive") or e.get("node")]
        if not cands:
            return None
        return sorted(cands, key=lambda e: e.get("priority", 0), reverse=True)[0]

    def pool(self, st: GameState) -> list[dict]:
        return [e for e in self.eligible(st) if e.get("trigger") == "pool"]

    # ---------- сопоставление ветки ----------
    def match_branch(self, ev: dict, intent: dict, st: GameState) -> dict | None:
        for br in ev.get("branches", []):
            m = br.get("match", {})
            if intent["verb"] not in m.get("verbs", []):
                continue
            if m.get("methods") and intent.get("method") not in m["methods"]:
                continue
            if m.get("honesty") and intent.get("honesty") not in m["honesty"]:
                continue
            if m.get("tone") and intent.get("tone") not in m["tone"]:
                continue
            if any(not self.eval_pred(st, p) for p in br.get("requires", [])):
                continue
            return br
        return None

    # ---------- скилл-чек ----------
    def skill_check(self, st: GameState, spec: dict, rng: random.Random) -> bool:
        eff = st.skill(spec["skill"])
        for s, w in spec.get("plus", {}).items():
            eff += st.skill(s) * w
        vs = spec["vs"]
        chance = max(5, min(95, 50 + (eff - vs)))  # %
        return rng.random() * 100 < chance

    def pick_outcome(self, st: GameState, br: dict, rng: random.Random) -> dict:
        outcomes = br.get("outcomes", [])
        if br.get("skill_check"):
            ok = self.skill_check(st, br["skill_check"], rng)
            tag = "success" if ok else "fail"
            for o in outcomes:
                if o.get("on") == tag:
                    return o
        for o in outcomes:
            if o.get("on", "always") == "always":
                return o
        return outcomes[0] if outcomes else {"text": "...", "on": "always"}

    # ---------- применение эффектов ----------
    def apply_effects(self, st: GameState, ev: dict, eff: dict, economy: dict) -> list[str]:
        notes: list[str] = []
        if "money" in eff:
            st.money += eff["money"]; notes.append(f"€{eff['money']:+d}")
        for f in eff.get("set_flags", []):
            st.set_flag(f)
        for f in eff.get("unset_flags", []):
            st.unset_flag(f)
        for k, v in eff.get("inc", {}).items():
            st.counters[k] = st.counters.get(k, 0) + v
        for fac, v in eff.get("faction", {}).items():
            st.faction[fac] = st.faction.get(fac, 0) + v; notes.append(f"репутация[{fac}]{v:+d}")
        for lk, v in eff.get("leaning", {}).items():
            st.leanings[lk] = st.leanings.get(lk, 0) + v
        if "rumor" in eff:
            r = dict(eff["rumor"]); r["day"] = st.day
            st.rumors.append(r); notes.append(f"слух «{r['tag']}»")
        if "dossier" in eff:
            st.dossier.append(f"д.{st.day}: {eff['dossier']}"); notes.append("заметка в дело")
        for stat in ("stress", "hunger", "fatigue"):
            if stat in eff:
                setattr(st, stat, max(0, getattr(st, stat) + eff[stat]))
        # рост навыков (v0.1 §2.3)
        sm = economy.get("skills_model", {})
        softcap = sm.get("softcap", 70)
        for sk, xp in eff.get("skill_xp", {}).items():
            cur = st.skills.get(sk, 0)
            grow = int(round(xp * max(0.1, (1 - cur / softcap))))
            st.skills[sk] = min(100, cur + max(1, grow))
        return notes
