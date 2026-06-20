"""Игровое состояние + персист в SQLite (stdlib)."""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field, asdict
from typing import Any


AXES = ["G", "T", "A", "L", "P"]  # AGGRO, TRUTH, ALTRU, LAW, PRIDE


@dataclass
class GameState:
    name: str = "Алекс"
    line: str = "soiskatel"
    day: int = 1
    time_of_day: str = "morning"        # morning | day | evening | night
    location: str = "hostel_komet"
    money: int = 1400
    visa_days: int = 90

    hunger: int = 0
    stress: int = 0
    fatigue: int = 0

    axes: dict[str, int] = field(default_factory=lambda: {a: 0 for a in AXES})
    skills: dict[str, int] = field(default_factory=dict)

    flags: list[str] = field(default_factory=list)          # множество (как list для JSON)
    counters: dict[str, int] = field(default_factory=dict)
    faction: dict[str, int] = field(default_factory=dict)
    leanings: dict[str, int] = field(default_factory=dict)
    rumors: list[dict] = field(default_factory=list)        # {tag, faction, intensity, day}
    dossier: list[str] = field(default_factory=list)        # заметки чиновников (общее дело)

    fired_events: list[str] = field(default_factory=list)   # once-события, уже сыгранные
    cooldowns: dict[str, int] = field(default_factory=dict) # event_id -> день, до которого нельзя
    pending: list[str] = field(default_factory=list)        # очередь followups
    active_event: str | None = None                          # открытое событие (ждёт валидного интента)

    day_action_counts: dict[str, int] = field(default_factory=dict)  # antifarm, сброс посуточно
    seed: int = 12345
    turn: int = 0

    # ---- множество-подобный доступ к флагам ----
    def has(self, flag: str) -> bool:
        return flag in self.flags

    def set_flag(self, flag: str) -> None:
        if flag not in self.flags:
            self.flags.append(flag)

    def unset_flag(self, flag: str) -> None:
        if flag in self.flags:
            self.flags.remove(flag)

    def axis(self, a: str) -> int:
        return self.axes.get(a, 0)

    def skill(self, s: str) -> int:
        return self.skills.get(s, 0)

    # ---- сериализация ----
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GameState":
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in d.items() if k in known})


class SaveStore:
    """Простое хранилище сейвов и журнала событий в SQLite."""

    def __init__(self, path: str = "berlin_save.sqlite"):
        self.path = path
        self.con = sqlite3.connect(path)
        self.con.execute(
            "CREATE TABLE IF NOT EXISTS saves "
            "(slot TEXT PRIMARY KEY, state TEXT, updated_at REAL)"
        )
        self.con.execute(
            "CREATE TABLE IF NOT EXISTS event_log "
            "(id INTEGER PRIMARY KEY AUTOINCREMENT, slot TEXT, turn INT, day INT, "
            " location TEXT, event TEXT, intent TEXT, branch TEXT, outcome TEXT, seed INT, ts REAL)"
        )
        self.con.commit()

    def save(self, state: GameState, slot: str = "auto") -> None:
        self.con.execute(
            "INSERT INTO saves(slot, state, updated_at) VALUES(?,?,?) "
            "ON CONFLICT(slot) DO UPDATE SET state=excluded.state, updated_at=excluded.updated_at",
            (slot, json.dumps(state.to_dict(), ensure_ascii=False), time.time()),
        )
        self.con.commit()

    def load(self, slot: str = "auto") -> GameState | None:
        row = self.con.execute("SELECT state FROM saves WHERE slot=?", (slot,)).fetchone()
        if not row:
            return None
        return GameState.from_dict(json.loads(row[0]))

    def log_event(self, state: GameState, slot: str, event: str, intent: str,
                  branch: str, outcome: str, seed: int) -> None:
        self.con.execute(
            "INSERT INTO event_log(slot,turn,day,location,event,intent,branch,outcome,seed,ts) "
            "VALUES(?,?,?,?,?,?,?,?,?,?)",
            (slot, state.turn, state.day, state.location, event, intent, branch, outcome, seed, time.time()),
        )
        self.con.commit()

    def close(self) -> None:
        self.con.close()
