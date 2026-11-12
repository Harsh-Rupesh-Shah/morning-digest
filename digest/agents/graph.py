"""LangGraph orchestrator workflow connecting researchers and editor."""

from langgraph.graph import StateGraph, START, END
from digest.agents.state import DigestState
from digest.agents.ai_researcher import research_ai
from digest.agents.tech_researcher import research_tech
from digest.agents.finance_researcher import research_finance
from digest.agents.editor import edit_and_format


def build_digest_graph():
    """Build the compiled LangGraph workflow for the morning digest."""
    builder = StateGraph(DigestState)

    builder.add_node("research_ai", research_ai)
    builder.add_node("research_tech", research_tech)
    builder.add_node("research_finance", research_finance)
    builder.add_node("editor", edit_and_format)

    # Orchestrator sequence: AI -> Tech -> Finance -> Editor
    builder.add_edge(START, "research_ai")
    builder.add_edge("research_ai", "research_tech")
    builder.add_edge("research_tech", "research_finance")
    builder.add_edge("research_finance", "editor")
    builder.add_edge("editor", END)

    return builder.compile()


digest_graph = build_digest_graph()

