from langgraph.graph import StateGraph, START, END

from graph.state import State
from graph.nodes import fetch_rss, translate_content, convert_to_html, publish_to_pages

graph = StateGraph(State)

graph.add_node("fetch_rss", fetch_rss)
graph.add_node("translate_content", translate_content)
graph.add_node("convert_to_html", convert_to_html)
graph.add_node("publish_to_pages", publish_to_pages)

graph.add_edge(START, "fetch_rss")
graph.add_edge("fetch_rss", "translate_content")
graph.add_edge("translate_content", "convert_to_html")
graph.add_edge("convert_to_html", "publish_to_pages")
graph.add_edge("publish_to_pages", END)

ai_daily_app = graph.compile()
