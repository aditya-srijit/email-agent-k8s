"""
Tool definitions for the email agent.

If you later expose tools to the LLM (via LangChain's `@tool`), define them here.
"""

from langchain.tools import tool
import re

@tool
def send_email(sender_email: str, to_email: str, subject: str, body: str) -> str:
    """
    Sends an email to the specified recipient.
    
    Args:
        sender_email: The email address of the sender.
        to_email: The email address of the recipient.
        subject: The subject of the email.
        body: The content of the email.
        
    Returns:
        A string indicating the status of the email sending process (Success or Failed).
    """
    # 1. Validate email format (simple regex)
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    
    if not re.match(email_regex, sender_email):
        return f"Failed: Invalid sender_email format: {sender_email}"
    
    if not re.match(email_regex, to_email):
        return f"Failed: Invalid to_email format: {to_email}"

    # 2. Dummy sending process
    print(f"Attempting to send email from {sender_email} to {to_email}...")
    print(f"Subject: {subject}")
    # Simulate processing
    import time
    time.sleep(1) # Simulate network delay

    # 3. Return status
    # We'll just assume success for the dummy tool unless specific triggers are added later
    return "Success: Email sent"


