"""
AI Tutor endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.middleware.auth import get_current_user_required
from app.services.ai_router import ai_router
from app.models.conversation import Conversation, ConversationMessage, MessageRole, AIModel
from app.models.user import User
from app.models.analytics import Analytics, EventType

router = APIRouter()

class ChatMessage(BaseModel):
    role: MessageRole
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model: AIModel = AIModel.OPENAI_GPT4
    subject: Optional[str] = None
    topic: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1000, ge=1, le=4000)

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    model: AIModel
    tokens_used: int
    response_time_ms: int
    message_id: str

class ConversationResponse(BaseModel):
    id: str
    title: str
    messages: List[ConversationMessage]
    created_at: datetime
    updated_at: datetime

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: Request,
    chat_request: ChatRequest,
    user_id: str = Depends(get_current_user_required)
):
    """Chat with AI tutor"""
    
    # Get or create conversation
    conversation = None
    if chat_request.conversation_id:
        conversation = await Conversation.get(chat_request.conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            title=f"AI Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            primary_ai_model=chat_request.model,
            subject=chat_request.subject,
            topic=chat_request.topic
        )
        await conversation.insert()
    
    # Prepare conversation history for AI
    messages = []
    for msg in conversation.messages[-10:]:  # Last 10 messages for context
        messages.append({
            "role": msg.role.value,
            "content": msg.content
        })
    
    # Add new user message
    messages.append({
        "role": "user",
        "content": chat_request.message
    })
    
    # Get AI response
    ai_response = await ai_router.chat_completion(
        model=chat_request.model,
        messages=messages,
        temperature=chat_request.temperature,
        max_tokens=chat_request.max_tokens,
        system_prompt=_get_system_prompt(chat_request.subject, chat_request.topic)
    )
    
    # Create user message
    user_message = ConversationMessage(
        role=MessageRole.USER,
        content=chat_request.message,
        related_topic=chat_request.topic
    )
    
    # Create AI message
    ai_message = ConversationMessage(
        role=MessageRole.ASSISTANT,
        content=ai_response["response"],
        model_used=chat_request.model,
        tokens_used=ai_response["tokens_used"],
        response_time_ms=ai_response["response_time_ms"],
        related_topic=chat_request.topic
    )
    
    # Update conversation
    conversation.messages.extend([user_message, ai_message])
    conversation.total_messages += 2
    conversation.total_tokens_used += ai_response["tokens_used"]
    conversation.last_message_at = datetime.utcnow()
    conversation.updated_at = datetime.utcnow()
    
    await conversation.save()
    
    # Log analytics
    await Analytics(
        user_id=user_id,
        event_type=EventType.AI_INTERACTION,
        event_data={
            "model": chat_request.model.value,
            "tokens_used": ai_response["tokens_used"],
            "response_time_ms": ai_response["response_time_ms"],
            "subject": chat_request.subject,
            "topic": chat_request.topic
        }
    ).insert()
    
    return ChatResponse(
        response=ai_response["response"],
        conversation_id=conversation.id,
        model=chat_request.model,
        tokens_used=ai_response["tokens_used"],
        response_time_ms=ai_response["response_time_ms"],
        message_id=ai_message.id
    )

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_user_conversations(
    request: Request,
    user_id: str = Depends(get_current_user_required),
    limit: int = 20,
    offset: int = 0
):
    """Get user's conversation history"""
    
    conversations = await Conversation.find(
        {"user_id": user_id, "is_archived": False}
    ).sort([("last_message_at", -1)]).skip(offset).limit(limit).to_list()
    
    return [
        ConversationResponse(
            id=conv.id,
            title=conv.title,
            messages=conv.messages,
            created_at=conv.created_at,
            updated_at=conv.updated_at
        )
        for conv in conversations
    ]

@router.get("/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    request: Request,
    user_id: str = Depends(get_current_user_required)
):
    """Get specific conversation"""
    
    conversation = await Conversation.get(conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        messages=conversation.messages,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )

@router.get("/models", response_model=List[Dict[str, Any]])
async def get_available_models(request: Request):
    """Get available AI models"""
    
    available_models = ai_router.get_available_models()
    
    return [
        {
            "model": model.value,
            "info": ai_router.get_model_info(model)
        }
        for model in available_models
    ]

@router.post("/rate-message")
async def rate_message(
    request: Request,
    message_id: str,
    rating: int = Field(..., ge=1, le=5),
    user_id: str = Depends(get_current_user_required)
):
    """Rate an AI message"""
    
    # Find conversation with this message
    conversation = await Conversation.find_one({
        "user_id": user_id,
        "messages.id": message_id
    })
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Update message rating
    for message in conversation.messages:
        if message.id == message_id:
            message.user_rating = rating
            message.is_helpful = rating >= 3
            break
    
    await conversation.save()
    
    return {"message": "Rating saved successfully"}

def _get_system_prompt(subject: Optional[str] = None, topic: Optional[str] = None) -> str:
    """Get system prompt for AI tutor"""
    
    base_prompt = """You are StarGuide, an AI tutor for students. You provide helpful, accurate, and encouraging responses to help students learn. 

Key guidelines:
- Be patient and encouraging
- Explain concepts clearly with examples
- Ask follow-up questions to check understanding
- Provide hints rather than direct answers when appropriate
- Adapt your language level to the student
- Encourage critical thinking
- If you're unsure about something, say so
- Focus on helping students understand rather than just providing answers"""
    
    if subject:
        base_prompt += f"\n\nYou are currently helping with {subject}."
    
    if topic:
        base_prompt += f" The specific topic is {topic}."
    
    return base_prompt