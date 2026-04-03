import asyncio
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


def _normalize_entries(raw: list) -> list[dict]:
    """将旧格式字符串条目迁移为对象格式。"""
    result = []
    for e in raw:
        if isinstance(e, str):
            result.append({"id": e, "date": e, "title": "AI 每日简报"})
        else:
            result.append(e)
    return result


def get_article_list() -> list[dict]:
    """获取已翻译的文章列表（对象格式）。"""
    index = _read_index()
    return _normalize_entries(index.get("ai-daily", []))


def get_translated_dates() -> list[str]:
    """获取已翻译的日期列表（去重）。"""
    return sorted({a["date"] for a in get_article_list()}, reverse=True)


def get_translated_titles() -> set[str]:
    """获取已翻译的文章标题集合。"""
    return {a["title"] for a in get_article_list()}


async def save_to_local(state: State) -> dict:
    """将 Markdown 内容保存到本地文件。"""
    _ensure_dirs()

    date = state["date"]
    title = state.get("title", "AI 每日简报")
    md_content = state["markdown_content"]

    # 读取索引并迁移旧格式
    index = _read_index()
    entries = _normalize_entries(index.get("ai-daily", []))

    # 计算该日期下一个序号
    same_date = [e for e in entries if e["date"] == date]
    seq = len(same_date) + 1

    article_id = f"{date}_{seq}"
    file_path = ARTICLES_DIR / f"{article_id}.md"
    await asyncio.to_thread(file_path.write_text, md_content, "utf-8")

    # 插入新条目并按日期降序排序
    entries.insert(0, {"id": article_id, "date": date, "title": title})
    entries.sort(key=lambda e: e["date"], reverse=True)

    index["ai-daily"] = entries
    _write_index(index)

    logger.info("已保存 ai-daily %s (%s) 到本地", article_id, title)
    return {}
