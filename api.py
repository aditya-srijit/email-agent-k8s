"""
FastAPI application wrapper for the email agent.

Provides:
- WebSocket endpoint for agent interaction
- Health check endpoint
- Human-in-the-loop interrupt handling
"""

import os
import json
import asyncio
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langgraph.types import Command

from email_agent import create_app

# Initialize FastAPI
app = FastAPI(
    title="Email Agent API",
    description="FastAPI wrapper for LangGraph email agent with WebSocket support",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the LangGraph agent
agent_app = create_app()


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON with status, timestamp, and version
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
            "service": "email-agent"
        }
    )

@app.get("/metrics")
async def metrics():
    """
    Metrics endpoint.
    
    Returns:
        JSON with metrics data
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
            "service": "email-agent"
        }
    )   


@app.websocket("/agent")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for bidirectional agent communication.
    
    Protocol:
    1. Client sends initial email data:
       {
           "type": "process_email",
           "email_content": "...",
           "sender_email": "...",
           "email_id": "..."
       }
    
    2. Server streams updates:
       {
           "type": "update",
           "node": "...",
           "data": {...}
       }
    
    3. If human review needed, server sends:
       {
           "type": "interrupt",
           "data": {
               "email_content": "...",
               "classification": {...},
               "draft": "..."
           }
       }
    
    4. Client responds with decision:
       {
           "type": "resume",
           "approved": true,
           "comment": "..."
       }
    
    5. Server continues and sends completion:
       {
           "type": "complete",
           "final_state": {...}
       }
    """
    await websocket.accept()
    
    try:
        # Wait for initial email data
        data = await websocket.receive_json()
        
        if data.get("type") != "process_email":
            await websocket.send_json({
                "type": "error",
                "message": "Expected 'process_email' message type"
            })
            await websocket.close()
            return
        
        # Extract email data
        email_content = data.get("email_content")
        sender_email = data.get("sender_email")
        email_id = data.get("email_id")
        
        if not all([email_content, sender_email, email_id]):
            await websocket.send_json({
                "type": "error",
                "message": "Missing required fields: email_content, sender_email, email_id"
            })
            await websocket.close()
            return
        
        # Create initial state
        initial_state = {
            "email_content": email_content,
            "sender_email": sender_email,
            "email_id": email_id,
            "messages": [],
        }
        
        config = {"configurable": {"thread_id": email_id}}
        
        # Stream the first part (until interrupt or completion)
        await websocket.send_json({
            "type": "status",
            "message": "Processing email..."
        })
        
        interrupted = False
        interrupt_data = None
        
        async for chunk in agent_app.astream(initial_state, stream_mode="updates", config=config):
            # Send update to client
            await websocket.send_json({
                "type": "update",
                "data":str(chunk) # Convert to string for serialization
            })
            
            # Check if we have an interrupt
            if hasattr(chunk, '__interrupt__') or (isinstance(chunk, dict) and chunk.get('__interrupt__')):
                interrupted = True
                # The interrupt data will be in the state
                break
        
        # Get the current state to check for interrupts
        state_snapshot = agent_app.get_state(config)
        
        if state_snapshot.next and len(state_snapshot.next) > 0:
            # We have an interrupt - request human review
            interrupted = True
            current_state = state_snapshot.values
            
            await websocket.send_json({
                "type": "interrupt",
                "message": "Human review required",
                "data": {
                    "email_content": current_state.get("email_content"),
                    "sender_email": current_state.get("sender_email"),
                    "email_id": current_state.get("email_id"),
                    "classification": current_state.get("classification", {}).model_dump() if hasattr(current_state.get("classification", {}), "model_dump") else {},
                    "draft": f"Detected urgency. Please review and approve."
                }
            })
            
            # Wait for human decision
            decision_data = await websocket.receive_json()
            
            if decision_data.get("type") != "resume":
                await websocket.send_json({
                    "type": "error",
                    "message": "Expected 'resume' message type"
                })
                await websocket.close()
                return
            
            # Resume with the decision
            human_response = Command(
                resume={
                    "approved": decision_data.get("approved", False),
                    "comment": decision_data.get("comment", ""),
                }
            )
            
            await websocket.send_json({
                "type": "status",
                "message": "Resuming processing..."
            })
            
            # Continue streaming
            async for chunk in agent_app.astream(human_response, stream_mode="updates", config=config):
                await websocket.send_json({
                    "type": "update",
                    "data": str(chunk)
                })
        
        # Send completion
        final_state = agent_app.get_state(config)
        await websocket.send_json({
            "type": "complete",
            "message": "Email processing complete",
            "final_state": {
                "email_id": email_id,
                "status": "completed"
            }
        })
        
    except WebSocketDisconnect:
        print(f"WebSocket disconnected")
    except Exception as e:
        print(f"Error in WebSocket: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
