"""CLI — текстовый интерфейс прототипа.

Интерактив: запускай `python play.py`. Команды: /look /me /map /goto <loc> /save /load
/debug /help /quit. Любой иной ввод — свободное действие (парсится в интент).
Скрипт-режим: `python play.py --script file.txt` (по строке на ход) — для автотестов.
"""
from __future__ import annotations

import sys

from .content_loader import Content
from .engine import Engine
from .state import GameState, SaveStore
from .llm import LLM


BAR = "─" * 64


class CLI:
    def __init__(self, content_root: str, save_path: str = "berlin_save.sqlite",
                 force_stub: bool = False, debug: bool = False, seed: int = 12345,
                 line: str = "soiskatel"):
        self.content = Content(content_root)
        self.llm = LLM(force_stub=force_stub)
        self.engine = Engine(self.content, self.llm)
        self.store = SaveStore(save_path)
        self.debug = debug
        self.seed = seed
        self.line = line
        self.st: GameState | None = None
        self._shown_scene: str | None = None

    # ---------- вывод ----------
    def out(self, *a):
        print(*a)

    def status_line(self, st: GameState) -> str:
        return (f"[День {st.day} · €{st.money} · {st.clock_label} {st.visa_days}д · "
                f"📍{self.content.loc_name(st.location)}]")

    def show_scene(self, ev) -> None:
        if ev and ev["id"] != self._shown_scene:
            self.out("\n" + BAR)
            self.out(self.engine.narrator.scene_intro(ev))
            self._shown_scene = ev["id"]

    def show_result(self, res) -> None:
        self.out("\n» " + res.narration)
        if res.changes:
            self.out("   · " + " · ".join(res.changes))
        if self.debug:
            if res.deltas:
                self.out("   · оси: " + ", ".join(f"{k}{v:+d}" for k, v in res.deltas.items()))
            if res.leads_to:
                self.out(f"   · ведёт к: {res.leads_to}")
            if res.intent:
                i = res.intent
                self.out(f"   · интент: {i['verb']}/{i.get('method')} honesty={i.get('honesty')} "
                         f"tone={i.get('tone')} conf={i.get('confidence')}")
        if res.reflection:
            self.out("   " + res.reflection)
        if res.day_advanced:
            self.out("\n" + BAR + f"\n   ☀  {self.status_line(self.st)}")

    # ---------- команды ----------
    def handle_command(self, line: str) -> bool:
        """Возвращает True, если это была мета-команда."""
        if not line.startswith("/"):
            return False
        parts = line.split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1].strip() if len(parts) > 1 else ""
        st = self.st
        if cmd in ("/quit", "/exit", "/q"):
            self.out("Пока. (автосейв)"); self.store.save(st, "auto"); raise SystemExit(0)
        elif cmd == "/help":
            self.out("Команды: /look /me /map /goto <loc> /save /load /debug /help /quit\n"
                     "Иначе — пиши действие словами: «осмотреться», «иду к Бюргерамту», "
                     "«честно объясняю чиновнице ситуацию», «плачу 60», «бегу»...")
        elif cmd == "/look":
            self.out(self.engine._free_action(st, {"verb": "observe", "raw": ""}).narration)
        elif cmd == "/me":
            self.out(self.engine._free_action(st, {"verb": "inspect_self", "raw": ""}).narration)
        elif cmd == "/map":
            here = self.content.loc_connects(st.location)
            self.out("Соседние локации:")
            for lid in here:
                self.out(f"  /goto {lid}  — {self.content.loc_name(lid)}")
        elif cmd in ("/next", "/sleep", "/endday"):
            self.engine._advance_day(st); self._shown_scene = None
            self.out(f"☀  Новый день. {self.status_line(st)}")
        elif cmd == "/goto":
            res = self.engine.travel(st, arg, fare_dodge=False)
            self._shown_scene = None
            self.out("» " + res.narration)
        elif cmd == "/save":
            self.store.save(st, arg or "manual"); self.out("Сохранено.")
        elif cmd == "/load":
            loaded = self.store.load(arg or "manual")
            if loaded:
                self.st = loaded; self._shown_scene = None; self.out("Загружено.")
            else:
                self.out("Сейв не найден.")
        elif cmd == "/debug":
            self.debug = not self.debug
            self.out(f"debug = {self.debug}")
            if self.debug:
                self.out("   оси: " + ", ".join(f"{k}={v}" for k, v in st.axes.items()))
                self.out("   склонности: " + str(st.leanings) + " | репутация: " + str(st.faction))
        else:
            self.out("Неизвестная команда. /help")
        return True

    # ---------- циклы ----------
    def turn(self, line: str) -> None:
        ev = self.engine.current_scene(self.st)
        self.show_scene(ev)
        if self.handle_command(line):
            return
        res = self.engine.step(self.st, line, ev)
        self.show_result(res)
        self.store.save(self.st, "auto")

    def run_interactive(self, load: str | None = None) -> None:
        self.st = self.store.load(load) if load else None
        if not self.st:
            self.st = self.engine.new_game(seed=self.seed, line=self.line)
        self.out(f"BERLIN: ÜBERLEBEN — прототип (LLM: {self.llm.mode}). /help для команд.")
        while True:
            ev = self.engine.current_scene(self.st)
            self.show_scene(ev)
            try:
                line = input(f"\n{self.status_line(self.st)}\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                self.out("\nПока. (автосейв)"); self.store.save(self.st, "auto"); return
            if not line:
                continue
            if self.handle_command(line):
                continue
            res = self.engine.step(self.st, line, ev)
            self.show_result(res)
            self.store.save(self.st, "auto")

    def run_script(self, lines: list[str]) -> None:
        self.st = self.engine.new_game(seed=self.seed, line=self.line)
        self.out(f"BERLIN: ÜBERLEBEN — скрипт-прогон (LLM: {self.llm.mode}).")
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            self.out(f"\n{self.status_line(self.st)}")
            self.out(f"> {line}")
            ev = self.engine.current_scene(self.st)
            self.show_scene(ev)
            if self.handle_command(line):
                continue
            res = self.engine.step(self.st, line, ev)
            self.show_result(res)
        self.out("\n" + BAR + "\nИтог прогона:")
        self.out(self.engine._free_action(self.st, {"verb": "inspect_self", "raw": ""}).narration)
        self.out("оси: " + ", ".join(f"{k}={v}" for k, v in self.st.axes.items()))
        self.out("флаги: " + ", ".join(self.st.flags))
        self.out("дело: " + ("; ".join(self.st.dossier) or "—"))
