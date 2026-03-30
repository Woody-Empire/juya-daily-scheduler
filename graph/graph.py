from langgraph.graph import StateGraph, START, END

from graph.state import State
from graph.nodes import fetch_rss, translate_content, convert_to_html, send_email

graph = StateGraph(State)

graph.add_node("fetch_rss", fetch_rss)
graph.add_node("translate_content", translate_content)
graph.add_node("convert_to_html", convert_to_html)
graph.add_node("send_email", send_email)

graph.add_edge(START, "fetch_rss")
graph.add_edge("fetch_rss", "translate_content")
graph.add_edge("translate_content", "convert_to_html")
graph.add_edge("convert_to_html", "send_email")
graph.add_edge("send_email", END)

ai_daily_app = graph.compile()
