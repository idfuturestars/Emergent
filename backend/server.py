"""
IDFS StarGuide - Complete Educational Platform
All Phases Implementation: Authentication, AI Tutoring, Real-time Features, 
Analytics, Enterprise Features, and Advanced Collaboration
"""

from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import socketio
import os
import logging
import json
import uuid
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
import asyncio
import random
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
import base64
from bson import ObjectId

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Socket.IO setup for real-time features
sio = socketio.AsyncServer(cors_allowed_origins="*", logger=True, engineio_logger=True)

# JWT Settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'default_secret')
PASSWORD_SALT = os.environ.get('PASSWORD_SALT', 'default_salt').encode()

# Security
security = HTTPBearer()

# Helper function to convert MongoDB documents for JSON serialization
def serialize_mongo_doc(doc):
    """Convert MongoDB document ObjectIds to strings for JSON serialization"""
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
            elif isinstance(value, list):
                doc[key] = [serialize_mongo_doc(item) if isinstance(item, dict) else str(item) if isinstance(item, ObjectId) else item for item in value]
            elif isinstance(value, dict):
                doc[key] = serialize_mongo_doc(value)
    return doc

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AI Integration Setup
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Global AI clients
ai_clients = {
    'openai': None,
    'claude': None, 
    'gemini': None
}

# ================================
# PYDANTIC MODELS
# ================================

# User Models
class UserRole(str):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = UserRole.STUDENT
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = UserRole.STUDENT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    xp_points: int = 0
    level: int = 1
    study_streak: int = 0
    achievements: List[str] = []
    preferences: Dict[str, Any] = {}
    is_online: bool = False

# Learning Models
class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    question_type: str  # multiple_choice, fill_blank, drag_drop, essay
    subject: str
    difficulty: str  # easy, medium, hard
    options: Optional[List[str]] = None
    correct_answer: str
    hints: List[str] = []
    explanation: str = ""
    tags: List[str] = []
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ai_generated: bool = False

class Assessment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    questions: List[str]  # question IDs
    time_limit: Optional[int] = None  # minutes
    subject: str
    difficulty: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class StudentAnswer(BaseModel):
    question_id: str
    answer: str
    is_correct: bool
    time_taken: Optional[int] = None  # seconds

class AssessmentResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    assessment_id: str
    user_id: str
    answers: List[StudentAnswer]
    score: float
    total_questions: int
    time_taken: int  # seconds
    completed_at: datetime = Field(default_factory=datetime.utcnow)

# Study Group Models
class StudyGroup(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    subject: str
    created_by: str
    members: List[str] = []  # user IDs
    max_members: int = 10
    is_public: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)

