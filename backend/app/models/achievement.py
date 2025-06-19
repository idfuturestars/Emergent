"""
Achievement & Gamification models
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class BadgeRarity(str, Enum):
    COMMON = "common"
    RARE = "rare" 
    EPIC = "epic"
    LEGENDARY = "legendary"

class AchievementType(str, Enum):
    LEARNING = "learning"
    SOCIAL = "social"
    STREAK = "streak"
    SPECIAL = "special"
    SEASONAL = "seasonal"

class Badge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon_url: str
    rarity: BadgeRarity
    xp_reward: int = 0

class Achievement(Document):
    """Achievement/Badge system"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    name: str
    description: str
    
    # Configuration
    achievement_type: AchievementType
    badge: Badge
    
    # Requirements
    requirements: Dict[str, Any] = {}  # Flexible requirements structure
    hidden: bool = False  # Hidden until unlocked
    
    # Rewards
    xp_reward: int = 0
    special_reward: Optional[str] = None
    
    # Metadata
    created_by: str
    organization_id: Optional[str] = None
    is_active: bool = True
    
    # Analytics
    total_earned: int = 0
    rarity_percentage: float = 0.0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "achievements"
        indexes = [
            [("achievement_type", 1)],
            [("organization_id", 1)],
            [("created_at", -1)]
        ]

class UserAchievement(Document):
    """User's earned achievements"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    achievement_id: str
    
    # Earning Details
    earned_at: datetime = Field(default_factory=datetime.utcnow)
    xp_earned: int = 0
    
    # Context
    session_id: Optional[str] = None
    trigger_event: Optional[str] = None
    
    # Display
    is_showcased: bool = False  # Featured on profile
    
    class Settings:
        collection = "user_achievements"
        indexes = [
            [("user_id", 1)],
            [("achievement_id", 1)],
            [("earned_at", -1)]
        ]

class Leaderboard(Document):
    """Leaderboard for rankings"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    name: str
    description: str
    
    # Configuration
    metric: str  # xp, streak, accuracy, etc.
    time_period: str  # daily, weekly, monthly, all_time
    category: str  # subject, grade_level, organization
    
    # Filtering
    subject: Optional[str] = None
    grade_level: Optional[str] = None
    organization_id: Optional[str] = None
    
    # Entries
    entries: List[Dict[str, Any]] = []  # [{user_id, score, rank, user_info}]
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Settings
    max_entries: int = 100
    is_active: bool = True
    
    class Settings:
        collection = "leaderboards"
        indexes = [
            [("metric", 1)],
            [("time_period", 1)],
            [("category", 1)],
            [("organization_id", 1)],
            [("last_updated", -1)]
        ]