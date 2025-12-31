from pprint import pprint
from email_agent import create_app


from langgraph.types import  Command


def main():
    # Simple manual test when running `python -m my_agent.agent`
    app = create_app()

    initial_state = {
        "email_content": "I am happy with the service provided by your company. ",
        "sender_email": "aditya@example.com",
        "email_id": "aditya@gmail.com",
        "messages": [],
    }

    config = {"configurable": {"thread_id": "aditya@gmail.com"}}

    # result = app.invoke(initial_state, config)
    for chunk in app.stream(initial_state,stream_mode="updates",config=config):
        chunk.pretty_print()

    # print("Interrupt:", result.get("__interrupt__"))

    human_response = Command(
            resume={
                "approved": True,
                "comment": "Looks good, send it.",
            }
        )

    # final = app.invoke(human_response, config)
    for chunk in app.stream(human_response, stream_mode="updates",config=config):
        chunk.pretty_print()


if __name__ == "__main__":
    main()

