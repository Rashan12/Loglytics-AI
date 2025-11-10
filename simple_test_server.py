#!/usr/bin/env python3
"""
Simple test server to verify CORS is working
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
from datetime import datetime
from typing import List, Dict, Any

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for projects
projects_db: List[Dict[str, Any]] = [
    {
        "id": "test_project_123",
        "name": "Test Project",
        "description": "Test project",
        "created_at": "2025-10-23T11:00:00Z",
        "user_id": "test_user",
        "status": "active"
    }
]

# In-memory storage for chats and messages
chats_db: List[Dict[str, Any]] = []
messages_db: List[Dict[str, Any]] = []

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test/cors")
async def test_cors():
    return {"message": "CORS is working!", "cors_headers": "should be present"}

@app.post("/test/create-token")
async def create_test_token():
    return {
        "status": "success",
        "access_token": "test_token_12345",
        "user_id": "test_user",
        "user_email": "test@example.com"
    }

@app.get("/api/v1/projects")
async def get_projects():
    return projects_db

@app.post("/api/v1/projects")
async def create_project(project_data: dict = None):
    # Generate a unique project ID
    project_id = str(uuid.uuid4())
    current_time = datetime.now().isoformat() + "Z"
    
    # Create new project
    new_project = {
        "id": project_id,
        "name": project_data.get("name", "New Project") if project_data else "New Project",
        "description": project_data.get("description", "Project description") if project_data else "Project description",
        "created_at": current_time,
        "user_id": "test_user",
        "status": "active"
    }
    
    # Add to database
    projects_db.append(new_project)
    
    return new_project

@app.get("/api/v1/projects/{project_id}")
async def get_project(project_id: str):
    # Find project by ID
    for project in projects_db:
        if project["id"] == project_id:
            return project
    
    # Return 404 if not found
    return {"error": "Project not found", "status": 404}

@app.get("/api/v1/analytics/dashboard")
async def get_analytics_dashboard():
    return {
        "total_logs": 1000,
        "error_rate": 5.2,
        "active_projects": len(projects_db),
        "ai_insights": 15
    }

@app.get("/api/v1/projects/{project_id}/analytics")
async def get_project_analytics(project_id: str):
    # Find project by ID
    project = None
    for p in projects_db:
        if p["id"] == project_id:
            project = p
            break
    
    if not project:
        return {"error": "Project not found", "status": 404}
    
    # Return project-specific analytics - NEW PROJECTS START EMPTY
    return {
        "project_id": project_id,
        "project_name": project["name"],
        "total_logs": 0,  # Start with 0 for new projects
        "error_rate": 0.0,  # Start with 0 for new projects
        "chats": 0,  # Start with 0 for new projects
        "log_files": 0,  # Start with 0 for new projects
        "vector_embeddings": 0,  # Start with 0 for new projects
        "insights": []  # Start with empty insights for new projects
    }

# Chat endpoints
@app.get("/api/v1/chats")
async def get_chats():
    """Get all chats"""
    return chats_db

@app.post("/api/v1/chats")
async def create_chat(chat_data: dict = None):
    """Create a new chat"""
    chat_id = str(uuid.uuid4())
    current_time = datetime.now().isoformat() + "Z"
    
    new_chat = {
        "id": chat_id,
        "title": chat_data.get("title", "New Chat") if chat_data else "New Chat",
        "project_id": chat_data.get("project_id") if chat_data else None,
        "created_at": current_time,
        "updated_at": current_time,
        "user_id": "test_user"
    }
    
    chats_db.append(new_chat)
    return new_chat

@app.get("/api/v1/chats/{chat_id}")
async def get_chat(chat_id: str):
    """Get specific chat"""
    for chat in chats_db:
        if chat["id"] == chat_id:
            return chat
    return {"error": "Chat not found", "status": 404}

@app.get("/api/v1/chats/{chat_id}/messages")
async def get_chat_messages(chat_id: str):
    """Get messages for a specific chat"""
    chat_messages = [msg for msg in messages_db if msg["chat_id"] == chat_id]
    return chat_messages

@app.post("/api/v1/chats/{chat_id}/messages")
async def send_message(chat_id: str, message_data: dict = None):
    """Send a message to a chat"""
    message_id = str(uuid.uuid4())
    current_time = datetime.now().isoformat() + "Z"
    
    # Check if chat exists
    chat_exists = any(chat["id"] == chat_id for chat in chats_db)
    if not chat_exists:
        return {"error": "Chat not found", "status": 404}
    
    new_message = {
        "id": message_id,
        "chat_id": chat_id,
        "content": message_data.get("content", "") if message_data else "",
        "role": message_data.get("role", "user") if message_data else "user",
        "timestamp": current_time,
        "user_id": "test_user"
    }
    
    messages_db.append(new_message)
    
    # Simulate AI response
    if new_message["role"] == "user":
        ai_response = {
            "id": str(uuid.uuid4()),
            "chat_id": chat_id,
            "content": f"I received your message: '{new_message['content']}'. This is a simulated AI response.",
            "role": "assistant",
            "timestamp": (datetime.now().timestamp() + 1) * 1000,  # 1 second later
            "user_id": "ai_system"
        }
        messages_db.append(ai_response)
    
    return new_message

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
