from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy

from graph.state import State
from graph.nodes import fetch_rss, translate_content, save_to_local

retry_policy = RetryPolicy(
    max_attempts=5,
    initial_interval=60,
    backoff_factor=2,
    max_interval=960,
)

graph = StateGraph(State)

graph.add_node("fetch_rss", fetch_rss, retry=retry_policy)
graph.add_node("translate_content", translate_content, retry=retry_policy)
graph.add_node("save_to_local", save_to_local)

graph.add_edge(START, "fetch_rss")
graph.add_edge("fetch_rss", "translate_content")
graph.add_edge("translate_content", "save_to_local")
graph.add_edge("save_to_local", END)

ai_daily_app = graph.compile()
