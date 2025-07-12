# app/models/crm.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ConversationCategory(str, Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    INQUIRING = "inquiring"
    GENERAL = "general"
    SUPPORT = "support"
    SALES = "sales"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[dict] = {}

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[dict] = None

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    company: Optional[str] = None
    phone: Optional[str] = None
    preferences: dict
    created_at: datetime
    updated_at: datetime

class ConversationMessage(BaseModel):
    message_id: str
    user_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[dict] = {}

class ConversationSession(BaseModel):
    session_id: str
    user_id: str
    category: ConversationCategory
    title: Optional[str] = None
    messages: List[ConversationMessage]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class ConversationResponse(BaseModel):
    session_id: str
    user_id: str
    category: ConversationCategory
    title: Optional[str] = None
    message_count: int
    created_at: datetime
    updated_at: datetime
    is_active: bool 