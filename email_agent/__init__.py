"""
Top-level package for the email classification agent.

Exports a convenience factory for creating the LangGraph app.
"""

from .agent import create_app

__all__ = ["create_app"]


