"""
AI Conversation models for chat history
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class AIModel(str, Enum):
    OPENAI_GPT4 = "openai-gpt4"
    OPENAI_GPT35 = "openai-gpt3.5"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    GEMINI_PRO = "gemini-pro"

class ConversationMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # AI Metadata
    model_used: Optional[AIModel] = None
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None
    
    # Learning Context
    related_question_id: Optional[str] = None
    related_topic: Optional[str] = None
    
    # Feedback
    user_rating: Optional[int] = None  # 1-5 stars
    is_helpful: Optional[bool] = None

class Conversation(Document):
    """AI conversation history"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    title: str = "AI Chat Session"
    
    # Messages
    messages: List[ConversationMessage] = []
    total_messages: int = 0
    
    # AI Configuration
    primary_ai_model: AIModel = AIModel.OPENAI_GPT4
    system_prompt: Optional[str] = None
    
    # Context
    session_id: Optional[str] = None
    study_group_id: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    
    # Analytics
    total_tokens_used: int = 0
    avg_response_time_ms: float = 0.0
    user_satisfaction: Optional[float] = None
    
    # Status
    is_active: bool = True
    is_archived: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "conversations"
        indexes = [
            [("user_id", 1)],
            [("session_id", 1)],
            [("study_group_id", 1)],
            [("subject", 1)],
            [("created_at", -1)],
            [("last_message_at", -1)]
        ]

class AIUsageLog(Document):
    """Detailed AI usage tracking for transparency"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    conversation_id: str
    
    # AI Details
    model_used: AIModel
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    # Performance
    response_time_ms: int
    cost_estimate: float = 0.0
    
    # Context
    session_id: Optional[str] = None
    question_id: Optional[str] = None
    help_type: Optional[str] = None  # hint, explanation, tutoring
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "ai_usage_logs"
        indexes = [
            [("user_id", 1)],
            [("conversation_id", 1)],
            [("model_used", 1)],
            [("timestamp", -1)]
        ]