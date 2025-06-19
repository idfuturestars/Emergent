"""
Study Group model for collaborative learning
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class StudyGroupType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    CLASS = "class"

class GroupMember(BaseModel):
    user_id: str
    role: str = "member"  # member, moderator, admin
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class StudySession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = 60
    created_by: str
    participants: List[str] = []

class StudyGroup(Document):
    """Study Group document model"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    name: str
    description: Optional[str] = None
    
    # Configuration
    group_type: StudyGroupType = StudyGroupType.PUBLIC
    subject: str
    grade_level: Optional[str] = None
    max_members: int = 20
    
    # Access
    join_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    created_by: str
    organization_id: Optional[str] = None
    
    # Members
    members: List[GroupMember] = []
    member_count: int = 0
    
    # Sessions
    upcoming_sessions: List[StudySession] = []
    total_sessions: int = 0
    
    # Activity
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    # Settings
    settings: Dict[str, Any] = {
        "allow_voice_chat": True,
        "allow_screen_share": True,
        "auto_record_sessions": False,
        "require_approval": False
    }
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "study_groups"
        indexes = [
            [("name", 1)],
            [("subject", 1)],
            [("created_by", 1)],
            [("organization_id", 1)],
            [("join_code", 1)],
            [("created_at", -1)]
        ]