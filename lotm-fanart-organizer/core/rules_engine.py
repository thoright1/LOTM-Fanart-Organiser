from __future__ import annotations

import json
from pathlib import Path


class RulesEngine:
    def __init__(self, rules_path: Path) -> None:
        try:
            raw = json.loads(rules_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raw = []
        self.rules: list[dict[str, object]] = raw if isinstance(raw, list) else []

    def assign_folder(self, core_tags: list[str]) -> str:
        tag_set = set(core_tags)
        for rule in self.rules:
            required = set(rule.get("tags", []))
            folder = rule.get("folder")
            if required and required.issubset(tag_set) and isinstance(folder, str):
                return folder
        return "unsorted"
