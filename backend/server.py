from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import logging
import uuid
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import openai
import json
from enum import Enum
import bcrypt
import redis
from collections import defaultdict

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configuration
MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']
JWT_SECRET = os.environ['JWT_SECRET']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# Initialize clients
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
openai.api_key = OPENAI_API_KEY

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# FastAPI app setup
app = FastAPI(title="StarGuide API", description="IDFS PathwayIQ™ Educational Platform")
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# MODELS & ENUMS
# ============================================================================

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_BLANK = "fill_blank"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"

class QuestionDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class BadgeRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

# User Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.STUDENT
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    role: UserRole
    full_name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    xp: int = 0
    level: int = 1
    streak_days: int = 0
    last_active: Optional[datetime] = None
    avatar: Optional[str] = None
    badges: List[str] = []
    study_groups: List[str] = []

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Learning Models
class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    question_type: QuestionType
    difficulty: QuestionDifficulty
    subject: str
    topic: str
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: str
    explanation: str
    points: int = 10
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = []

class QuestionCreate(BaseModel):
    question_text: str
    question_type: QuestionType
    difficulty: QuestionDifficulty
    subject: str
    topic: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    points: int = 10
    tags: List[str] = []

class UserAnswer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    question_id: str
    answer: str
    is_correct: bool
    points_earned: int
    time_taken: int  # seconds
    answered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StudySession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subject: str
    topic: str
    questions_answered: int = 0
    correct_answers: int = 0
    total_points: int = 0
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None

