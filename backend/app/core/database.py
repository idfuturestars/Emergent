"""
Database configuration and connection management
"""

import motor.motor_asyncio
from beanie import init_beanie
import asyncio
from app.core.config import settings
from app.models.user import User
from app.models.organization import Organization
from app.models.study_group import StudyGroup
from app.models.question import Question
from app.models.session import Session
from app.models.achievement import Achievement
from app.models.analytics import Analytics
from app.models.conversation import Conversation

# MongoDB client
client = None
database = None

async def init_db():
    """Initialize database connection and models"""
    global client, database
    
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URL)
    database = client[settings.DB_NAME]
    
    # Initialize Beanie with document models
    await init_beanie(
        database=database,
        document_models=[
            User,
            Organization, 
            StudyGroup,
            Question,
            Session,
            Achievement,
            Analytics,
            Conversation
        ]
    )
    
    print(f"✅ Database initialized: {settings.DB_NAME}")

async def close_db():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("✅ Database connection closed")

async def get_database():
    """Get database instance"""
    return database