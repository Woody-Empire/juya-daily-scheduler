import logging

import markdown as md

from graph.state import State

logger = logging.getLogger(__name__)


def convert_to_html(state: State) -> dict:
    """将 Markdown 转换为 HTML 片段，用于 GitHub Pages 发布。"""
    html_body = md.markdown(
        state["markdown_content"],
        extensions=["extra", "nl2br", "sane_lists"],
    )

    logger.info("Markdown 已转换为 HTML 片段")
    return {"html_content": html_body}
