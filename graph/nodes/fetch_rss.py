import os
import logging

import feedparser

from graph.state import State

logger = logging.getLogger(__name__)


def fetch_rss(state: State) -> dict:
    """从 RSS 源获取最新一条消息的 content:encoded 字段。"""
    feed_url = os.environ["RSS_FEED_URL"]
    logger.info("正在获取 RSS: %s", feed_url)

    feed = feedparser.parse(feed_url)
    if not feed.entries:
        raise ValueError("RSS 中没有找到任何条目")

    entry = feed.entries[0]

    # content:encoded -> feedparser 存储在 entry.content 列表中
    content = ""
    if hasattr(entry, "content") and entry.content:
        content = entry.content[0].get("value", "")
    if not content:
        content = entry.get("summary", "")
    if not content:
        content = entry.get("description", "")

    logger.info("获取到条目: %s (内容长度: %d)", entry.get("title", "N/A"), len(content))
    return {"rss_content": content}
