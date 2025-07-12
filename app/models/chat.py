# app/models/chat.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None
    use_rag: Optional[bool] = True
    rag_context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    model_used: str
    processing_time: float
    rag_used: bool
    user_context_used: bool
    conversation_history_used: bool
    tokens_used: Optional[int] = None
    session_id: Optional[str] = None
    error: Optional[bool] = False

class SessionCreateRequest(BaseModel):
    user_id: str
    category: Optional[str] = "general"

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    category: str
    created_at: str
    is_active: bool

class ResetRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None  # If None, reset all sessions for user
