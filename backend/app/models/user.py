"""
User model with authentication and profile management
"""

from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"
    PARENT = "parent"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class LearningPreferences(BaseModel):
    preferred_ai_model: str = "openai"
    difficulty_level: str = "adaptive"
    learning_style: str = "visual"
    study_time_preference: str = "morning"
    subjects_of_interest: List[str] = []

class UserProgress(BaseModel):
    total_xp: int = 0
    current_level: int = 1
    streak_days: int = 0
    lessons_completed: int = 0
    quizzes_completed: int = 0
    achievements_earned: List[str] = []
    last_activity: Optional[datetime] = None

class UserStats(BaseModel):
    total_study_time: int = 0  # in minutes
    avg_session_time: float = 0.0
    total_questions_answered: int = 0
    correct_answers: int = 0
    accuracy_rate: float = 0.0
    subjects_mastered: List[str] = []

class User(Document):
    """User document model"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    email: Indexed(EmailStr, unique=True)
    username: Indexed(str, unique=True)
    full_name: str
    
    # Authentication
    hashed_password: str
    is_verified: bool = False
    verification_token: Optional[str] = None
    reset_token: Optional[str] = None
    
    # Profile
    role: UserRole = UserRole.STUDENT
    status: UserStatus = UserStatus.ACTIVE
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    grade_level: Optional[str] = None
    school: Optional[str] = None
    
    # Organization
    organization_id: Optional[str] = None
    parent_id: Optional[str] = None  # For student-parent relationship
    
    # Learning Data
    preferences: LearningPreferences = Field(default_factory=LearningPreferences)
    progress: UserProgress = Field(default_factory=UserProgress)
    stats: UserStats = Field(default_factory=UserStats)
    
    # Study Groups
    study_groups: List[str] = []  # List of study group IDs
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Settings
    settings: Dict[str, Any] = {}
    
    class Settings:
        collection = "users"
        indexes = [
            [("email", 1)],
            [("username", 1)],
            [("organization_id", 1)],
            [("role", 1)],
            [("created_at", -1)]
        ]

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    username: str
    full_name: str
    password: str
    role: UserRole = UserRole.STUDENT
    grade_level: Optional[str] = None
    school: Optional[str] = None

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    grade_level: Optional[str] = None
    school: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[LearningPreferences] = None

class UserResponse(BaseModel):
    """Schema for user response (excluding sensitive data)"""
    id: str
    email: str
    username: str
    full_name: str
    role: UserRole
    status: UserStatus
    avatar_url: Optional[str]
    bio: Optional[str]
    grade_level: Optional[str]
    school: Optional[str]
    progress: UserProgress
    stats: UserStats
    created_at: datetime
    last_login: Optional[datetime]