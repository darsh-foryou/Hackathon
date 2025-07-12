# app/routers/chat.py
from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse, SessionCreateRequest, SessionResponse, ResetRequest
from app.services.llm_service import get_gpt_response, extract_user_info, categorize_conversation
from app.services.crm_service import crm_service
from app.models.crm import ConversationCategory
import uuid

router = APIRouter(tags=["Chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Enhanced chat endpoint with CRM and RAG integration"""
    try:
        # Check if user exists, if not create a temporary user
        user = crm_service.get_user(request.user_id)
        if not user:
            # Extract user info from message and create user
            user_info = extract_user_info(request.message)
            if user_info.get('name') and user_info.get('email'):
                from app.models.crm import UserCreate
                user_data = UserCreate(
                    name=user_info['name'],
                    email=user_info['email'],
                    company=user_info.get('company'),
                    phone=user_info.get('phone'),
                    preferences=user_info.get('preferences', {})
                )
                user = crm_service.create_user(user_data)
        
        # Create or use existing session
        session_id = request.session_id
        if not session_id:
            # Create new session
            category = categorize_conversation(request.message)
            session_id = crm_service.create_conversation_session(request.user_id, category)
        
        # Get enhanced response with RAG and CRM context
        response_data = get_gpt_response(
            message=request.message,
            user_id=request.user_id,
            session_id=session_id,
            use_rag=request.use_rag,
            rag_context=request.rag_context
        )
        
        return ChatResponse(
            response=response_data["response"],
            model_used=response_data["model_used"],
            processing_time=response_data["processing_time"],
            rag_used=response_data["rag_used"],
            user_context_used=response_data["user_context_used"],
            conversation_history_used=response_data["conversation_history_used"],
            tokens_used=response_data.get("tokens_used"),
            session_id=session_id,
            error=response_data.get("error", False)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """Create a new conversation session"""
    try:
        # Check if user exists
        user = crm_service.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create session
        category = ConversationCategory(request.category) if request.category else ConversationCategory.GENERAL
        session_id = crm_service.create_conversation_session(request.user_id, category)
        
        # Get session details
        conversations = crm_service.get_conversation_history(request.user_id, limit=1)
        session = next((conv for conv in conversations if conv.session_id == session_id), None)
        
        if session:
            return SessionResponse(
                session_id=session.session_id,
                user_id=session.user_id,
                category=session.category.value,
                created_at=session.created_at.isoformat(),
                is_active=session.is_active
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create session")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset")
async def reset_conversation(request: ResetRequest):
    """Reset conversation memory for a user or specific session"""
    try:
        if request.session_id:
            # Reset specific session
            success = crm_service.close_conversation_session(request.session_id)
            if success:
                return {"status": "success", "message": f"Session {request.session_id} reset"}
            else:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            # Reset all sessions for user
            conversations = crm_service.get_conversation_history(request.user_id, limit=100)
            closed_count = 0
            for conv in conversations:
                if conv.is_active:
                    crm_service.close_conversation_session(conv.session_id)
                    closed_count += 1
            
            return {
                "status": "success", 
                "message": f"Reset {closed_count} active sessions for user {request.user_id}"
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{user_id}")
async def get_user_sessions(user_id: str, limit: int = 20):
    """Get all sessions for a user"""
    try:
        conversations = crm_service.get_conversation_history(user_id, limit)
        return {
            "user_id": user_id,
            "sessions": conversations,
            "total_sessions": len(conversations)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
