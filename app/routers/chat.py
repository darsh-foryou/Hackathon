# app/routers/chat.py
from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_service import get_gpt_response

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    reply = get_gpt_response(request.message)
    return ChatResponse(response=reply, model_used="gpt-3.5-turbo")
