# LOTM Fanart Organizer

Local-first fanart organizer for gallery-dl collections. It classifies images using deterministic glossary normalization + rules, then provides a lightweight review dashboard.

## Features
- Ingest images and matching metadata JSON from gallery-dl output
- Normalize Chinese/English/variant tags to canonical English via `config/glossary.json`
- Apply subset-based group rules from `config/rules.json`
- Sort to `data/sorted` or `data/unsorted`
- Persist review state in SQLite (`db/images.db`)
- Manual review dashboard (FastAPI)
- Optional AI hook placeholder (`core/ai_helper.py`), never used as core logic

## Setup
```bash
cd lotm-fanart-organizer
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run ingestion + sorting
Put gallery-dl output in `data/raw` (each image should have sibling `.json` metadata when available):

```bash
python run.py --source data/raw --mode copy
```

Options:
- `--mode copy|move` (default: copy)
- `--dry-run` to classify without file operations

## Start review dashboard
```bash
uvicorn dashboard.app:app --reload --port 8000
```

Open: `http://127.0.0.1:8000/`

API endpoints:
- `GET /next` → next pending image
- `POST /decision` with form fields: `filename`, `status`, `normalized_tags`, `assigned_folder`

## Idempotency notes
- Database uses upsert by `filename`.
- Re-running ingestion updates existing records.
- Sorting in copy mode is safe for repeated runs.
