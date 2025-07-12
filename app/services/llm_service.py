# app/services/llm_service.py

import time
from typing import List, Optional, Dict, Any
from openai import OpenAI
from app.config import OPENAI_API_KEY
from app.services.rag_service import search_vector_store
from app.services.crm_service import crm_service
from app.models.crm import ConversationCategory

# ✅ Create OpenAI client using the NEW SDK format
client = OpenAI(api_key=OPENAI_API_KEY)

def get_gpt_response(
    message: str, 
    user_id: str, 
    session_id: Optional[str] = None,
    use_rag: bool = True,
    rag_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get GPT response with optional RAG and CRM context
    """
    start_time = time.time()
    
    try:
        # Get user context from CRM
        user = crm_service.get_user(user_id)
        user_context = ""
        if user:
            user_context = f"""
            User Information:
            - Name: {user.name}
            - Email: {user.email}
            - Company: {user.company or 'Not specified'}
            - Phone: {user.phone or 'Not specified'}
            - Preferences: {user.preferences}
            """
        
        # Get conversation history if session_id provided
        conversation_history = []
        if session_id:
            messages = crm_service.get_session_messages(session_id)
            # Convert to OpenAI format (last 10 messages for context)
            recent_messages = messages[-10:] if len(messages) > 10 else messages
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in recent_messages
            ]
        
        # Get RAG context if enabled
        rag_context_text = ""
        if use_rag:
            if rag_context:
                # Use provided RAG context
                rag_context_text = f"\nRelevant Information from Knowledge Base:\n{rag_context}"
            else:
                # Search vector store for relevant context
                relevant_docs = search_vector_store(message, top_k=3)
                if relevant_docs:
                    rag_context_text = f"\nRelevant Information from Knowledge Base:\n{relevant_docs}"
        
        # Build system prompt
        system_prompt = f"""You are an intelligent AI assistant integrated with a CRM system. 
        Your role is to provide helpful, contextual responses while maintaining awareness of user information and conversation history.
        
        {user_context}
        
        Guidelines:
        1. Be conversational and helpful
        2. Use the user's name when appropriate
        3. Reference their company or preferences when relevant
        4. If they ask about their previous conversations, refer to the conversation history
        5. If they provide new information about themselves, acknowledge it
        6. Use the knowledge base information when relevant to their questions
        
        {rag_context_text}
        """
        
        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        response_content = response.choices[0].message.content.strip()
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Store message in CRM if session_id provided
        if session_id:
            crm_service.add_message(session_id, user_id, "user", message)
            crm_service.add_message(session_id, user_id, "assistant", response_content, {
                "processing_time": processing_time,
                "model_used": "gpt-3.5-turbo",
                "rag_used": use_rag,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
            })
        
        return {
            "response": response_content,
            "model_used": "gpt-3.5-turbo",
            "processing_time": processing_time,
            "rag_used": use_rag,
            "user_context_used": bool(user),
            "conversation_history_used": bool(conversation_history),
            "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_response = f"Error: {str(e)}"
        
        # Store error message in CRM if session_id provided
        if session_id:
            crm_service.add_message(session_id, user_id, "user", message)
            crm_service.add_message(session_id, user_id, "assistant", error_response, {
                "error": True,
                "processing_time": processing_time
            })
        
        return {
            "response": error_response,
            "model_used": "gpt-3.5-turbo",
            "processing_time": processing_time,
            "error": True
        }

def extract_user_info(message: str) -> Dict[str, Any]:
    """
    Extract potential user information from message using LLM
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
                Extract user information from the message. Return a JSON object with the following fields:
                - name: Full name if mentioned
                - email: Email address if mentioned
                - company: Company name if mentioned
                - phone: Phone number if mentioned
                - preferences: Any preferences or interests mentioned
                
                If a field is not found, set it to null. Return only the JSON object.
                """},
                {"role": "user", "content": message}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        import json
        result = json.loads(response.choices[0].message.content.strip())
        return result
    except:
        return {}

def categorize_conversation(message: str, conversation_history: List[str] = None) -> ConversationCategory:
    """
    Categorize conversation based on content
    """
    try:
        context = message
        if conversation_history:
            context += "\n" + "\n".join(conversation_history[-5:])  # Last 5 messages
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
                Categorize this conversation into one of these categories:
                - general: General questions or casual conversation
                - support: Technical support or help requests
                - sales: Sales inquiries or product questions
                - inquiring: Questions about services or information gathering
                - resolved: Issues that have been resolved
                - unresolved: Issues that still need attention
                
                Return only the category name.
                """},
                {"role": "user", "content": context}
            ],
            temperature=0.1,
            max_tokens=50
        )
        
        category_text = response.choices[0].message.content.strip().lower()
        
        # Map to enum
        category_mapping = {
            "general": ConversationCategory.GENERAL,
            "support": ConversationCategory.SUPPORT,
            "sales": ConversationCategory.SALES,
            "inquiring": ConversationCategory.INQUIRING,
            "resolved": ConversationCategory.RESOLVED,
            "unresolved": ConversationCategory.UNRESOLVED
        }
        
        return category_mapping.get(category_text, ConversationCategory.GENERAL)
    except:
        return ConversationCategory.GENERAL
