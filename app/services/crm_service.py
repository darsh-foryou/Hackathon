# app/services/crm_service.py
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from app.models.crm import (
    UserCreate, UserUpdate, UserResponse, 
    ConversationMessage, ConversationSession, 
    ConversationResponse, ConversationCategory
)
from app.models.upload import FileMetadata
from app.config import MONGODB_URI, MONGODB_DB

class CRMService:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[MONGODB_DB]
        self.users: Collection = self.db["users"]
        self.sessions: Collection = self.db["sessions"]
        self.messages: Collection = self.db["messages"]
        self.files: Collection = self.db["files"]  # New collection for file metadata
        self._init_indexes()
        # Test connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print("MongoDB connection error:", e)

    def _init_indexes(self):
        self.users.create_index("user_id", unique=True)
        self.users.create_index("email", unique=True)
        self.sessions.create_index("session_id", unique=True)
        self.sessions.create_index("user_id")
        self.messages.create_index("message_id", unique=True)
        self.messages.create_index("session_id")
        self.messages.create_index("user_id")
        # File indexes
        self.files.create_index("file_id", unique=True)
        self.files.create_index("user_id")
        self.files.create_index("vector_store_path")

    def create_user(self, user_data: UserCreate) -> UserResponse:
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        doc = {
            "user_id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "company": user_data.company,
            "phone": user_data.phone,
            "preferences": user_data.preferences or {},
            "created_at": now,
            "updated_at": now
        }
        self.users.insert_one(doc)
        return self.get_user(user_id)

    def get_user(self, user_id: str) -> Optional[UserResponse]:
        doc = self.users.find_one({"user_id": user_id})
        if doc:
            return UserResponse(
                user_id=doc["user_id"],
                name=doc["name"],
                email=doc["email"],
                company=doc.get("company"),
                phone=doc.get("phone"),
                preferences=doc.get("preferences", {}),
                created_at=doc["created_at"],
                updated_at=doc["updated_at"]
            )
        return None

    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        update_fields = {k: v for k, v in user_data.dict(exclude_unset=True).items() if v is not None}
        if not update_fields:
            return self.get_user(user_id)
        update_fields["updated_at"] = datetime.utcnow()
        self.users.update_one({"user_id": user_id}, {"$set": update_fields})
        return self.get_user(user_id)

    def create_conversation_session(self, user_id: str, category: ConversationCategory = ConversationCategory.GENERAL) -> str:
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        doc = {
            "session_id": session_id,
            "user_id": user_id,
            "category": category.value,
            "title": None,
            "created_at": now,
            "updated_at": now,
            "is_active": True
        }
        self.sessions.insert_one(doc)
        return session_id

    def add_message(self, session_id: str, user_id: str, role: str, content: str, metadata: Optional[Dict] = None) -> str:
        message_id = str(uuid.uuid4())
        now = datetime.utcnow()
        doc = {
            "message_id": message_id,
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": now,
            "metadata": metadata or {}
        }
        self.messages.insert_one(doc)
        self.sessions.update_one({"session_id": session_id}, {"$set": {"updated_at": now}})
        return message_id

    def get_conversation_history(self, user_id: str, limit: int = 50) -> List[ConversationResponse]:
        cursor = self.sessions.find({"user_id": user_id}).sort("updated_at", DESCENDING).limit(limit)
        conversations = []
        for doc in cursor:
            message_count = self.messages.count_documents({"session_id": doc["session_id"]})
            conversations.append(ConversationResponse(
                session_id=doc["session_id"],
                user_id=doc["user_id"],
                category=ConversationCategory(doc["category"]),
                title=doc.get("title"),
                message_count=message_count,
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                is_active=doc.get("is_active", True)
            ))
        return conversations

    def get_session_messages(self, session_id: str) -> List[ConversationMessage]:
        cursor = self.messages.find({"session_id": session_id}).sort("timestamp", ASCENDING)
        messages = []
        for doc in cursor:
            messages.append(ConversationMessage(
                message_id=doc["message_id"],
                user_id=doc["user_id"],
                role=doc["role"],
                content=doc["content"],
                timestamp=doc["timestamp"],
                metadata=doc.get("metadata", {})
            ))
        return messages

    def update_conversation_category(self, session_id: str, category: ConversationCategory) -> bool:
        result = self.sessions.update_one({"session_id": session_id}, {"$set": {"category": category.value, "updated_at": datetime.utcnow()}})
        return result.modified_count > 0

    def close_conversation_session(self, session_id: str) -> bool:
        result = self.sessions.update_one({"session_id": session_id}, {"$set": {"is_active": False, "updated_at": datetime.utcnow()}})
        return result.modified_count > 0

    # File management methods
    def save_file_metadata(self, file_id: str, user_id: str, filename: str, file_type: str, file_size: int, vector_store_path: str) -> bool:
        """Save file metadata to MongoDB"""
        try:
            doc = {
                "file_id": file_id,
                "user_id": user_id,
                "filename": filename,
                "file_type": file_type,
                "file_size": file_size,
                "vector_store_path": vector_store_path,
                "uploaded_at": datetime.utcnow(),
                "is_active": True
            }
            self.files.insert_one(doc)
            return True
        except Exception as e:
            print(f"Error saving file metadata: {e}")
            return False

    def get_user_files(self, user_id: str) -> List[Dict]:
        """Get all files uploaded by a user"""
        cursor = self.files.find({"user_id": user_id, "is_active": True}).sort("uploaded_at", DESCENDING)
        files = []
        for doc in cursor:
            files.append({
                "file_id": doc["file_id"],
                "filename": doc["filename"],
                "file_type": doc["file_type"],
                "file_size": doc["file_size"],
                "vector_store_path": doc["vector_store_path"],
                "uploaded_at": doc["uploaded_at"]
            })
        return files

    def get_file_by_id(self, file_id: str) -> Optional[Dict]:
        """Get file metadata by file_id"""
        doc = self.files.find_one({"file_id": file_id, "is_active": True})
        if doc:
            return {
                "file_id": doc["file_id"],
                "user_id": doc["user_id"],
                "filename": doc["filename"],
                "file_type": doc["file_type"],
                "file_size": doc["file_size"],
                "vector_store_path": doc["vector_store_path"],
                "uploaded_at": doc["uploaded_at"]
            }
        return None

    def delete_file(self, file_id: str, user_id: str) -> bool:
        """Soft delete a file (mark as inactive)"""
        result = self.files.update_one(
            {"file_id": file_id, "user_id": user_id}, 
            {"$set": {"is_active": False}}
        )
        return result.modified_count > 0

# Global CRM service instance
crm_service = CRMService() 