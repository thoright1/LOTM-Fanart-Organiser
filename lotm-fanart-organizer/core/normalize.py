from __future__ import annotations

import json
from pathlib import Path


class TagNormalizer:
    def __init__(self, glossary_path: Path) -> None:
        raw_glossary = json.loads(glossary_path.read_text(encoding="utf-8"))
        self.alias_to_canonical = self._build_alias_map(raw_glossary)

    @staticmethod
    def _build_alias_map(glossary: dict[str, list[str]]) -> dict[str, str]:
        alias_map: dict[str, str] = {}
        for canonical, aliases in glossary.items():
            alias_map[canonical.strip().lower()] = canonical
            for alias in aliases:
                alias_map[alias.strip().lower()] = canonical
        return alias_map

    def normalize(self, tags: list[str]) -> list[str]:
        normalized = {self.alias_to_canonical.get(tag.strip().lower(), tag.strip().lower()) for tag in tags if tag.strip()}
        return sorted(normalized)
