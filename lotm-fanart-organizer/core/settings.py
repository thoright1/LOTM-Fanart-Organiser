from __future__ import annotations

import json
from pathlib import Path

DEFAULT_SETTINGS = {
    "current_import_dir": None,
    "recent_import_dirs": [],
}


class SettingsManager:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save(DEFAULT_SETTINGS)

    def load(self) -> dict:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = DEFAULT_SETTINGS.copy()
        data.setdefault("current_import_dir", None)
        data.setdefault("recent_import_dirs", [])
        if not isinstance(data["recent_import_dirs"], list):
            data["recent_import_dirs"] = []
        return data

    def save(self, settings: dict) -> None:
        self.path.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")

    def update_import_dir(self, import_dir: str) -> dict:
        settings = self.load()
        cleaned = import_dir.strip()
        settings["current_import_dir"] = cleaned or None
        if cleaned:
            recents = [d for d in settings["recent_import_dirs"] if d != cleaned]
            recents.insert(0, cleaned)
            settings["recent_import_dirs"] = recents[:10]
        self.save(settings)
        return settings
