from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from core.db import ImageDB

BASE_DIR = Path(__file__).resolve().parents[1]
DB = ImageDB(BASE_DIR / "db" / "images.db")
app = FastAPI(title="LOTM Fanart Organizer Dashboard")


@app.get("/next")
def get_next() -> dict | None:
    return DB.get_next_pending()


@app.post("/decision")
def post_decision(
    filename: str = Form(...),
    status: str = Form(...),
    normalized_tags: str = Form(""),
    assigned_folder: str = Form("unsorted"),
) -> dict:
    tags = [tag.strip() for tag in normalized_tags.split(",") if tag.strip()]
    DB.update_decision(filename=filename, status=status, normalized_tags=tags, assigned_folder=assigned_folder)
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
<!DOCTYPE html>
<html>
<head><title>LOTM Review Dashboard</title></head>
<body>
  <h1>LOTM Fanart Review</h1>
  <div id="card">Loading...</div>

<script>
async function loadNext() {
  const res = await fetch('/next');
  const item = await res.json();
  const card = document.getElementById('card');
  if (!item) { card.innerHTML = '<p>No pending items.</p>'; return; }

  card.innerHTML = `
    <img src="file://${item.path}" style="max-width: 500px; display:block;" />
    <p><b>Filename:</b> ${item.filename}</p>
    <label>Tags (comma separated)</label><br>
    <input id="tags" style="width:500px" value="${item.normalized_tags.join(', ')}"/><br>
    <label>Folder</label><br>
    <input id="folder" style="width:500px" value="${item.assigned_folder}"/><br><br>
    <button onclick="submitDecision('approved')">Approve</button>
    <button onclick="submitDecision('rejected')">Reject</button>
    <button onclick="loadNext()">Next</button>
  `;
  card.dataset.filename = item.filename;
}

async function submitDecision(status) {
  const filename = document.getElementById('card').dataset.filename;
  const tags = document.getElementById('tags').value;
  const folder = document.getElementById('folder').value;
  const body = new FormData();
  body.append('filename', filename);
  body.append('status', status);
  body.append('normalized_tags', tags);
  body.append('assigned_folder', folder);
  await fetch('/decision', { method: 'POST', body });
  await loadNext();
}

loadNext();
</script>
</body>
</html>
"""
