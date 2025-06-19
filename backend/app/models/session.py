"""
Learning Session models for tracking user activity
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class SessionType(str, Enum):
    STUDY = "study"
    QUIZ = "quiz"
    ASSESSMENT = "assessment"
    AI_CHAT = "ai_chat"
    GROUP_STUDY = "group_study"
    CHALLENGE = "challenge"

class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    PAUSED = "paused"

class QuestionAttempt(BaseModel):
    question_id: str
    user_answer: str
    is_correct: bool
    time_taken_seconds: int
    hints_used: int = 0
    xp_earned: int = 0
    attempted_at: datetime = Field(default_factory=datetime.utcnow)

class AIInteraction(BaseModel):
    model_used: str  # openai, claude, gemini
    prompt: str
    response: str
    tokens_used: int
    response_time_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Session(Document):
    """Learning session document"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    session_type: SessionType
    
    # Session Data
    title: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    
    # Context
    study_group_id: Optional[str] = None
    question_set_id: Optional[str] = None
    organization_id: Optional[str] = None
    
    # Progress
    status: SessionStatus = SessionStatus.ACTIVE
    questions_attempted: List[QuestionAttempt] = []
    ai_interactions: List[AIInteraction] = []
    
    # Performance
    total_questions: int = 0
    correct_answers: int = 0
    total_xp_earned: int = 0
    total_time_minutes: int = 0
    
    # Analytics
    accuracy_rate: float = 0.0
    avg_time_per_question: float = 0.0
    hints_used_total: int = 0
    ai_help_percentage: float = 0.0
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    device_info: Dict[str, str] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    class Settings:
        collection = "sessions"
        indexes = [
            [("user_id", 1)],
            [("session_type", 1)],
            [("status", 1)],
            [("study_group_id", 1)],
            [("started_at", -1)],
            [("organization_id", 1)]
        ]

class DailyChallenge(Document):
    """Daily challenge tracking"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    date: datetime = Field(default_factory=lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
    
    # Challenge Details
    title: str
    description: str
    question_ids: List[str] = []
    xp_reward: int = 50
    badge_reward: Optional[str] = None
    
    # Participation
    participants: List[str] = []  # user_ids
    completions: List[str] = []  # user_ids who completed
    completion_rate: float = 0.0
    
    # Settings
    difficulty_level: str = "mixed"
    time_limit_minutes: int = 30
    subject: str
    
    # Status
    is_active: bool = True
    
    class Settings:
        collection = "daily_challenges"
        indexes = [
            [("date", -1)],
            [("subject", 1)],
            [("is_active", 1)]
        ]