from typing import Literal, Optional, Dict, Any

from langgraph.graph import MessagesState
from pydantic import BaseModel


class BaseState(MessagesState):
    """Base state that carries a `messages` list compatible with LangGraph."""

    pass


class EmailAnalysis(BaseModel):
    """Structured output schema for email intent classification."""

    intent: str
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str


class EmailAgentState(BaseState):
    """State for the email agent graph."""

    email_content: str
    sender_email: str
    email_id: str

    # Set by the graph
    human_decision: Optional[Dict[str, Any]] = None
    classification: Optional[EmailAnalysis] = None


