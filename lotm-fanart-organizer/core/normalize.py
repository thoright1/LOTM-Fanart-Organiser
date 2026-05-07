from __future__ import annotations

import json
from pathlib import Path


class TagNormalizer:
    def __init__(self, glossary_path: Path) -> None:
        self.glossary_path = glossary_path
        self.alias_to_canonical = self._load_glossary()

    def _load_glossary(self) -> dict[str, str]:
        try:
            raw = json.loads(self.glossary_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raw = {}
        alias_map: dict[str, str] = {}
        for alias, canonical in raw.items():
            if isinstance(alias, str) and isinstance(canonical, str):
                alias_map[alias.strip().lower()] = canonical.strip().lower()
        return alias_map

    def split_tags(self, tags: list[str]) -> tuple[list[str], list[str]]:
        core_tags: set[str] = set()
        attribute_tags: set[str] = set()
        for tag in tags:
            cleaned = str(tag).strip().lower()
            if not cleaned:
                continue
            canonical = self.alias_to_canonical.get(cleaned)
            if canonical:
                core_tags.add(canonical)
            else:
                attribute_tags.add(cleaned)
        return sorted(core_tags), sorted(attribute_tags)
