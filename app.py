import logging
import threading
import uuid
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

from graph import ai_daily_app
from graph.nodes.fetch_rss import fetch_rss_entries
from graph.nodes.save_to_local import get_translated_dates, ARTICLES_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BJT = timezone(timedelta(hours=8))

app = FastAPI(title="Juya AI Daily")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Task Manager ---
tasks: dict[str, dict] = {}
tasks_lock = threading.Lock()


def _run_translate_task(task_id: str, entry: dict):
    with tasks_lock:
        tasks[task_id]["status"] = "running"
    try:
        ai_daily_app.invoke({
            "rss_content": entry["content"],
            "date": entry["published"],
        })
        with tasks_lock:
            tasks[task_id]["status"] = "completed"
        logger.info("翻译完成: %s", entry["title"])
    except Exception as e:
        with tasks_lock:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = str(e)
        logger.error("翻译失败 %s: %s", entry["title"], e)


class TranslateRequest(BaseModel):
    since: str
    selected_indices: list[int]


@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("static/index.html")


@app.get("/api/rss/pending")
async def get_pending_entries(since: str | None = None):
    if since is None:
        since = datetime.now(BJT).strftime("%Y-%m-%d")

    entries = fetch_rss_entries(since=since)
    translated = set(get_translated_dates())

    with tasks_lock:
        translating = {t["date"] for t in tasks.values() if t["status"] in ("pending", "running")}

    result = []
    for e in entries:
        status = None
        if e["published"] in translated:
            status = "translated"
        elif e["published"] in translating:
            status = "translating"
        result.append({
            "index": e["index"],
            "title": e["title"],
            "published": e["published"],
            "summary": e["summary"],
            "status": status,
        })
    return result


@app.post("/api/translate")
async def translate_entries(req: TranslateRequest):
    all_entries = fetch_rss_entries(since=req.since)
    translated = set(get_translated_dates())

    pending = [e for e in all_entries if e["published"] not in translated]
    selected = [e for e in pending if e["index"] in req.selected_indices]

    task_ids = []
    for entry in selected:
        task_id = uuid.uuid4().hex[:8]
        with tasks_lock:
            tasks[task_id] = {
                "id": task_id,
                "title": entry["title"],
                "date": entry["published"],
                "status": "pending",
            }
        thread = threading.Thread(target=_run_translate_task, args=(task_id, entry), daemon=True)
        thread.start()
        task_ids.append(task_id)

    return {"task_ids": task_ids}


@app.get("/api/tasks")
async def list_tasks():
    with tasks_lock:
        return list(tasks.values())


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    with tasks_lock:
        task = tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        if task["status"] in ("pending", "running"):
            raise HTTPException(status_code=400, detail="任务进行中，无法删除")
        del tasks[task_id]
    return {"ok": True}


@app.get("/api/articles")
async def list_articles():
    return get_translated_dates()


@app.get("/api/articles/{date}")
async def get_article(date: str):
    file_path = ARTICLES_DIR / f"{date}.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文章不存在")
    return {"markdown": file_path.read_text(encoding="utf-8")}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
