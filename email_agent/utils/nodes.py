from langchain.messages import HumanMessage, AIMessage
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import interrupt, Command, Send

from .state import EmailAgentState, EmailAnalysis
from .tools import send_email


# Shared LLM instance for all nodes
import os
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://192.168.1.55:1234/v1/"),
    api_key=os.getenv("LLM_API_KEY", "sk-dummy"),
    model_name=os.getenv("LLM_MODEL_NAME", "qwen/qwen3-32"),
    temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
)


def read_email(state: EmailAgentState) -> EmailAgentState:
    """Read the raw email content and add an initial message to the thread."""

    state["messages"].append(
        HumanMessage(content=f"Processing email: {state['email_content']}")
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that reads emails and extracts the "
                "email content, sender email, and email id.",
            ),
            ("human", "{email_content}"),
        ]
    )
    messages = prompt.format_messages(email_content=state["email_content"])
    model_response = model.invoke(messages)

    state["messages"].append(AIMessage(content=model_response.content))
    return state


def classify_intent(state: EmailAgentState) -> Command:
    """
    Classify the intent/urgency of the email using structured output.

    Routes either to `human_review` (for high urgency) or to END.
    """

    structured_llm = model.with_structured_output(EmailAnalysis)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that classifies the intent of the email.",
            ),
            ("human", "{email_content}"),
        ]
    )
    messages = prompt.format_messages(email_content=state["email_content"])
    model_response: EmailAnalysis = structured_llm.invoke(messages)

    state["messages"].append(AIMessage(content=model_response.model_dump_json()))

    if model_response.urgency == "high":
        return Command(update={"classification": model_response}, goto="human_review")
    else:
        return Command(update={"classification": model_response}, goto="send_email_reply")


def human_review(state: EmailAgentState) -> Command:
    """
    Pause for human review using `interrupt`.

    The human should return a dict like:
        {"approved": True, "comment": "Looks good, send it."}
    """

    classification = state["classification"]

    human_decision = interrupt(
        {
            "email_content": state["email_content"],
            "sender_email": state["sender_email"],
            "email_id": state["email_id"],
            "classification": classification.model_dump(),
            "draft": (
                f"Auto-detected {classification.intent} with urgency "
                f"{classification.urgency}. Approve?"
            ),
        }
    )

    return Command(update={"human_decision": human_decision}, goto="approve_response_human")


def approve_response_human(state: EmailAgentState) -> EmailAgentState:
    """
    Finalize the response after human review.

    Appends a summary message and optionally triggers `send_email_reply`.
    """

    classification = state["classification"]
    decision = state.get("human_decision") or {}

    description = (
        f"Final response for {classification.intent} "
        f"(urgency: {classification.urgency}) "
        f"approved={decision.get('approved', False)}"
    )

    # If approved, go to send_email_reply. Otherwise, follow default edge (likely END).
    if decision.get("approved"):
        return Command(update={"messages": [AIMessage(content=description)]}, goto="send_email_reply")

    return Command(update={"messages": [AIMessage(content=description)]})


def send_email_reply(state: EmailAgentState) -> EmailAgentState:
    """Refined node: Generate reply content using LLM and send it via tool."""
    
    print("Sending email reply with decision:", state.get("human_decision"))

    # 1. Prepare context for the LLM
    decision = state.get("human_decision", {})
    classification = state.get("classification")
    original_email = state.get("email_content")
    sender = state.get("sender_email")

    # 2. Bind tool to model
    model_with_tools = model.bind_tools([send_email])

    # 3. Construct prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an intelligent email assistant. "
                "Your goal is to write a professional email reply based on the user's decision "
                "and send it using the 'send_email' tool. "
                "The 'sender_email' argument for the tool should be 'agent@middlewareapp.com'. "
                "The 'to_email' should be the original sender: {sender}. "
                "Infer a suitable subject related to the original email."
            ),
            (
                "human",
                "Original Email: {original_email}\n"
                "Classification: {classification}\n"
                "Human Decision: {decision}\n\n"
                "Please generate the reply and send it now."
            ),
        ]
    )

    messages = prompt.format_messages(
        sender=sender,
        original_email=original_email,
        classification=classification,
        decision=decision
    )

    # 4. Invoke LLM
    response = model_with_tools.invoke(messages)
    state["messages"].append(AIMessage(content=response.content))

    # 5. Execute tool calls if present
    for tool_call in response.tool_calls:
        if tool_call["name"] == "send_email":
            try:
                print(f"Executing tool: {tool_call['name']} with args: {tool_call['args']}")
                output = send_email.invoke(tool_call["args"])
                print(f"Tool output: {output}")
                
                state["messages"].append(
                    ToolMessage(content=str(output), tool_call_id=tool_call["id"])
                )
            except Exception as e:
                error_msg = f"Tool execution failed: {e}"
                print(error_msg)
                state["messages"].append(
                    ToolMessage(content=error_msg, tool_call_id=tool_call["id"])
                )

    return state
