# LOTM Fanart Organizer

Local-first deterministic fanart organizer with rule-based classification and mobile-friendly review UI.

## Stack
- Python, FastAPI, Jinja2, SQLite
- No external APIs, no AI in core logic

## Setup
```bash
cd lotm-fanart-organizer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run web dashboard
```bash
uvicorn dashboard.app:app --reload --port 8000
```

Open `http://127.0.0.1:8000/settings`:
1. Set import folder path.
2. Save or run ingestion.

## Data model
- `core_tags`: glossary-matched canonical tags only.
- `attribute_tags`: all non-glossary tags.
- Rules use only `core_tags`.

## Reprocess
Use `POST /reprocess` (button on review page) to re-run normalization/splitting/rules deterministically.
