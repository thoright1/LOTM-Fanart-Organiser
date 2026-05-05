from __future__ import annotations

import json
from pathlib import Path


class RulesEngine:
    def __init__(self, rules_path: Path) -> None:
        raw = json.loads(rules_path.read_text(encoding="utf-8"))
        self.group_rules = raw.get("group_rules", [])
        self.single_tag_folders = raw.get("single_tag_folders", {})

    def assign_folder(self, normalized_tags: list[str]) -> str:
        tag_set = set(normalized_tags)

        for rule in self.group_rules:
            required = set(rule.get("required_tags", []))
            if required and required.issubset(tag_set):
                return rule["name"]

        for tag in normalized_tags:
            if tag in self.single_tag_folders:
                return self.single_tag_folders[tag]

        return "unsorted"
