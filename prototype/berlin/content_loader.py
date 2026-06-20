"""Загрузка контента (YAML) — данные отдельно от кода (design/05 §5.7)."""
from __future__ import annotations

import os
import glob
import yaml


class Content:
    def __init__(self, root: str):
        self.root = root
        self.economy = self._load("economy.yaml")
        self.verbs_raw = self._load("verbs.yaml")
        self.locations_raw = self._load("locations.yaml")
        self.npcs_raw = self._load("npcs.yaml")

        self.verbs: dict = self.verbs_raw.get("verbs", {})
        self.honesty_kw: dict = self.verbs_raw.get("honesty", {})
        self.tone_kw: dict = self.verbs_raw.get("tone", {})
        self.locations: dict = self.locations_raw.get("locations", {})
        self.loc_groups: dict = self.locations_raw.get("groups", {})
        self.npcs: dict = self.npcs_raw.get("npcs", {})

        # события из всех файлов в content/events/
        self.events: dict[str, dict] = {}
        for path in sorted(glob.glob(os.path.join(root, "events", "*.yaml"))):
            data = yaml.safe_load(open(path, encoding="utf-8")) or {}
            for ev in data.get("events", []):
                self.events[ev["id"]] = ev

    def _load(self, name: str) -> dict:
        path = os.path.join(self.root, name)
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    # --- удобные геттеры ---
    def npc(self, npc_id: str) -> dict:
        return self.npcs.get(npc_id, {"name": npc_id, "register": "", "tics": []})

    def loc_name(self, loc_id: str) -> str:
        return self.locations.get(loc_id, {}).get("name", loc_id)

    def loc_connects(self, loc_id: str) -> list[str]:
        return self.locations.get(loc_id, {}).get("connects", [])

    def group_members(self, name: str) -> list[str]:
        return self.loc_groups.get(name, [name])
