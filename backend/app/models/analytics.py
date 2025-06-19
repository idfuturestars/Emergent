"""
Analytics and tracking models
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class EventType(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    QUESTION_ANSWERED = "question_answered"
    SESSION_STARTED = "session_started"
    SESSION_COMPLETED = "session_completed"
    ACHIEVEMENT_EARNED = "achievement_earned"
    AI_INTERACTION = "ai_interaction"
    GROUP_JOINED = "group_joined"
    QUIZ_COMPLETED = "quiz_completed"

class Analytics(Document):
    """Analytics event tracking"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    event_type: EventType
    
    # Event Data
    event_data: Dict[str, Any] = {}
    session_id: Optional[str] = None
    
    # Context
    organization_id: Optional[str] = None
    study_group_id: Optional[str] = None
    
    # Technical
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_type: Optional[str] = None
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "analytics"
        indexes = [
            [("user_id", 1)],
            [("event_type", 1)],
            [("timestamp", -1)],
            [("organization_id", 1)],
            [("session_id", 1)]
        ]

class UserLearningMetrics(Document):
    """Aggregated learning metrics per user"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    date: datetime = Field(default_factory=lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
    
    # Learning Metrics
    total_study_time_minutes: int = 0
    questions_answered: int = 0
    correct_answers: int = 0
    accuracy_rate: float = 0.0
    
    # XP & Progress
    xp_earned: int = 0
    level_ups: int = 0
    achievements_earned: int = 0
    
    # AI Usage
    ai_interactions: int = 0
    ai_help_percentage: float = 0.0
    
    # Social
    group_sessions: int = 0
    messages_sent: int = 0
    
    # Subjects
    subjects_studied: List[str] = []
    subject_performance: Dict[str, float] = {}
    
    class Settings:
        collection = "user_learning_metrics"
        indexes = [
            [("user_id", 1), ("date", -1)],
            [("date", -1)]
        ]

class PlatformMetrics(Document):
    """Platform-wide metrics"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    date: datetime = Field(default_factory=lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
    
    # User Metrics
    total_users: int = 0
    active_users: int = 0
    new_users: int = 0
    
    # Activity Metrics
    total_sessions: int = 0
    total_questions_answered: int = 0
    total_study_time_hours: float = 0.0
    
    # AI Metrics
    ai_interactions: int = 0
    ai_tokens_used: int = 0
    ai_response_time_avg: float = 0.0
    
    # Social Metrics
    active_study_groups: int = 0
    messages_sent: int = 0
    
    # Performance Metrics
    avg_accuracy_rate: float = 0.0
    avg_session_duration: float = 0.0
    
    # Organization
    organization_id: Optional[str] = None
    
    class Settings:
        collection = "platform_metrics"
        indexes = [
            [("date", -1)],
            [("organization_id", 1), ("date", -1)]
        ]