import asyncio
import os
import logging
from datetime import datetime, timezone, timedelta

import feedparser

from graph.state import State

logger = logging.getLogger(__name__)

BJT = timezone(timedelta(hours=8))


def _parse_published(entry) -> str | None:
    """从 RSS 条目中解析发布日期，返回 YYYY-MM-DD 格式。"""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(BJT).strftime("%Y-%m-%d")
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc).astimezone(BJT).strftime("%Y-%m-%d")
    return None


def _extract_content(entry) -> str:
    """提取 RSS 条目的正文内容。"""
    content = ""
    if hasattr(entry, "content") and entry.content:
        content = entry.content[0].get("value", "")
    if not content:
        content = entry.get("summary", "")
    if not content:
        content = entry.get("description", "")
    return content


def _extract_summary(entry, max_len: int = 200) -> str:
    """提取摘要片段，用于前端展示。"""
    text = entry.get("summary", "") or entry.get("description", "")
    # 去除 HTML 标签的简易处理
    import re
    text = re.sub(r"<[^>]+>", "", text)
    return text[:max_len] + ("..." if len(text) > max_len else "")


def fetch_rss_entries(since: str | None = None) -> list[dict]:
    """获取 RSS 所有条目，可按起始日期过滤。

    Args:
        since: 起始日期 YYYY-MM-DD，只返回 >= 该日期的条目。默认 None 表示不过滤。

    Returns:
        条目列表，每条包含 index, title, published, summary, content。
    """
    feed_url = os.environ["RSS_FEED_URL"]
    logger.info("正在获取 RSS: %s", feed_url)

    feed = feedparser.parse(feed_url)
    if not feed.entries:
        return []

    entries = []
    for i, entry in enumerate(feed.entries):
        published = _parse_published(entry)
        if since and published and published < since:
            continue
        entries.append({
            "index": i,
            "title": entry.get("title", "无标题"),
            "published": published or "未知日期",
            "summary": _extract_summary(entry),
            "content": _extract_content(entry),
        })

    logger.info("获取到 %d 条条目（since=%s）", len(entries), since)
    return entries


async def fetch_rss(state: State) -> dict:
    """从 RSS 源获取指定条目的内容（用于 LangGraph 流水线）。"""
    content = state.get("rss_content", "")
    if content:
        return {"rss_content": content}

    feed_url = os.environ["RSS_FEED_URL"]
    feed = await asyncio.to_thread(feedparser.parse, feed_url)
    if not feed.entries:
        raise ValueError("RSS 中没有找到任何条目")

    entry = feed.entries[0]
    content = _extract_content(entry)
    published = _parse_published(entry)
    logger.info("获取到条目: %s (内容长度: %d)", entry.get("title", "N/A"), len(content))
    return {"rss_content": content, "date": published or datetime.now(BJT).strftime("%Y-%m-%d")}
