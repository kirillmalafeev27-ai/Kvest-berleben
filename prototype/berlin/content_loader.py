"""Загрузка контента (YAML) — данные отдельно от кода (design/05 §5.7)."""
from __future__ import annotations

import os
import re
import glob
import yaml


class Content:
    def __init__(self, root: str):
        self.root = root
        self.economy = self._load("economy.yaml")
        self.verbs_raw = self._load("verbs.yaml")
        self.locations_raw = self._load("locations.yaml")
        self.npcs_raw = self._load("npcs.yaml")
        self.wildcards_raw = self._load("wildcards.yaml")
        self.wildcards: dict = self.wildcards_raw.get("wildcards", {})
        self.wild_defaults: dict = self.wildcards_raw.get("defaults", {})
        self.wild_free: dict = self.wildcards_raw.get("free_roam", {})

        self.verbs: dict = self.verbs_raw.get("verbs", {})
        self.honesty_kw: dict = self.verbs_raw.get("honesty", {})
        self.tone_kw: dict = self.verbs_raw.get("tone", {})
        self.locations: dict = self.locations_raw.get("locations", {})
        self.loc_groups: dict = self.locations_raw.get("groups", {})

        # NPC: базовый файл + все content/npcs/*.yaml (по-линейные)
        self.npcs: dict = dict(self.npcs_raw.get("npcs", {}))
        for path in sorted(glob.glob(os.path.join(root, "npcs", "*.yaml"))):
            data = yaml.safe_load(open(path, encoding="utf-8")) or {}
            self.npcs.update(data.get("npcs", {}))

        # события из всех файлов в content/events/; линия выводится из имени файла
        self.events: dict[str, dict] = {}
        for path in sorted(glob.glob(os.path.join(root, "events", "*.yaml"))):
            stem = os.path.splitext(os.path.basename(path))[0]
            line_id = re.sub(r"_act\d+$", "", stem)  # soiskatel_act2 -> soiskatel
            data = yaml.safe_load(open(path, encoding="utf-8")) or {}
            for ev in data.get("events", []):
                ev.setdefault("line", line_id)
                self.events[ev["id"]] = ev

    def lines(self) -> dict:
        return self.economy.get("lines", {})

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
