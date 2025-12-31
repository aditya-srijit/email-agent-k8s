from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
    hook_config,
)
from langgraph.runtime import Runtime
from typing import Any, Callable
from langchain.messages import AIMessage
from langchain_core.language_models.chat_models import BaseChatModel

class LoggingMiddleware(AgentMiddleware):
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"About to call model with {len(state['messages'])} messages")
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"Model returned:  ")
        return None

    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"Agent returned: ")
        return None

class RetryMiddleware(AgentMiddleware):
    def __init__(self, max_retries: int = 3):
        super().__init__()
        self.max_retries = max_retries

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        for attempt in range(self.max_retries):
            try:
                return handler(request)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                print(f"Retry {attempt + 1}/{self.max_retries} after error: {e}")

class ContentFilterMiddleware(AgentMiddleware):
    """Deterministic guardrail: Block requests containing banned keywords."""

    def __init__(self, banned_keywords: list[str]):
        super().__init__()
        self.banned_keywords = [kw.lower() for kw in banned_keywords]

    @hook_config(can_jump_to=["end"])
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # Get the first user message
        if not state["messages"]:
            return None

        first_message = state["messages"][0]
        if first_message.type != "human":
            return None

        content = first_message.content.lower()

        # Check for banned keywords
        for keyword in self.banned_keywords:
            if keyword in content:
                # Block execution before any processing
                # return AIMessage(content=f"I cannot process requests containing '[{keyword}]' inappropriate content. Please rephrase your request.",jump_to="end")
                return {
                    "messages": [{
                        "role": "assistant",
                        "content": f"I cannot process requests containing '[{keyword}]' inappropriate content. Please rephrase your request."
                    }],
                    "jump_to": "end"
                }

        return None

class DynamicModelSelection(AgentMiddleware):
    def __init__(self, basic_model: BaseChatModel, advanced_model: BaseChatModel):
        super().__init__()
        self.basic_model = basic_model
        self.advanced_model = advanced_model

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Choose model based on conversation complexity."""
        message_count = len(request.state["messages"])
        print(f"Message count: {message_count}")

        if message_count > 2:
            model = self.advanced_model
            print("Using advanced model")
        else:
            model = self.basic_model
            print("Using basic model")

        return handler(request.override(model=model))