import logging

import markdown as md

from graph.state import State

logger = logging.getLogger(__name__)


def convert_to_html(state: State) -> dict:
    """将 Markdown 转换为带样式的 HTML 邮件。"""
    html_body = md.markdown(
        state["markdown_content"],
        extensions=["extra", "nl2br", "sane_lists"],
    )

    html = f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                   "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      line-height: 1.8;
      color: #333;
      background-color: #fafafa;
    }}
    h1 {{ color: #1a1a1a; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; }}
    h2 {{ color: #2c3e50; margin-top: 28px; }}
    h3 {{ color: #34495e; margin-top: 16px; }}
    blockquote {{
      border-left: 4px solid #3498db;
      margin: 16px 0;
      padding: 8px 16px;
      background: #eaf2f8;
      color: #2c3e50;
    }}
    a {{ color: #2980b9; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    hr {{ border: none; border-top: 1px solid #e0e0e0; margin: 24px 0; }}
    ul {{ padding-left: 20px; }}
    li {{ margin-bottom: 12px; }}
  </style>
</head>
<body>
{html_body}
</body>
</html>"""

    logger.info("Markdown 已转换为 HTML")
    return {"html_content": html}
