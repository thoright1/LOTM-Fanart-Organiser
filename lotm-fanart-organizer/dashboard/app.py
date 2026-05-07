from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from core.db import ImageDB
from core.ingest import ingest_gallery_dl
from core.normalize import TagNormalizer
from core.rules_engine import RulesEngine
from core.settings import SettingsManager
from core.sorter import sort_records

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE_DIR / "config"
DB = ImageDB(BASE_DIR / "db" / "images.db")
SETTINGS = SettingsManager(CONFIG_DIR / "settings.json")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app = FastAPI(title="LOTM Fanart Organizer")


def _load_glossary() -> dict[str, str]:
    try:
        return json.loads((CONFIG_DIR / "glossary.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_glossary(data: dict[str, str]) -> None:
    (CONFIG_DIR / "glossary.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_rules() -> list[dict]:
    try:
        raw = json.loads((CONFIG_DIR / "rules.json").read_text(encoding="utf-8"))
        return raw if isinstance(raw, list) else []
    except (OSError, json.JSONDecodeError):
        return []


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/next", status_code=302)


@app.get("/next")
def next_review(request: Request):
    item = DB.get_next_pending()
    return templates.TemplateResponse("review.html", {"request": request, "item": item, "glossary": sorted(set(_load_glossary().values()))})


@app.post("/review")
def review(image_id: int = Form(...), core_tags: str = Form(""), assigned_folder: str = Form("unsorted"), status: str = Form(...)):
    tags = sorted({t.strip().lower() for t in core_tags.split(",") if t.strip()})
    DB.update_review(image_id, tags, assigned_folder.strip() or "unsorted", status)
    return RedirectResponse(url="/next", status_code=303)


@app.get("/settings")
def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request, "settings": SETTINGS.load()})


@app.post("/settings/update")
def update_settings(import_dir: str = Form(...), run_ingestion: str = Form("0")):
    s = SETTINGS.update_import_dir(import_dir)
    if run_ingestion == "1" and s.get("current_import_dir"):
        source = Path(s["current_import_dir"]).expanduser()
        records = ingest_gallery_dl(source)
        sort_records(records, BASE_DIR, str(source), mode="copy", dry_run=False)
    return RedirectResponse(url="/settings", status_code=303)


@app.get("/glossary")
def glossary_page(request: Request):
    return templates.TemplateResponse("glossary.html", {"request": request, "glossary": _load_glossary()})


@app.post("/glossary/add")
def glossary_add(raw_tag: str = Form(...), canonical_tag: str = Form(...)):
    g = _load_glossary()
    if raw_tag.strip() and canonical_tag.strip():
        g[raw_tag.strip()] = canonical_tag.strip().lower()
        _save_glossary(g)
    return RedirectResponse(url="/glossary", status_code=303)


@app.get("/rules")
def rules_page(request: Request):
    return templates.TemplateResponse("rules.html", {"request": request, "rules": _load_rules()})


@app.post("/rules/add")
def rules_add(tags: str = Form(...), folder: str = Form(...)):
    rules = _load_rules()
    parsed_tags = [t.strip().lower() for t in tags.split(",") if t.strip()]
    if parsed_tags and folder.strip():
        rules.append({"tags": parsed_tags, "folder": folder.strip()})
        (CONFIG_DIR / "rules.json").write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")
    return RedirectResponse(url="/rules", status_code=303)


@app.post("/reprocess")
def reprocess():
    pending = DB.all_pending()
    normalizer = TagNormalizer(CONFIG_DIR / "glossary.json")
    rules = RulesEngine(CONFIG_DIR / "rules.json")
    for item in pending:
        combined = item["core_tags"] + item["attribute_tags"]
        core_tags, attribute_tags = normalizer.split_tags(combined)
        folder = rules.assign_folder(core_tags)
        DB.upsert_image(item["filename"], item["path"], core_tags, attribute_tags, folder, item["status"], item["source_folder"])
    return RedirectResponse(url="/next", status_code=303)
