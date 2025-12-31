from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

class MockChatModel(BaseChatModel):
    """A mock chat model that returns a fixed response."""
    
    response_text: str = Field(default="This is a mock response from MockChatModel email: test@example.com.")
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Run the LLM."""
        message = AIMessage(content=self.response_text)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        """Return type of hybrid."""
        return "mock-chat-model"

class MockErrorChatModel(BaseChatModel):
    """A mock chat model that throws exceptions significantly to test retries."""
    
    response_text: str = Field(default="Success after retries!")
    fail_count: int = Field(default=2)
    exception_message: str = Field(default="Simulated failure")
    _current_attempts: int = 0

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Run the LLM, failing for the first `fail_count` attempts."""
        if self._current_attempts < self.fail_count:
            self._current_attempts += 1
            raise Exception(f"{self.exception_message} (Attempt {self._current_attempts})")
        
        # Reset counter if you want it to fail again next time, or keep it successful.
        # For a single stream of usage, typically we might want it to succeed now.
        # However, if reused, we might want to think about resetting. 
        # For now, let's just facilitate the success.
        
        message = AIMessage(content=self.response_text)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "mock-error-chat-model"
