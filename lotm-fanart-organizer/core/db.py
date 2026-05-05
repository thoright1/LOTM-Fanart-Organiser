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
                    filename TEXT PRIMARY KEY,
                    path TEXT NOT NULL,
                    normalized_tags TEXT NOT NULL,
                    assigned_folder TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected')),
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def upsert_image(
        self,
        filename: str,
        path: str,
        normalized_tags: list[str],
        assigned_folder: str,
        status: str = "pending",
    ) -> None:
        payload = (filename, path, json.dumps(normalized_tags, ensure_ascii=False), assigned_folder, status)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO images (filename, path, normalized_tags, assigned_folder, status)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(filename) DO UPDATE SET
                    path=excluded.path,
                    normalized_tags=excluded.normalized_tags,
                    assigned_folder=excluded.assigned_folder,
                    status=excluded.status,
                    updated_at=CURRENT_TIMESTAMP
                """,
                payload,
            )

    def get_next_pending(self) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT filename, path, normalized_tags, assigned_folder, status FROM images WHERE status='pending' ORDER BY updated_at ASC LIMIT 1"
            ).fetchone()
        if row is None:
            return None
        data = dict(row)
        data["normalized_tags"] = json.loads(data["normalized_tags"])
        return data

    def update_decision(
        self,
        filename: str,
        status: str,
        normalized_tags: list[str],
        assigned_folder: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE images
                SET status=?, normalized_tags=?, assigned_folder=?, updated_at=CURRENT_TIMESTAMP
                WHERE filename=?
                """,
                (status, json.dumps(normalized_tags, ensure_ascii=False), assigned_folder, filename),
            )
