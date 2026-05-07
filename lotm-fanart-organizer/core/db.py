from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class ImageDB:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    path TEXT UNIQUE NOT NULL,
                    core_tags TEXT NOT NULL,
                    attribute_tags TEXT NOT NULL,
                    assigned_folder TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected')),
                    source_folder TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def upsert_image(self, filename: str, path: str, core_tags: list[str], attribute_tags: list[str], assigned_folder: str, status: str, source_folder: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO images (filename, path, core_tags, attribute_tags, assigned_folder, status, source_folder)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    filename=excluded.filename,
                    core_tags=excluded.core_tags,
                    attribute_tags=excluded.attribute_tags,
                    assigned_folder=excluded.assigned_folder,
                    status=excluded.status,
                    source_folder=excluded.source_folder,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (filename, path, json.dumps(core_tags, ensure_ascii=False), json.dumps(attribute_tags, ensure_ascii=False), assigned_folder, status, source_folder),
            )

    def get_next_pending(self) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM images WHERE status='pending' ORDER BY id ASC LIMIT 1").fetchone()
        if not row:
            return None
        item = dict(row)
        item["core_tags"] = json.loads(item["core_tags"])
        item["attribute_tags"] = json.loads(item["attribute_tags"])
        return item

    def update_review(self, image_id: int, core_tags: list[str], assigned_folder: str, status: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE images SET core_tags=?, assigned_folder=?, status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (json.dumps(core_tags, ensure_ascii=False), assigned_folder, status, image_id),
            )

    def all_pending(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM images WHERE status='pending'").fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["core_tags"] = json.loads(d["core_tags"])
            d["attribute_tags"] = json.loads(d["attribute_tags"])
            out.append(d)
        return out
