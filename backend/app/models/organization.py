"""
Organization model for multi-tenant architecture
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class OrganizationTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class OrganizationSettings(BaseModel):
    allow_student_registration: bool = True
    require_email_verification: bool = True
    enable_parent_dashboard: bool = False
    custom_branding: Dict[str, str] = {}
    ai_models_enabled: List[str] = ["openai"]

class Organization(Document):
    """Organization document for multi-tenancy"""
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    name: Indexed(str, unique=True)
    slug: Indexed(str, unique=True)
    
    # Details
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    
    # Subscription
    tier: OrganizationTier = OrganizationTier.FREE
    max_users: int = 50
    max_storage_gb: int = 1
    
    # Admin
    admin_user_id: str
    
    # Settings
    settings: OrganizationSettings = Field(default_factory=OrganizationSettings)
    
    # Statistics
    total_users: int = 0
    active_users: int = 0
    total_sessions: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "organizations"
        indexes = [
            [("name", 1)],
            [("slug", 1)],
            [("admin_user_id", 1)],
            [("created_at", -1)]
        ]