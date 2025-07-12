# app/routers/crm.py
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.crm import (
    UserCreate, UserUpdate, UserResponse, 
    ConversationResponse, ConversationCategory
)
from app.services.crm_service import crm_service

router = APIRouter(prefix="/crm", tags=["CRM"])

@router.post("/create_user", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """Create a new user in the CRM system"""
    try:
        user = crm_service.create_user(user_data)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/update_user/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate):
    """Update user information"""
    try:
        user = crm_service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    try:
        user = crm_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/conversations/{user_id}", response_model=List[ConversationResponse])
async def get_conversations(user_id: str, limit: int = 50):
    """Get conversation history for a user"""
    try:
        conversations = crm_service.get_conversation_history(user_id, limit)
        return conversations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/conversation/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Get all messages for a specific conversation session"""
    try:
        messages = crm_service.get_session_messages(session_id)
        return {
            "session_id": session_id,
            "messages": messages,
            "message_count": len(messages)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/conversation/{session_id}/category")
async def update_conversation_category(session_id: str, category: ConversationCategory):
    """Update conversation category"""
    try:
        success = crm_service.update_conversation_category(session_id, category)
        if success:
            return {"status": "success", "message": f"Category updated to {category.value}"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/conversation/{session_id}")
async def close_conversation(session_id: str):
    """Close a conversation session"""
    try:
        success = crm_service.close_conversation_session(session_id)
        if success:
            return {"status": "success", "message": "Conversation closed"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/categories")
async def get_categories():
    """Get available conversation categories"""
    return {
        "categories": [
            {"value": cat.value, "description": cat.name.lower()}
            for cat in ConversationCategory
        ]
    } 