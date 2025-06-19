"""
Question and Assessment models
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    DRAG_DROP = "drag_drop"
    MATCHING = "matching"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class AnswerOption(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    is_correct: bool = False
    explanation: Optional[str] = None

class QuestionHint(BaseModel):
    level: int  # 1, 2, 3 (increasing specificity)
    text: str
    xp_penalty: int = 0  # XP reduction for using hint

class Question(Document):
    """Question document model"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    title: str
    question_text: str
    
    # Categorization
    subject: str
    topic: str
    subtopic: Optional[str] = None
    grade_level: str
    difficulty: DifficultyLevel
    
    # Question Data
    question_type: QuestionType
    answer_options: List[AnswerOption] = []
    correct_answer: str  # For non-multiple choice
    explanation: Optional[str] = None
    
    # Learning Support
    hints: List[QuestionHint] = []
    related_concepts: List[str] = []
    prerequisites: List[str] = []
    
    # Scoring
    base_xp: int = 10
    time_limit_seconds: Optional[int] = None
    
    # Media
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    attachments: List[str] = []
    
    # Metadata
    created_by: str
    organization_id: Optional[str] = None
    is_public: bool = True
    tags: List[str] = []
    
    # Analytics
    times_attempted: int = 0
    times_correct: int = 0
    avg_time_taken: float = 0.0
    difficulty_rating: float = 0.0
    
    # Status
    is_active: bool = True
    is_verified: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "questions"
        indexes = [
            [("subject", 1)],
            [("topic", 1)],
            [("difficulty", 1)],
            [("grade_level", 1)],
            [("created_by", 1)],
            [("organization_id", 1)],
            [("created_at", -1)]
        ]

class QuestionSet(Document):
    """Collection of questions for assessments/quizzes"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    title: str
    description: Optional[str] = None
    
    # Configuration
    question_ids: List[str] = []
    total_questions: int = 0
    time_limit_minutes: Optional[int] = None
    
    # Categorization
    subject: str
    topics: List[str] = []
    difficulty_mix: Dict[str, int] = {}  # {"beginner": 5, "intermediate": 3}
    
    # Settings
    shuffle_questions: bool = True
    shuffle_options: bool = True
    show_results_immediately: bool = False
    allow_retakes: bool = True
    max_attempts: int = 3
    
    # Access
    created_by: str
    organization_id: Optional[str] = None
    is_public: bool = True
    
    # Analytics
    total_attempts: int = 0
    avg_score: float = 0.0
    completion_rate: float = 0.0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "question_sets"