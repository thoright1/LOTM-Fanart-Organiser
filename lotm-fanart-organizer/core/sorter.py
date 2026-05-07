from __future__ import annotations

import shutil
from pathlib import Path

from core.db import ImageDB
from core.normalize import TagNormalizer
from core.rules_engine import RulesEngine


def sort_records(records: list[dict], base_dir: Path, source_folder: str, mode: str = "copy", dry_run: bool = False) -> dict[str, int]:
    db = ImageDB(base_dir / "db" / "images.db")
    normalizer = TagNormalizer(base_dir / "config" / "glossary.json")
    rules = RulesEngine(base_dir / "config" / "rules.json")
    counts = {"processed": 0, "sorted": 0, "unsorted": 0}

    for record in records:
        counts["processed"] += 1
        src = Path(record["image_path"])
        core_tags, attribute_tags = normalizer.split_tags(record.get("tags", []))
        folder = rules.assign_folder(core_tags)
        target_root = base_dir / "data" / ("unsorted" if folder == "unsorted" else f"sorted/{folder}")
        target_root.mkdir(parents=True, exist_ok=True)
        target = target_root / src.name
        if not dry_run:
            if mode == "move":
                if src.resolve() != target.resolve():
                    shutil.move(str(src), str(target))
            else:
                shutil.copy2(src, target)
        db.upsert_image(src.name, str(target), core_tags, attribute_tags, folder, "pending", source_folder)
        counts["unsorted" if folder == "unsorted" else "sorted"] += 1
    return counts
