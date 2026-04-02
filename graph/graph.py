from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy

from graph.state import State
from graph.nodes import fetch_rss, translate_content, convert_to_html, publish_to_pages

retry_policy = RetryPolicy(
    max_attempts=5,
    initial_interval=60,
    backoff_factor=2,
    max_interval=960,
)

graph = StateGraph(State)

graph.add_node("fetch_rss", fetch_rss, retry=retry_policy)
graph.add_node("translate_content", translate_content, retry=retry_policy)
graph.add_node("convert_to_html", convert_to_html)
graph.add_node("publish_to_pages", publish_to_pages, retry=retry_policy)

graph.add_edge(START, "fetch_rss")
graph.add_edge("fetch_rss", "translate_content")
graph.add_edge("translate_content", "convert_to_html")
graph.add_edge("convert_to_html", "publish_to_pages")
graph.add_edge("publish_to_pages", END)

ai_daily_app = graph.compile()
