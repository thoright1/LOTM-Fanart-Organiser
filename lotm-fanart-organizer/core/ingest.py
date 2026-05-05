from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from utils.file_utils import IMAGE_EXTENSIONS


def _extract_tags(meta: dict[str, Any]) -> list[str]:
    raw_tags = meta.get("tags")
    if isinstance(raw_tags, list):
        return [str(tag) for tag in raw_tags]
    if isinstance(raw_tags, str):
        return [raw_tags]

    keywords = meta.get("keywords")
    if isinstance(keywords, list):
        return [str(tag) for tag in keywords]

    return []


def ingest_gallery_dl(source_dir: Path, base_dir: Path) -> list[dict[str, Any]]:
    source_dir = source_dir.resolve()
    records: list[dict[str, Any]] = []

    for image_path in source_dir.rglob("*"):
        if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        metadata_path = image_path.with_suffix(".json")
        if not metadata_path.exists():
            records.append({"image_path": image_path, "filename": image_path.name, "tags": []})
            continue

        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            metadata = {}

        records.append(
            {
                "image_path": image_path,
                "filename": image_path.name,
                "tags": _extract_tags(metadata),
            }
        )

    return records
