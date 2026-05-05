from __future__ import annotations

import argparse
from pathlib import Path

from core.ingest import ingest_gallery_dl
from core.sorter import sort_records

BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="LOTM Fanart Organizer")
    parser.add_argument(
        "--source",
        type=Path,
        default=BASE_DIR / "data" / "raw",
        help="Path to gallery-dl output folder",
    )
    parser.add_argument(
        "--mode",
        choices=["copy", "move"],
        default="copy",
        help="How to place files into sorted folders",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and classify without moving/copying files",
    )
    args = parser.parse_args()

    records = ingest_gallery_dl(source_dir=args.source, base_dir=BASE_DIR)
    result = sort_records(records=records, base_dir=BASE_DIR, mode=args.mode, dry_run=args.dry_run)

    print(f"Processed: {result['processed']}")
    print(f"Sorted: {result['sorted']}")
    print(f"Unsorted: {result['unsorted']}")


if __name__ == "__main__":
    main()
