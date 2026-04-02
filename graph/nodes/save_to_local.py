import json
import os
import logging
from pathlib import Path

from graph.state import State

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))
ARTICLES_DIR = DATA_DIR / "articles"
INDEX_PATH = DATA_DIR / "index.json"


def _ensure_dirs():
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)


def _read_index() -> dict:
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return {"ai-daily": []}


def _write_index(data: dict):
    INDEX_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def get_translated_dates() -> list[str]:
    """获取已翻译的日期列表。"""
    index = _read_index()
    return index.get("ai-daily", [])


def save_to_local(state: State) -> dict:
    """将 Markdown 内容保存到本地文件。"""
    _ensure_dirs()

    date = state["date"]
    md_content = state["markdown_content"]

    file_path = ARTICLES_DIR / f"{date}.md"
    file_path.write_text(md_content, encoding="utf-8")

    # 更新 index.json
    index = _read_index()
    dates = index.setdefault("ai-daily", [])
    if date not in dates:
        dates.insert(0, date)
        dates.sort(reverse=True)
    _write_index(index)

    logger.info("已保存 ai-daily %s 到本地", date)
    return {}
