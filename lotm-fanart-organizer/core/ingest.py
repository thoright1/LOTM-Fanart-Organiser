from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from utils.file_utils import IMAGE_EXTENSIONS


def _extract_tags(meta: dict[str, Any]) -> list[str]:
    for key in ("tags", "keywords", "tag_string"):
        val = meta.get(key)
        if isinstance(val, list):
            return [str(x) for x in val]
        if isinstance(val, str):
            return [v.strip() for v in val.split(",") if v.strip()]
    return []


def ingest_gallery_dl(source_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not source_dir.exists() or not source_dir.is_dir():
        return records
    for image_path in source_dir.rglob("*"):
        if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        meta_path = image_path.with_suffix(".json")
        try:
            metadata = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        except (OSError, json.JSONDecodeError):
            metadata = {}
        records.append({"image_path": image_path, "filename": image_path.name, "tags": _extract_tags(metadata)})
    return records
