# Middleware App - Email Agent

This project implements an intelligent Email Agent using LangGraph and FastAPI. It processes emails, classifies them, and can draft responses with a human-in-the-loop workflow.

## Features

- **Email Processing**: Analyzes incoming email content.
- **Classification**: Categorizes emails based on urgency and topic.
- **Human-in-the-loop**: identifying when human review is needed before sending.
- **WebSocket API**: Real-time communication for agent interactions.

## Prerequisites

- Python 3.12+
- `pip` or `uv` package manager

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   # OR if using uv
   uv sync
   ```

3. Configure Environment:
   Copy `.env.example` to `.env` and fill in necessary API keys (OpenAI, etc.).
   ```bash
   cp .env.example .env
   ```

## Running the Application

### 1. Start the API Server
The FastAPI server provides the WebSocket endpoint for the agent.

```bash
# Using Python directly
python api.py

# OR using Uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
The API will be available at `http://localhost:8000`.
Health check: `http://localhost:8000/health`

### 2. Run Manual Test
You can run a standalone test of the agent logic using the main script:

```bash
python main.py
```

## Structure
- `api.py`: FastAPI application entry point.
- `main.py`: Standalone script for testing agent logic.
- `email_agent/`: Core agent implementation (LangGraph).
- `deployment/`: Kubernetes and Docker configurations.