# Study Group Models
class StudyGroup(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    subject: str
    created_by: str
    members: List[str] = []
    max_members: int = 20
    is_private: bool = False
    join_code: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StudyGroupCreate(BaseModel):
    name: str
    description: str
    subject: str
    max_members: int = 20
    is_private: bool = False

class StudyGroupJoin(BaseModel):
    join_code: str

# Quiz Arena Models
class QuizRoom(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subject: str
    difficulty: QuestionDifficulty
    max_participants: int = 10
    questions_per_game: int = 10
    time_per_question: int = 30  # seconds
    created_by: str
    participants: List[str] = []
    is_active: bool = True
    room_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    start_time: Optional[datetime] = None

class QuizRoomCreate(BaseModel):
    name: str
    subject: str
    difficulty: QuestionDifficulty
    max_participants: int = 10
    questions_per_game: int = 10
    time_per_question: int = 30

class QuizParticipant(BaseModel):
    user_id: str
    username: str
    score: int = 0
    answers: List[Dict] = []
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Badge Models
class Badge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon: str
    rarity: BadgeRarity
    requirements: Dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserBadge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    badge_id: str
    earned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Chat Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    room_id: str  # study_group_id or quiz_room_id
    user_id: str
    username: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_type: str = "text"  # text, image, file

class AIConversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    messages: List[Dict[str, str]] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Analytics Models
class UserAnalytics(BaseModel):
    user_id: str
    total_questions_answered: int = 0
    correct_answers: int = 0
    accuracy_rate: float = 0.0
    total_study_time: int = 0  # minutes
    subjects_studied: List[str] = []
    favorite_subject: Optional[str] = None
    weekly_activity: List[int] = [0] * 7  # Last 7 days
    learning_streak: int = 0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================================================
# AUTHENTICATION UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise credentials_exception
    return User(**user)

# ============================================================================
# AI HELPER FUNCTIONS
# ============================================================================

async def get_ai_response(messages: List[Dict[str, str]], user_context: Optional[Dict] = None) -> str:
    try:
        system_prompt = """You are StarGuide AI, an intelligent tutoring assistant powered by IDFS PathwayIQ™. 
        You help students learn through personalized guidance, explanations, and encouragement.
        
        Guidelines:
        - Be encouraging and supportive
        - Provide clear, educational explanations
        - Ask follow-up questions to ensure understanding
        - Adapt to the student's learning level
        - Focus on building confidence and knowledge
        """
        
        if user_context:
            system_prompt += f"\nStudent context: Level {user_context.get('level', 1)}, XP: {user_context.get('xp', 0)}"
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI response error: {e}")
        return "I'm sorry, I'm having trouble responding right now. Please try again later."

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    hashed_password = hash_password(user_data.password)
    user_dict = user_data.dict()
    user = User(**user_dict)
    
    # Create user document with password
    user_doc = user.dict()
    user_doc["password"] = hashed_password
    
    await db.users.insert_one(user_doc)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_obj = User(**user)
    access_token = create_access_token(data={"sub": user_obj.id})
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# ============================================================================
# LEARNING ENGINE ENDPOINTS
# ============================================================================

@api_router.post("/questions", response_model=Question)
async def create_question(question_data: QuestionCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only teachers and admins can create questions")
    
    question_dict = question_data.dict()
    question_dict["created_by"] = current_user.id
    question = Question(**question_dict)
    
    await db.questions.insert_one(question.dict())
    return question

@api_router.get("/questions", response_model=List[Question])
async def get_questions(
    subject: Optional[str] = None,
    difficulty: Optional[QuestionDifficulty] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    query = {}
    if subject:
        query["subject"] = subject
    if difficulty:
        query["difficulty"] = difficulty
    
    questions = await db.questions.find(query).limit(limit).to_list(limit)
    return [Question(**q) for q in questions]

@api_router.post("/questions/{question_id}/answer")
async def submit_answer(
    question_id: str,
    answer: str,
    current_user: User = Depends(get_current_user)
):
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_correct = answer.lower().strip() == question["correct_answer"].lower().strip()
    points_earned = question["points"] if is_correct else 0
    
    user_answer = UserAnswer(
        user_id=current_user.id,
        question_id=question_id,
        answer=answer,
        is_correct=is_correct,
        points_earned=points_earned,
        time_taken=30  # TODO: Track actual time
    )
    
    await db.user_answers.insert_one(user_answer.dict())
    
    # Update user XP and level
    if is_correct:
        new_xp = current_user.xp + points_earned
        new_level = (new_xp // 100) + 1
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"xp": new_xp, "level": new_level}}
        )
    
    return {
        "correct": is_correct,
        "points_earned": points_earned,
        "explanation": question["explanation"]
    }

# ============================================================================
# STUDY GROUPS ENDPOINTS
# ============================================================================

@api_router.post("/study-groups", response_model=StudyGroup)
async def create_study_group(group_data: StudyGroupCreate, current_user: User = Depends(get_current_user)):
    group_dict = group_data.dict()
    group_dict["created_by"] = current_user.id
    group_dict["members"] = [current_user.id]
    
    if group_data.is_private:
        group_dict["join_code"] = str(uuid.uuid4())[:8].upper()
    
    study_group = StudyGroup(**group_dict)
    await db.study_groups.insert_one(study_group.dict())
    return study_group

@api_router.get("/study-groups", response_model=List[StudyGroup])
async def get_study_groups(current_user: User = Depends(get_current_user)):
    groups = await db.study_groups.find({"members": current_user.id}).to_list(100)
    return [StudyGroup(**g) for g in groups]

@api_router.post("/study-groups/{group_id}/join")
async def join_study_group(group_id: str, current_user: User = Depends(get_current_user)):
    group = await db.study_groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Study group not found")
    
    if current_user.id in group["members"]:
        raise HTTPException(status_code=400, detail="Already a member")
    
    if len(group["members"]) >= group["max_members"]:
        raise HTTPException(status_code=400, detail="Group is full")
    
    await db.study_groups.update_one(
        {"id": group_id},
        {"$push": {"members": current_user.id}}
    )
    
    return {"message": "Successfully joined study group"}

# ============================================================================
# QUIZ ARENA ENDPOINTS
# ============================================================================

@api_router.post("/quiz-rooms", response_model=QuizRoom)
async def create_quiz_room(room_data: QuizRoomCreate, current_user: User = Depends(get_current_user)):
    room_dict = room_data.dict()
    room_dict["created_by"] = current_user.id
    room_dict["participants"] = [current_user.id]
    
    quiz_room = QuizRoom(**room_dict)
    await db.quiz_rooms.insert_one(quiz_room.dict())
    return quiz_room

@api_router.get("/quiz-rooms", response_model=List[QuizRoom])
async def get_quiz_rooms(current_user: User = Depends(get_current_user)):
    rooms = await db.quiz_rooms.find({"is_active": True}).to_list(100)
    return [QuizRoom(**r) for r in rooms]

@api_router.post("/quiz-rooms/{room_code}/join")
async def join_quiz_room(room_code: str, current_user: User = Depends(get_current_user)):
    room = await db.quiz_rooms.find_one({"room_code": room_code})
    if not room:
        raise HTTPException(status_code=404, detail="Quiz room not found")
    
    if current_user.id in room["participants"]:
        raise HTTPException(status_code=400, detail="Already joined")
    
    if len(room["participants"]) >= room["max_participants"]:
        raise HTTPException(status_code=400, detail="Room is full")
    
    await db.quiz_rooms.update_one(
        {"room_code": room_code},
        {"$push": {"participants": current_user.id}}
    )
    
    return {"message": "Successfully joined quiz room"}

# ============================================================================
# AI TUTOR ENDPOINTS
# ============================================================================

@api_router.post("/ai/chat")
async def chat_with_ai(
    message: str,
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Get or create conversation
    conversation = await db.ai_conversations.find_one({
        "user_id": current_user.id,
        "session_id": session_id
    })
    
    if not conversation:
        conversation = AIConversation(
            user_id=current_user.id,
            session_id=session_id,
            messages=[]
        )
    else:
        conversation = AIConversation(**conversation)
    
    # Add user message
    conversation.messages.append({"role": "user", "content": message})
    
    # Get AI response
    user_context = {
        "level": current_user.level,
        "xp": current_user.xp,
        "role": current_user.role
    }
    
    ai_response = await get_ai_response(conversation.messages, user_context)
    conversation.messages.append({"role": "assistant", "content": ai_response})
    conversation.updated_at = datetime.now(timezone.utc)
    
    # Save conversation
    await db.ai_conversations.replace_one(
        {"user_id": current_user.id, "session_id": session_id},
        conversation.dict(),
        upsert=True
    )
    
    return {
        "session_id": session_id,
        "response": ai_response,
        "context": user_context
    }

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@api_router.get("/analytics/dashboard")
async def get_dashboard_analytics(current_user: User = Depends(get_current_user)):
    # Get user answers
    answers = await db.user_answers.find({"user_id": current_user.id}).to_list(1000)
    
    total_questions = len(answers)
    correct_answers = sum(1 for a in answers if a.get("is_correct", False))
    accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Get study sessions
    sessions = await db.study_sessions.find({"user_id": current_user.id}).to_list(100)
    total_study_time = sum(s.get("duration_minutes", 0) for s in sessions)
    
    # Get study groups
    groups = await db.study_groups.find({"members": current_user.id}).to_list(100)
    
    # Convert MongoDB documents to dictionaries and handle ObjectId
    recent_activity = []
    if answers:
        for answer in answers[-10:]:
            # Convert ObjectId to string if present
            if "_id" in answer:
                answer["_id"] = str(answer["_id"])
            recent_activity.append(answer)
    
    return {
        "user_stats": {
            "level": current_user.level,
            "xp": current_user.xp,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "accuracy_rate": round(accuracy, 1),
            "total_study_time": total_study_time,
            "study_groups": len(groups),
            "badges_earned": len(current_user.badges)
        },
        "recent_activity": recent_activity,
        "weekly_progress": [0] * 7  # TODO: Implement weekly tracking
    }

# ============================================================================
# CHAT ENDPOINTS (for real-time features)
# ============================================================================

@api_router.get("/chat/{room_id}/messages")
async def get_chat_messages(
    room_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    messages = await db.chat_messages.find({"room_id": room_id}).sort("timestamp", -1).limit(limit).to_list(limit)
    return [ChatMessage(**m) for m in messages]

@api_router.post("/chat/{room_id}/message")
async def send_chat_message(
    room_id: str,
    message: str,
    current_user: User = Depends(get_current_user)
):
    chat_message = ChatMessage(
        room_id=room_id,
        user_id=current_user.id,
        username=current_user.username,
        message=message
    )
    
    await db.chat_messages.insert_one(chat_message.dict())
    return chat_message

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@api_router.get("/")
async def root():
    return {"message": "StarGuide API powered by IDFS PathwayIQ™", "version": "1.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

# Include router in main app
app.include_router(api_router)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("StarGuide API starting up...")
    
    # Create default badges
    default_badges = [
        {"name": "First Steps", "description": "Complete your first question", "icon": "🚀", "rarity": "common", "requirements": {"questions_answered": 1}},
        {"name": "Scholar", "description": "Answer 100 questions correctly", "icon": "📚", "rarity": "rare", "requirements": {"correct_answers": 100}},
        {"name": "Streak Master", "description": "Maintain a 7-day learning streak", "icon": "🔥", "rarity": "epic", "requirements": {"streak_days": 7}},
        {"name": "Quiz Champion", "description": "Win 10 quiz battles", "icon": "🏆", "rarity": "legendary", "requirements": {"quiz_wins": 10}}
    ]
    
    for badge_data in default_badges:
        existing = await db.badges.find_one({"name": badge_data["name"]})
        if not existing:
            badge = Badge(**badge_data)
            await db.badges.insert_one(badge.dict())

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    client.close()
    logger.info("StarGuide API shutting down...")