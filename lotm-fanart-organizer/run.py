from __future__ import annotations

from pathlib import Path

from core.ingest import ingest_gallery_dl
from core.settings import SettingsManager
from core.sorter import sort_records

BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    settings = SettingsManager(BASE_DIR / "config" / "settings.json").load()
    current = settings.get("current_import_dir")
    if not current:
        print("No current_import_dir set. Configure via /settings UI.")
        return
    source = Path(current).expanduser()
    records = ingest_gallery_dl(source)
    result = sort_records(records, BASE_DIR, str(source), mode="copy", dry_run=False)
    print(result)


if __name__ == "__main__":
    main()
