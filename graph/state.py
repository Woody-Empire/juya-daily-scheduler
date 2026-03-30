from typing import TypedDict


class State(TypedDict):
    rss_content: str
    markdown_content: str
    html_content: str
    subject: str
