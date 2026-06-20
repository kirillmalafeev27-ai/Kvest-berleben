"""Engine — оркестратор цикла Parser→Rules→Analyst→Narrator + ход времени."""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from .content_loader import Content
from .state import GameState
from .parser import IntentParser
from .rules import Resolver
from .analyst import Analyst
from .narrator import Narrator
from .director import Director
from .gm import GM
from .llm import LLM


@dataclass
class StepResult:
    narration: str = ""
    changes: list[str] = field(default_factory=list)
    deltas: dict = field(default_factory=dict)
    reflection: str | None = None
    day_advanced: bool = False
    leads_to: str | None = None
    event_id: str | None = None
    branch_id: str | None = None
    intent: dict | None = None
    seed: int | None = None


class Engine:
    def __init__(self, content: Content, llm: LLM | None = None):
        self.c = content
        self.llm = llm or LLM()
        self.parser = IntentParser(content, self.llm)
        self.rules = Resolver(content)
        self.analyst = Analyst(content.economy)
        self.narrator = Narrator(content, self.llm)
        self.director = Director(content.economy)
        self.gm = GM(content, self.llm)

    # ---------- старт ----------
    def new_game(self, name: str = "Алекс", seed: int = 12345, line: str = "soiskatel") -> GameState:
        s = self.c.economy.get("start", {})
        prof = self.c.lines().get(line, {})
        skills = dict(s.get("skills", {}))
        skills.update(prof.get("skills", {}))
        st = GameState(
            name=name, line=line, seed=seed,
            money=prof.get("money", s.get("money", 1400)),
            visa_days=prof.get("clock_start", s.get("visa_days", 90)),
            clock_label=prof.get("clock_label", "виза"),
            location=prof.get("start_location", "hostel_komet"),
            skills=skills,
            flags=list(prof.get("flags", s.get("flags", []))),
        )
        return st

    # ---------- какая сцена сейчас ----------
    def current_scene(self, st: GameState) -> dict | None:
        if st.active_event:
            ev = self.c.events.get(st.active_event)
            loc = ev.get("location") if ev else None
            loc_ok = (not loc or loc in ("any", None) or loc == st.location
                      or self.rules._loc_ok_by_entry(st, ev))
            if ev and loc_ok and self.rules.eval_conditions(st, ev.get("entry")):
                return ev
            st.active_event = None   # ушёл из локации/условия отпали — сцена не «следует» за игроком
        # сначала — отложенные followups, если они уже проходят по условиям
        for fid in list(st.pending):
            ev = self.c.events.get(fid)
            if not ev or (ev.get("once") and fid in st.fired_events):
                st.pending.remove(fid); continue
            loc = ev.get("location")
            loc_ok = (not loc or loc in ("any", None) or loc == st.location
                      or self.rules._loc_ok_by_entry(st, ev))
            if loc_ok and self.rules.eval_conditions(st, ev.get("entry")):
                st.pending.remove(fid)
                st.active_event = fid
                return ev
        forced = self.rules.pick_forced(st)
        if forced:
            st.active_event = forced["id"]
            return forced
        return None

    def present_targets(self, ev: dict | None) -> list[str]:
        return list(ev.get("targets", [])) if ev else []

    # ---------- основной шаг ----------
    def step(self, st: GameState, text: str, ev: dict | None) -> StepResult:
        st.turn += 1
        intent = self.parser.parse(text, self.present_targets(ev))

        # явный переход между локациями — всегда разрешён
        if intent["verb"] == "move" and (ev is None or "move" not in self._verbs_of(ev)):
            return self._free_action(st, intent)

        # есть открытая (forced/active) сцена — резолвим её
        if ev is not None:
            return self._resolve(st, ev, intent)

        # открытой сцены нет — пробуем активировать фоновое (pool) событие по интенту
        pooled = self._match_pool(st, intent)
        if pooled is not None:
            return self._resolve(st, pooled, intent)

        return self._free_action(st, intent)

    def _match_pool(self, st: GameState, intent: dict) -> dict | None:
        cands = [e for e in self.rules.pool(st)
                 if (e.get("location") in (None, "any", st.location)
                     or self.rules._loc_ok_by_entry(st, e))]
        # приоритет: события с подходящей под интент веткой
        matching = [e for e in cands if self.rules.match_branch(e, intent, st)]
        if not matching:
            return None
        rng = random.Random(f"{st.seed}:{st.turn}:pool")
        return self.director.choose(st, matching, rng)

    def _verbs_of(self, ev: dict) -> set[str]:
        out: set[str] = set()
        for br in ev.get("branches", []):
            out.update(br.get("match", {}).get("verbs", []))
        return out

    def _resolve(self, st: GameState, ev: dict, intent: dict) -> StepResult:
        br = self.rules.match_branch(ev, intent, st)
        if br is None:
            return self._gm_react(st, ev, intent)   # Ведущий реагирует по существу действия

        seed_key = f"{st.seed}:{st.turn}:{ev['id']}:{br['id']}"
        rng = random.Random(seed_key)
        outcome = self.rules.pick_outcome(st, br, rng)

        changes = self.rules.apply_effects(st, ev, outcome.get("effects", {}), self.c.economy)
        deltas = self.analyst.apply(st, intent, outcome, ev.get("stakes", "low"))

        # followups / закрытие события
        for fid in outcome.get("followups", []):
            if fid not in st.pending:
                st.pending.append(fid)
        if ev.get("once"):
            if ev["id"] not in st.fired_events:
                st.fired_events.append(ev["id"])
        cd = ev.get("cooldown_days")
        if cd:
            st.cooldowns[ev["id"]] = st.day + cd
        st.active_event = None

        npc_id = (ev.get("targets") or [None])[0]
        narration = self.narrator.outcome(ev, outcome, deltas, npc_id)

        res = StepResult(
            narration=narration, changes=changes, deltas=deltas,
            reflection=self.narrator.reflection(st.axes),
            leads_to=outcome.get("leads_to"),
            event_id=ev["id"], branch_id=br["id"], intent=intent,
            seed=hash(seed_key) & 0xFFFFFFFF,
        )
        if outcome.get("effects", {}).get("advance_day"):
            self._advance_day(st); res.day_advanced = True
        return res

    # ---------- вольные действия / навигация ----------
    def _free_action(self, st: GameState, intent: dict) -> StepResult:
        v = intent["verb"]
        raw_unknown = (v == "observe" and intent.get("confidence", 1.0) < 0.4)
        if not raw_unknown:
            if v == "rest":
                self._advance_day(st)
                return StepResult(narration="Ты переводишь дух. Наступает новый день.",
                                  day_advanced=True, intent=intent)
            if v == "observe":
                loc = self.c.loc_name(st.location)
                nb = ", ".join(self.c.loc_name(x) for x in self.c.loc_connects(st.location)) or "—"
                return StepResult(narration=f"Ты в локации: {loc}. Отсюда можно пройти: {nb}.", intent=intent)
            if v == "inspect_self":
                return StepResult(
                    narration=(f"{st.name} ({st.line}), день {st.day}. Деньги: €{st.money}. "
                               f"{st.clock_label}: {st.visa_days}. "
                               f"Голод {st.hunger}, усталость {st.fatigue}, стресс {st.stress}."),
                    intent=intent)
            if v == "move":
                dest = self._detect_dest(intent)
                if dest:
                    fare_dodge = intent.get("method") == "transit_fare_dodge"
                    return self.travel(st, dest, fare_dodge)
                return StepResult(narration="Куда именно? Назови место (или используй /goto).", intent=intent)
        # всё прочее (дикое/неожиданное/нестандартное) — Ведущий реагирует по существу действия
        return self._gm_react(st, None, intent)

    def _gm_react(self, st: GameState, ev: dict | None, intent: dict) -> StepResult:
        r = self.gm.react(st, intent, ev)
        ch = r.get("state_changes", {}) or {}
        changes = self.gm.apply(st, ch)
        deltas = self.analyst.apply(st, intent, {"deltas": r.get("axis_hints", {})}, (ev or {}).get("stakes", "low"))
        day_adv = False
        for _ in range(min(int(ch.get("time_advance_days", 0) or 0), 3)):
            self._advance_day(st); day_adv = True
        narration = r.get("narration", "...")
        if r.get("npc_reaction"):
            narration += f"\n— {r['npc_reaction']}."
        if ev:
            st.active_event = ev["id"]   # ситуация просто продолжается (никакого меню)
        return StepResult(narration=narration, changes=changes, deltas=deltas,
                          reflection=self.narrator.reflection(st.axes),
                          leads_to=r.get("interpretation"), day_advanced=day_adv,
                          event_id=(ev or {}).get("id"), branch_id="_gm", intent=intent)

    # ---------- «мир откликается на что угодно» (steering к сюжету) ----------
    VERB_HINT = {
        "talk": "поговорить", "persuade": "убедить", "deceive": "схитрить", "threaten": "надавить",
        "bribe": "предложить денег", "beg": "попросить", "befriend": "расположить к себе",
        "ask_help": "попросить помощи", "offer_help": "помочь", "flirt": "сблизиться",
        "apologize": "извиниться", "refuse": "отказаться", "trade": "договориться о деньгах",
        "work": "взяться за работу", "steal": "рискнуть и взять своё", "borrow": "занять",
        "give": "отдать/заплатить", "apply": "оформить", "submit_docs": "показать документы",
        "book_appointment": "искать запись", "inquire_status": "расспросить", "move": "уйти",
        "search": "осмотреться", "flee": "уйти", "hide": "затаиться",
    }

    def _scene_hint(self, ev: dict | None) -> str:
        if not ev:
            return "Осмотрись, перейди куда-то или передохни."
        seen: list[str] = []
        for br in ev.get("branches", []):
            for v in br.get("match", {}).get("verbs", []):
                h = self.VERB_HINT.get(v)
                if h and h not in seen:
                    seen.append(h)
        if not seen:
            return "Реши, как поступить."
        return "Сейчас уместнее: " + ", ".join(seen[:5]) + "."

    def _npc_name(self, ev: dict | None) -> str:
        tid = (ev.get("targets") or [None])[0] if ev else None
        return self.c.npc(tid).get("name", "собеседник") if tid else "собеседник"

    def _loc_groups_of(self, loc: str) -> list[str]:
        return [g for g, members in self.c.loc_groups.items() if loc in members]

    def _pick_loc_text(self, wc: dict, st: GameState) -> str | None:
        byloc = wc.get("by_location", {})
        for g in self._loc_groups_of(st.location):
            if g in byloc:
                return byloc[g]
        return wc.get("default")

    def _fmt(self, s: str, npc: str, place: str, hint: str) -> str:
        try:
            return s.format(npc=npc, place=place, hint=hint).strip()
        except Exception:
            return s

    def _steer(self, st: GameState, ev: dict, intent: dict) -> StepResult:
        verb = intent.get("verb", "")
        if verb == "observe" and intent.get("confidence", 1.0) < 0.4:
            verb = "unknown"
        wc = self.c.wildcards.get(verb)
        hint = self._scene_hint(ev)
        npc = self._npc_name(ev)
        place = self.c.loc_name(st.location)

        base = self._pick_loc_text(wc, st) if wc else None
        if base is None:
            base = ev.get("fallback", {}).get("text")          # своя реплика сцены, если есть
        if base is None:
            base = (self.c.wildcards.get("unknown", {}) or {}).get("default") \
                   or self.c.wild_defaults.get("unknown_reaction", "...")
        steer_tpl = (wc or {}).get("steer") or self.c.wild_defaults.get("steer", "{hint}")
        text = self._fmt(base, npc, place, hint)
        steer = self._fmt(steer_tpl, npc, place, hint)
        narration = text + (("\n" + steer) if steer and steer not in text else "")

        changes, deltas = [], {}
        if wc:
            changes = self.rules.apply_effects(st, ev, wc.get("effects", {}), self.c.economy)
            deltas = self.analyst.apply(st, intent, {"deltas": wc.get("deltas", {})}, ev.get("stakes", "low"))
            for fid in wc.get("followups", []):
                if fid not in st.pending:
                    st.pending.append(fid)

        st.active_event = ev["id"]   # сцена остаётся открытой — ждём настоящего решения
        if self.llm.available:
            try:
                narration = self.narrator.steer(ev, intent, base, hint, (ev.get("targets") or [None])[0])
            except Exception:
                pass
        return StepResult(narration=narration, changes=changes, deltas=deltas,
                          reflection=self.narrator.reflection(st.axes),
                          leads_to="(мир откликнулся; сцена ждёт твоего решения)",
                          event_id=ev["id"], branch_id="_steer", intent=intent)

    def _detect_dest(self, intent: dict) -> str | None:
        raw = intent.get("raw", "").lower()
        for lid, loc in self.c.locations.items():
            name = loc.get("name", "").lower()
            if lid in raw or any(w in raw for w in name.replace("«", " ").replace("»", " ").replace("(", " ").replace(")", " ").split() if len(w) > 3):
                return lid
        return intent.get("props", {}).get("dest")

    def travel(self, st: GameState, dest: str, fare_dodge: bool) -> StepResult:
        if dest not in self.c.locations:
            return StepResult(narration="Такого места нет на карте.")
        notes = []
        if fare_dodge:
            st.set_flag("moved_without_ticket")
            st.location = "ubahn_station"
            notes.append("едешь зайцем")
            reactive = self.rules.pick_forced(st)  # может всплыть контроль
            if reactive and reactive["id"] == "ubahn_control":
                st.active_event = "ubahn_control"  # остаёмся на станции, пока не разрулим
                return StepResult(narration=self.narrator.scene_intro(reactive),
                                  changes=notes, event_id="ubahn_control")
        st.location = dest
        return StepResult(narration=f"Ты перемещаешься: {self.c.loc_name(dest)}.", changes=notes)

    # ---------- ход времени ----------
    def _advance_day(self, st: GameState) -> None:
        eco = self.c.economy.get("daily", {})
        st.day += 1
        st.visa_days -= 1
        st.money -= eco.get("cost_base", 25)
        st.hunger = min(100, st.hunger + eco.get("hunger_per_day", 12))
        st.fatigue = max(0, st.fatigue - 5)         # сон немного восстанавливает
        st.stress = max(0, st.stress - eco.get("stress_decay", 5))
        st.day_action_counts = {}
        # подтянуть отложенные followups в активные (как «продолжения»)
