from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from core.ai_helper import ai_predict
from core.db import ImageDB
from core.normalize import TagNormalizer
from core.rules_engine import RulesEngine


def sort_records(records: list[dict[str, Any]], base_dir: Path, mode: str = "copy", dry_run: bool = False) -> dict[str, int]:
    normalizer = TagNormalizer(base_dir / "config" / "glossary.json")
    rules_engine = RulesEngine(base_dir / "config" / "rules.json")
    db = ImageDB(base_dir / "db" / "images.db")

    counts = {"processed": 0, "sorted": 0, "unsorted": 0}

    for record in records:
        counts["processed"] += 1
        image_path: Path = record["image_path"]
        normalized_tags = normalizer.normalize(record["tags"])
        assigned_folder = rules_engine.assign_folder(normalized_tags)

        if assigned_folder == "unsorted":
            ai_result = ai_predict(image_path)
            if ai_result:
                _, _ = ai_result
            destination_root = base_dir / "data" / "unsorted"
        else:
            destination_root = base_dir / "data" / "sorted" / assigned_folder

        destination_root.mkdir(parents=True, exist_ok=True)
        destination_path = destination_root / image_path.name

        if not dry_run:
            if mode == "copy":
                shutil.copy2(image_path, destination_path)
            else:
                shutil.move(image_path, destination_path)

        db.upsert_image(
            filename=record["filename"],
            path=str(destination_path),
            normalized_tags=normalized_tags,
            assigned_folder=assigned_folder,
            status="pending",
        )

        if assigned_folder == "unsorted":
            counts["unsorted"] += 1
        else:
            counts["sorted"] += 1

    return counts
