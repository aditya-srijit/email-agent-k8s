"""
Graph construction for the email agent.

This module exposes `create_app()` which builds and returns
the compiled LangGraph application.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# Support running as a module (`python -m my_agent.agent`) and as a script (`python my_agent/agent.py`)
try:
    from .utils.state import EmailAgentState
    from .utils.nodes import (
        read_email,
        classify_intent,
        human_review,
        approve_response_human,
        send_email_reply,
    )
except ImportError:
    from email_agent.utils.state import EmailAgentState  # type: ignore
    from email_agent.utils.nodes import (  # type: ignore
    read_email,
    classify_intent,
    human_review,
    approve_response_human,
    send_email_reply,
)


def create_app():
    """Create and compile the email agent LangGraph app."""

    workflow = StateGraph(EmailAgentState)

    # Nodes
    workflow.add_node("read_email", read_email)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("human_review", human_review)
    workflow.add_node("approve_response_human", approve_response_human)
    workflow.add_node("send_email_reply", send_email_reply)

    # Edges
    workflow.add_edge(START, "read_email")
    workflow.add_edge("read_email", "classify_intent")
    workflow.add_edge("approve_response_human", END)
    workflow.add_edge("send_email_reply", END)


    memory = InMemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app





