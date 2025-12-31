from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware,PIIMiddleware,TodoListMiddleware,LLMToolEmulator
import os
from mock_llm import MockChatModel, MockErrorChatModel
from langchain.tools import tool
from langchain.messages import HumanMessage
from pprint import pprint
from custom_middleware import LoggingMiddleware,RetryMiddleware,ContentFilterMiddleware,DynamicModelSelection
from langchain_openai import ChatOpenAI

advanced_model = ChatOpenAI(base_url="http://192.168.1.55:1234/v1/",api_key="sk-dummy",model_name="qwen/qwen3-32",temperature=0.7)
model = ChatOpenAI(base_url="http://192.168.1.55:1234/v1/",api_key="sk-dummy",model_name="qwen/qwen3-32",temperature=0.7)

# model = MockChatModel()
# Use MockErrorChatModel to test retries
# model = MockErrorChatModel(fail_count=2)

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"Weather in {location}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    print(f"Sending email to {to} with subject {subject} and body {body}")
    return "Email sent"


agent = create_agent(
    model=model,
    middleware=[
        SummarizationMiddleware(model=model,trigger=("tokens", 10),keep=("messages", 3)),
        PIIMiddleware("email", strategy="hash", apply_to_input=True,apply_to_output=True),
        LLMToolEmulator(model=model,tools=[get_weather, send_email]),
        LoggingMiddleware(),
        RetryMiddleware(max_retries=3),
        ContentFilterMiddleware(banned_keywords=["inappropriate", "offensive","hack", "exploit", "malware"]),
        DynamicModelSelection(basic_model=model, advanced_model=advanced_model),
    ],
    # tools=[get_weather, send_email],    
)

pprint(agent.invoke({
    "messages": [HumanMessage(content="Send and email to test@example.com with subject 'Test' and body 'This is a test email. '")]
}))