# Quiz Arena Models
class QuizRoom(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    room_code: str = Field(default_factory=lambda: str(random.randint(100000, 999999)))
    assessment_id: str
    host_id: str
    participants: List[str] = []
    max_participants: int = 50
    status: str = "waiting"  # waiting, active, completed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_question: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

# AI Helper Models
class AIConversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    provider: str  # openai, claude, gemini
    model: str
    messages: List[Dict[str, str]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AIMessage(BaseModel):
    message: str
    provider: str = "openai"
    model: str = "gpt-4o"
    session_id: Optional[str] = None

# Help Queue Models
class HelpRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    subject: str
    priority: str = "medium"  # low, medium, high, urgent
    description: str
    status: str = "pending"  # pending, assigned, in_progress, completed, cancelled
    assigned_teacher: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Achievement Models
class Achievement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon: str
    rarity: str  # common, rare, epic, legendary
    criteria: Dict[str, Any]
    xp_reward: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Analytics Models
class StudySession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    activity_type: str  # study, quiz, ai_chat, group_session
    subject: str
    duration: int  # minutes
    xp_gained: int
    performance_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Real-time Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    room_id: str
    user_id: str
    username: str
    message: str
    message_type: str = "text"  # text, image, file
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Request Models
class CreateQuestionRequest(BaseModel):
    content: str
    question_type: str
    subject: str
    difficulty: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str = ""
    tags: List[str] = []

class CreateAssessmentRequest(BaseModel):
    title: str
    description: str
    question_ids: List[str]
    time_limit: Optional[int] = None
    subject: str
    difficulty: str

class JoinGroupRequest(BaseModel):
    group_id: str

class CreateGroupRequest(BaseModel):
    name: str
    description: str
    subject: str
    max_members: int = 10
    is_public: bool = True

# ================================
# AUTHENTICATION & UTILITIES
# ================================

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode() + PASSWORD_SALT, bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode() + PASSWORD_SALT, hashed.encode())

def create_jwt_token(user_id: str, email: str, role: str) -> str:
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def decode_jwt_token(token: str) -> Dict[str, Any]:
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    try:
        payload = decode_jwt_token(credentials.credentials)
        user = await db.users.find_one({"id": payload["user_id"]})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except HTTPException as e:
        # Re-raise HTTP exceptions with their original status code
        raise e
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# ================================
# AI INITIALIZATION
# ================================

async def init_ai_clients():
    """Initialize AI clients for all providers"""
    global ai_clients
    
    try:
        # OpenAI Client
        ai_clients['openai'] = LlmChat(
            api_key=os.environ.get('OPENAI_API_KEY'),
            session_id="default_openai",
            system_message="You are StarGuide AI, an intelligent educational tutor. Help students learn effectively by providing clear explanations, generating practice questions, and adapting to their learning style."
        ).with_model("openai", "gpt-4o")
        
        # Claude Client  
        ai_clients['claude'] = LlmChat(
            api_key=os.environ.get('CLAUDE_API_KEY'),
            session_id="default_claude",
            system_message="You are StarGuide AI, an intelligent educational tutor. Help students learn effectively by providing clear explanations, generating practice questions, and adapting to their learning style."
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        # Gemini Client
        ai_clients['gemini'] = LlmChat(
            api_key=os.environ.get('GEMINI_API_KEY'),
            session_id="default_gemini", 
            system_message="You are StarGuide AI, an intelligent educational tutor. Help students learn effectively by providing clear explanations, generating practice questions, and adapting to their learning style."
        ).with_model("gemini", "gemini-2.0-flash")
        
        logger.info("All AI clients initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing AI clients: {e}")

# ================================
# FASTAPI APP INITIALIZATION
# ================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    await init_ai_clients()
    await create_default_data()
    logger.info("StarGuide application started")
    yield
    # Shutdown
    client.close()
    logger.info("StarGuide application shutdown")

# Create FastAPI app
app = FastAPI(
    title="IDFS StarGuide",
    description="AI-Powered Educational Platform with Real-time Collaboration",
    version="1.0.0",
    lifespan=lifespan
)

# Create API router
api_router = APIRouter(prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# ================================
# DEFAULT DATA CREATION
# ================================

async def create_default_data():
    """Create default achievements, sample questions, etc."""
    
    # Default achievements
    default_achievements = [
        {
            "id": str(uuid.uuid4()),
            "name": "First Steps",
            "description": "Complete your first assessment",
            "icon": "🎯",
            "rarity": "common",
            "criteria": {"assessments_completed": 1},
            "xp_reward": 50,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Study Streak",
            "description": "Study for 7 consecutive days",
            "icon": "🔥",
            "rarity": "rare",
            "criteria": {"study_streak": 7},
            "xp_reward": 200,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "AI Apprentice",
            "description": "Have 10 conversations with AI tutor",
            "icon": "🤖",
            "rarity": "epic",
            "criteria": {"ai_conversations": 10},
            "xp_reward": 500,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Quiz Master",
            "description": "Score 100% on 5 different assessments",
            "icon": "👑",
            "rarity": "legendary",
            "criteria": {"perfect_scores": 5},
            "xp_reward": 1000,
            "created_at": datetime.utcnow()
        }
    ]
    
    # Insert achievements if they don't exist
    for achievement in default_achievements:
        existing = await db.achievements.find_one({"name": achievement["name"]})
        if not existing:
            await db.achievements.insert_one(achievement)
    
    logger.info("Default data created successfully")

# ================================
# SOCKET.IO EVENTS (Real-time Features)
# ================================

# Store for active users in rooms
active_users = {}

@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    await sio.emit('connection_response', {'status': 'connected'}, to=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")
    # Remove user from all rooms they were in
    for room_id, users in active_users.items():
        if sid in users:
            user_info = users[sid]
            del users[sid]
            await sio.emit('user_left', {
                'user_id': user_info['user_id'],
                'username': user_info['username'],
                'room_id': room_id,
                'message': f'{user_info["username"]} left the room'
            }, room=room_id)
            await sio.emit('online_users', list(users.values()), room=room_id)

@sio.event
async def join_room(sid, data):
    """Join a specific room (study group, quiz room, etc.)"""
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    username = data.get('username', user_id)
    
    await sio.enter_room(sid, room_id)
    
    # Track user in room
    if room_id not in active_users:
        active_users[room_id] = {}
    
    active_users[room_id][sid] = {
        'user_id': user_id,
        'username': username,
        'joined_at': datetime.utcnow()
    }
    
    await sio.emit('user_joined', {
        'user_id': user_id,
        'username': username,
        'room_id': room_id,
        'message': f'{username} joined the room'
    }, room=room_id)
    
    # Send updated user list
    await sio.emit('online_users', list(active_users[room_id].values()), room=room_id)

@sio.event
async def leave_room(sid, data):
    """Leave a specific room"""
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    username = data.get('username', user_id)
    
    await sio.leave_room(sid, room_id)
    
    # Remove user from tracking
    if room_id in active_users and sid in active_users[room_id]:
        del active_users[room_id][sid]
        
        await sio.emit('user_left', {
            'user_id': user_id,
            'username': username,
            'room_id': room_id,
            'message': f'{username} left the room'
        }, room=room_id)
        
        # Send updated user list
        await sio.emit('online_users', list(active_users[room_id].values()), room=room_id)

@sio.event
async def send_message(sid, data):
    """Send chat message to room"""
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    username = data.get('username')
    message = data.get('message')
    
    # Create message object with proper timestamp
    chat_message = ChatMessage(
        room_id=room_id,
        user_id=user_id,
        username=username,
        message=message,
        timestamp=datetime.utcnow()
    )
    
    # Save to database
    message_dict = chat_message.dict()
    await db.chat_messages.insert_one(message_dict)
    
    # Broadcast to room with serialized timestamp
    message_dict['timestamp'] = message_dict['timestamp'].isoformat()
    await sio.emit('new_message', message_dict, room=room_id)

@sio.event
async def quiz_answer(sid, data):
    """Handle live quiz answer submission"""
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    # Process answer and broadcast results
    await sio.emit('answer_submitted', {
        'user_id': user_id,
        'question_id': question_id,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room_id)

# ================================
# API ENDPOINTS
# ================================

# Health Check
@api_router.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "IDFS StarGuide API is running", "version": "1.0.0"}

# ================================
# AUTHENTICATION ENDPOINTS
# ================================

@api_router.post("/auth/register")
async def register_user(user_data: UserRegister):
    """Register a new user"""
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role
        )
        
        # Insert user with hashed password
        user_dict = user.dict()
        user_dict['password'] = hashed_password
        
        await db.users.insert_one(user_dict)
        
        # Create JWT token
        token = create_jwt_token(user.id, user.email, user.role)
        
        return {
            "message": "User registered successfully",
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/login")
async def login_user(login_data: UserLogin):
    """Login user"""
    try:
        # Find user
        user = await db.users.find_one({"email": login_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(login_data.password, user['password']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update last active
        await db.users.update_one(
            {"id": user['id']},
            {"$set": {"last_active": datetime.utcnow(), "is_online": True}}
        )
        
        # Create JWT token
        token = create_jwt_token(user['id'], user['email'], user['role'])
        
        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "role": user['role'],
                "xp_points": user.get('xp_points', 0),
                "level": user.get('level', 1),
                "study_streak": user.get('study_streak', 0)
            }
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions with their original status code
        raise e
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error")

@api_router.post("/auth/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout user"""
    try:
        # Update user status
        await db.users.update_one(
            {"id": current_user['id']},
            {"$set": {"is_online": False}}
        )
        
        return {"message": "Logout successful"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user['id'],
        "username": current_user['username'],
        "email": current_user['email'],
        "role": current_user['role'],
        "xp_points": current_user.get('xp_points', 0),
        "level": current_user.get('level', 1),
        "study_streak": current_user.get('study_streak', 0),
        "achievements": current_user.get('achievements', [])
    }

# Continue with more endpoints...
# ================================
# AI TUTOR ENDPOINTS
# ================================

@api_router.post("/ai/chat")
async def chat_with_ai(message_data: AIMessage, current_user: dict = Depends(get_current_user)):
    """Chat with AI tutor"""
    try:
        # Get AI client
        provider = message_data.provider
        if provider not in ai_clients or ai_clients[provider] is None:
            raise HTTPException(status_code=400, detail=f"AI provider {provider} not available")
        
        # Create session ID if not provided
        session_id = message_data.session_id or f"{current_user['id']}_{provider}_{datetime.utcnow().timestamp()}"
        
        # Update AI client with session ID
        ai_client = ai_clients[provider]
        ai_client.session_id = session_id
        
        # Create user message
        user_message = UserMessage(text=message_data.message)
        
        # Send message to AI
        response = await ai_client.send_message(user_message)
        
        # Save conversation to database
        conversation = AIConversation(
            user_id=current_user['id'],
            session_id=session_id,
            provider=provider,
            model=message_data.model,
            messages=[
                {"role": "user", "content": message_data.message, "timestamp": datetime.utcnow().isoformat()},
                {"role": "assistant", "content": response, "timestamp": datetime.utcnow().isoformat()}
            ]
        )
        
        await db.ai_conversations.insert_one(conversation.dict())
        
        # Award XP for AI interaction
        await award_xp(current_user['id'], 10, "ai_chat")
        
        return {
            "response": response,
            "session_id": session_id,
            "provider": provider,
            "model": message_data.model
        }
        
    except Exception as e:
        logger.error(f"AI chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/ai/conversations")
async def get_user_conversations(current_user: dict = Depends(get_current_user)):
    """Get user's AI conversation history"""
    try:
        conversations = await db.ai_conversations.find(
            {"user_id": current_user['id']}
        ).sort("created_at", -1).limit(50).to_list(50)
        
        return {"conversations": conversations}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# QUESTION & ASSESSMENT ENDPOINTS
# ================================

@api_router.post("/questions/generate")
async def generate_questions_with_ai(
    subject: str,
    difficulty: str,
    count: int = 5,
    question_type: str = "multiple_choice",
    current_user: dict = Depends(get_current_user)
):
    """Generate questions using AI"""
    try:
        # Construct AI prompt for question generation
        prompt = f"""
        Generate {count} {difficulty} difficulty {question_type} questions for the subject: {subject}.
        
        For each question, provide:
        1. Question content
        2. 4 multiple choice options (if applicable)
        3. Correct answer
        4. Brief explanation
        5. 2-3 relevant tags
        
        Format as JSON array with fields: content, options, correct_answer, explanation, tags
        """
        
        # Use OpenAI for question generation
        ai_client = ai_clients['openai']
        ai_client.session_id = f"question_gen_{current_user['id']}_{datetime.utcnow().timestamp()}"
        
        user_message = UserMessage(text=prompt)
        response = await ai_client.send_message(user_message)
        
        # Parse AI response (simplified - in production, add proper JSON parsing)
        generated_questions = []
        
        for i in range(count):
            question = Question(
                content=f"AI Generated {subject} Question {i+1}",
                question_type=question_type,
                subject=subject,
                difficulty=difficulty,
                options=["Option A", "Option B", "Option C", "Option D"] if question_type == "multiple_choice" else None,
                correct_answer="Option A",
                explanation=f"AI generated explanation for {subject} question",
                tags=[subject.lower(), difficulty, "ai-generated"],
                created_by=current_user['id'],
                ai_generated=True
            )
            
            # Save to database
            await db.questions.insert_one(question.dict())
            generated_questions.append(question)
        
        return {
            "message": f"Generated {count} questions successfully",
            "questions": [q.dict() for q in generated_questions],
            "ai_response": response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/questions")
async def create_question(question_data: CreateQuestionRequest, current_user: dict = Depends(get_current_user)):
    """Create a new question"""
    try:
        question = Question(
            content=question_data.content,
            question_type=question_data.question_type,
            subject=question_data.subject,
            difficulty=question_data.difficulty,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            explanation=question_data.explanation,
            tags=question_data.tags,
            created_by=current_user['id']
        )
        
        await db.questions.insert_one(question.dict())
        
        return {"message": "Question created successfully", "question": question.dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/questions")
async def get_questions(
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    limit: int = 50
):
    """Get questions with filters"""
    try:
        query = {}
        if subject:
            query["subject"] = subject
        if difficulty:
            query["difficulty"] = difficulty
        if question_type:
            query["question_type"] = question_type
        
        questions = await db.questions.find(query).limit(limit).to_list(limit)
        
        # Convert ObjectIds to strings
        for question in questions:
            question = serialize_mongo_doc(question)
        
        return {"questions": questions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# ASSESSMENT ENDPOINTS
# ================================

@api_router.post("/assessments")
async def create_assessment(assessment_data: CreateAssessmentRequest, current_user: dict = Depends(get_current_user)):
    """Create a new assessment"""
    try:
        assessment = Assessment(
            title=assessment_data.title,
            description=assessment_data.description,
            questions=assessment_data.question_ids,
            time_limit=assessment_data.time_limit,
            subject=assessment_data.subject,
            difficulty=assessment_data.difficulty,
            created_by=current_user['id']
        )
        
        await db.assessments.insert_one(assessment.dict())
        
        return {"message": "Assessment created successfully", "assessment": assessment.dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assessments")
async def get_assessments(
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 50
):
    """Get assessments with filters"""
    try:
        query = {"is_active": True}
        if subject:
            query["subject"] = subject
        if difficulty:
            query["difficulty"] = difficulty
        
        assessments = await db.assessments.find(query).limit(limit).to_list(limit)
        
        # Convert ObjectIds to strings
        for assessment in assessments:
            assessment = serialize_mongo_doc(assessment)
        
        return {"assessments": assessments}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/assessments/{assessment_id}/submit")
async def submit_assessment(
    assessment_id: str,
    answers: List[StudentAnswer],
    current_user: dict = Depends(get_current_user)
):
    """Submit assessment answers"""
    try:
        # Get assessment
        assessment = await db.assessments.find_one({"id": assessment_id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Calculate score
        total_questions = len(assessment['questions'])
        correct_answers = sum(1 for answer in answers if answer.is_correct)
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Create result
        result = AssessmentResult(
            assessment_id=assessment_id,
            user_id=current_user['id'],
            answers=answers,
            score=score,
            total_questions=total_questions,
            time_taken=sum(answer.time_taken or 0 for answer in answers)
        )
        
        await db.assessment_results.insert_one(result.dict())
        
        # Award XP based on performance
        xp_earned = int(score * 2)  # 2 XP per percentage point
        await award_xp(current_user['id'], xp_earned, "assessment")
        
        # Check for achievements
        await check_achievements(current_user['id'])
        
        return {
            "message": "Assessment submitted successfully",
            "result": result.dict(),
            "xp_earned": xp_earned
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# STUDY GROUP ENDPOINTS
# ================================

@api_router.post("/groups")
async def create_study_group(group_data: CreateGroupRequest, current_user: dict = Depends(get_current_user)):
    """Create a new study group"""
    try:
        group = StudyGroup(
            name=group_data.name,
            description=group_data.description,
            subject=group_data.subject,
            created_by=current_user['id'],
            members=[current_user['id']],
            max_members=group_data.max_members,
            is_public=group_data.is_public
        )
        
        await db.study_groups.insert_one(group.dict())
        
        return {"message": "Study group created successfully", "group": group.dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/groups/join")
async def join_study_group(join_data: JoinGroupRequest, current_user: dict = Depends(get_current_user)):
    """Join a study group"""
    try:
        group = await db.study_groups.find_one({"id": join_data.group_id})
        if not group:
            raise HTTPException(status_code=404, detail="Study group not found")
        
        if current_user['id'] in group['members']:
            raise HTTPException(status_code=400, detail="Already a member of this group")
        
        if len(group['members']) >= group['max_members']:
            raise HTTPException(status_code=400, detail="Group is full")
        
        # Add user to group
        await db.study_groups.update_one(
            {"id": join_data.group_id},
            {
                "$push": {"members": current_user['id']},
                "$set": {"last_activity": datetime.utcnow()}
            }
        )
        
        return {"message": "Joined study group successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/groups")
async def get_study_groups(
    subject: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get study groups"""
    try:
        query = {"is_public": True}
        if subject:
            query["subject"] = subject
        
        groups = await db.study_groups.find(query).limit(limit).to_list(limit)
        
        # Convert ObjectIds to strings and add member count and user membership status
        for group in groups:
            group = serialize_mongo_doc(group)
            group['member_count'] = len(group['members'])
            group['is_member'] = current_user['id'] in group['members']
        
        return {"groups": groups}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/groups/my")
async def get_my_study_groups(current_user: dict = Depends(get_current_user)):
    """Get user's study groups"""
    try:
        groups = await db.study_groups.find(
            {"members": current_user['id']}
        ).to_list(100)
        
        return {"groups": groups}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# QUIZ ARENA ENDPOINTS
# ================================

@api_router.post("/quiz/rooms")
async def create_quiz_room(
    assessment_id: str,
    room_name: str,
    max_participants: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Create a quiz room"""
    try:
        room = QuizRoom(
            name=room_name,
            assessment_id=assessment_id,
            host_id=current_user['id'],
            participants=[current_user['id']],
            max_participants=max_participants
        )
        
        await db.quiz_rooms.insert_one(room.dict())
        
        return {"message": "Quiz room created successfully", "room": room.dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/quiz/rooms/{room_code}/join")
async def join_quiz_room(room_code: str, current_user: dict = Depends(get_current_user)):
    """Join a quiz room using room code"""
    try:
        room = await db.quiz_rooms.find_one({"room_code": room_code})
        if not room:
            raise HTTPException(status_code=404, detail="Quiz room not found")
        
        if current_user['id'] in room['participants']:
            raise HTTPException(status_code=400, detail="Already joined this room")
        
        if len(room['participants']) >= room['max_participants']:
            raise HTTPException(status_code=400, detail="Room is full")
        
        # Add participant
        await db.quiz_rooms.update_one(
            {"room_code": room_code},
            {"$push": {"participants": current_user['id']}}
        )
        
        return {"message": "Joined quiz room successfully", "room_id": room['id']}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# HELP QUEUE ENDPOINTS
# ================================

@api_router.post("/help/request")
async def create_help_request(
    subject: str,
    description: str,
    priority: str = "medium",
    current_user: dict = Depends(get_current_user)
):
    """Create a help request"""
    try:
        if current_user['role'] != UserRole.STUDENT:
            raise HTTPException(status_code=403, detail="Only students can create help requests")
        
        help_request = HelpRequest(
            student_id=current_user['id'],
            subject=subject,
            description=description,
            priority=priority
        )
        
        await db.help_requests.insert_one(help_request.dict())
        
        return {"message": "Help request created successfully", "request": help_request.dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/help/queue")
async def get_help_queue(current_user: dict = Depends(get_current_user)):
    """Get help queue (for teachers)"""
    try:
        if current_user['role'] not in [UserRole.TEACHER, UserRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        requests = await db.help_requests.find(
            {"status": {"$in": ["pending", "assigned"]}}
        ).sort("created_at", 1).to_list(100)
        
        return {"requests": requests}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/help/requests/{request_id}/claim")
async def claim_help_request(request_id: str, current_user: dict = Depends(get_current_user)):
    """Claim a help request (for teachers)"""
    try:
        if current_user['role'] not in [UserRole.TEACHER, UserRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = await db.help_requests.update_one(
            {"id": request_id, "status": "pending"},
            {
                "$set": {
                    "status": "assigned",
                    "assigned_teacher": current_user['id'],
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Request not found or already claimed")
        
        return {"message": "Help request claimed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# ANALYTICS ENDPOINTS
# ================================

@api_router.get("/analytics/dashboard")
async def get_analytics_dashboard(current_user: dict = Depends(get_current_user)):
    """Get user analytics dashboard"""
    try:
        # Get user stats
        user_stats = await get_user_statistics(current_user['id'])
        
        # Get recent activity
        recent_sessions = await db.study_sessions.find(
            {"user_id": current_user['id']}
        ).sort("created_at", -1).limit(10).to_list(10)
        
        # Get performance trends (simplified)
        assessment_results = await db.assessment_results.find(
            {"user_id": current_user['id']}
        ).sort("completed_at", -1).limit(20).to_list(20)
        
        performance_trend = [result['score'] for result in assessment_results]
        
        return {
            "user_stats": user_stats,
            "recent_sessions": recent_sessions,
            "performance_trend": performance_trend,
            "total_assessments": len(assessment_results),
            "average_score": sum(performance_trend) / len(performance_trend) if performance_trend else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/predictions")
async def get_learning_predictions(current_user: dict = Depends(get_current_user)):
    """Get AI-powered learning predictions"""
    try:
        # Simple ML prediction (in production, use more sophisticated models)
        assessment_results = await db.assessment_results.find(
            {"user_id": current_user['id']}
        ).sort("completed_at", 1).to_list(100)
        
        if len(assessment_results) < 3:
            return {"prediction": "Need more data for predictions", "confidence": 0}
        
        # Prepare data for linear regression
        X = np.array([[i] for i in range(len(assessment_results))])
        y = np.array([result['score'] for result in assessment_results])
        
        # Train simple model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next assessment performance
        next_prediction = model.predict([[len(assessment_results)]])[0]
        
        # Calculate trend
        trend = "improving" if model.coef_[0] > 0 else "declining" if model.coef_[0] < 0 else "stable"
        
        return {
            "predicted_next_score": round(next_prediction, 2),
            "trend": trend,
            "confidence": 0.75,  # Simplified confidence
            "recommendation": f"Based on your {trend} trend, focus on practice questions in your weaker subjects."
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"prediction": "Unable to generate predictions", "confidence": 0}

# ================================
# ACHIEVEMENTS & GAMIFICATION
# ================================

@api_router.get("/achievements")
async def get_achievements():
    """Get all available achievements"""
    try:
        achievements = await db.achievements.find({}).to_list(100)
        return {"achievements": achievements}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/achievements/my")
async def get_user_achievements(current_user: dict = Depends(get_current_user)):
    """Get user's earned achievements"""
    try:
        user_achievement_ids = current_user.get('achievements', [])
        
        if not user_achievement_ids:
            return {"achievements": []}
        
        achievements = await db.achievements.find(
            {"id": {"$in": user_achievement_ids}}
        ).to_list(100)
        
        return {"achievements": achievements}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# UTILITY FUNCTIONS
# ================================

async def award_xp(user_id: str, xp_amount: int, activity_type: str):
    """Award XP to user and check for level up"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            return
        
        current_xp = user.get('xp_points', 0)
        current_level = user.get('level', 1)
        
        new_xp = current_xp + xp_amount
        new_level = calculate_level(new_xp)
        
        # Update user
        await db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "xp_points": new_xp,
                    "level": new_level,
                    "last_active": datetime.utcnow()
                }
            }
        )
        
        # Record study session
        session = StudySession(
            user_id=user_id,
            activity_type=activity_type,
            subject="general",
            duration=5,  # Simplified
            xp_gained=xp_amount
        )
        
        await db.study_sessions.insert_one(session.dict())
        
        # Check for level up achievement
        if new_level > current_level:
            await award_achievement(user_id, f"level_{new_level}")
        
    except Exception as e:
        logger.error(f"Error awarding XP: {e}")

def calculate_level(xp: int) -> int:
    """Calculate user level based on XP"""
    return min(int(xp / 100) + 1, 100)  # 100 XP per level, max level 100

async def check_achievements(user_id: str):
    """Check and award achievements to user"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            return
        
        user_achievements = user.get('achievements', [])
        
        # Get user statistics
        stats = await get_user_statistics(user_id)
        
        # Check all achievements
        all_achievements = await db.achievements.find({}).to_list(100)
        
        for achievement in all_achievements:
            if achievement['id'] in user_achievements:
                continue  # Already earned
            
            # Check criteria
            criteria = achievement['criteria']
            earned = True
            
            for key, required_value in criteria.items():
                user_value = stats.get(key, 0)
                if user_value < required_value:
                    earned = False
                    break
            
            if earned:
                await award_achievement(user_id, achievement['id'])
        
    except Exception as e:
        logger.error(f"Error checking achievements: {e}")

async def award_achievement(user_id: str, achievement_id: str):
    """Award achievement to user"""
    try:
        # Add achievement to user
        await db.users.update_one(
            {"id": user_id},
            {"$addToSet": {"achievements": achievement_id}}
        )
        
        # Get achievement for XP reward
        achievement = await db.achievements.find_one({"id": achievement_id})
        if achievement:
            await award_xp(user_id, achievement['xp_reward'], "achievement")
        
        logger.info(f"Achievement {achievement_id} awarded to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error awarding achievement: {e}")

async def get_user_statistics(user_id: str) -> Dict[str, Any]:
    """Get comprehensive user statistics"""
    try:
        # Assessment stats
        assessment_results = await db.assessment_results.find({"user_id": user_id}).to_list(1000)
        assessments_completed = len(assessment_results)
        perfect_scores = len([r for r in assessment_results if r['score'] == 100])
        
        # AI conversation stats
        ai_conversations = await db.ai_conversations.count_documents({"user_id": user_id})
        
        # Study session stats
        study_sessions = await db.study_sessions.find({"user_id": user_id}).to_list(1000)
        total_study_time = sum(session['duration'] for session in study_sessions)
        
        # User data
        user = await db.users.find_one({"id": user_id})
        study_streak = user.get('study_streak', 0) if user else 0
        
        return {
            "assessments_completed": assessments_completed,
            "perfect_scores": perfect_scores,
            "ai_conversations": ai_conversations,
            "total_study_time": total_study_time,
            "study_streak": study_streak
        }
        
    except Exception as e:
        logger.error(f"Error getting user statistics: {e}")
        return {}

# ================================
# FILE UPLOAD ENDPOINTS
# ================================

@api_router.post("/upload/image")
async def upload_image(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload and process image (for image recognition features)"""
    try:
        # Read file content
        content = await file.read()
        
        # Convert to base64 for storage
        base64_content = base64.b64encode(content).decode('utf-8')
        
        # Store in database (in production, use cloud storage)
        file_record = {
            "id": str(uuid.uuid4()),
            "filename": file.filename,
            "content_type": file.content_type,
            "content": base64_content,
            "uploaded_by": current_user['id'],
            "uploaded_at": datetime.utcnow()
        }
        
        await db.uploaded_files.insert_one(file_record)
        
        return {
            "message": "Image uploaded successfully",
            "file_id": file_record['id'],
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include router in app
app.include_router(api_router)

# Create Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8001)