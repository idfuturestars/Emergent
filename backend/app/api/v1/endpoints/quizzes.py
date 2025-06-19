"""
Quiz and Assessment endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

from app.middleware.auth import get_current_user_required
from app.models.user import User
from app.models.question import Question, QuestionSet, QuestionType, DifficultyLevel
from app.models.session import Session, SessionType, SessionStatus
from app.models.analytics import Analytics, EventType

router = APIRouter()

class QuizRoom(BaseModel):
    id: str
    title: str
    description: Optional[str]
    subject: str
    max_participants: int
    current_participants: int
    room_code: str
    created_by: str
    status: str
    created_at: datetime

class CreateQuizRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    subject: str
    difficulty: DifficultyLevel
    question_count: int = Field(default=10, ge=5, le=50)
    time_limit_minutes: int = Field(default=30, ge=5, le=120)
    max_participants: int = Field(default=50, ge=2, le=100)

class JoinQuizRequest(BaseModel):
    room_code: str

class QuizQuestion(BaseModel):
    id: str
    question_text: str
    question_type: QuestionType
    options: List[Dict[str, str]]
    time_limit_seconds: int
    points: int

class QuizSession:
    """In-memory quiz session management"""
    
    def __init__(self):
        self.active_rooms: Dict[str, Dict] = {}
        self.room_participants: Dict[str, List[str]] = {}
    
    def create_room(self, room_data: Dict) -> str:
        """Create a new quiz room"""
        room_id = room_data["id"]
        self.active_rooms[room_id] = room_data
        self.room_participants[room_id] = []
        return room_id
    
    def join_room(self, room_id: str, user_id: str) -> bool:
        """Add user to quiz room"""
        if room_id in self.active_rooms:
            if user_id not in self.room_participants[room_id]:
                self.room_participants[room_id].append(user_id)
                self.active_rooms[room_id]["current_participants"] = len(self.room_participants[room_id])
                return True
        return False
    
    def leave_room(self, room_id: str, user_id: str):
        """Remove user from quiz room"""
        if room_id in self.room_participants and user_id in self.room_participants[room_id]:
            self.room_participants[room_id].remove(user_id)
            self.active_rooms[room_id]["current_participants"] = len(self.room_participants[room_id])

# Global quiz session manager
quiz_manager = QuizSession()

@router.post("/create-room")
async def create_quiz_room(
    request: Request,
    quiz_data: CreateQuizRequest,
    user_id: str = Depends(get_current_user_required)
):
    """Create a new quiz room"""
    
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate room code
    room_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    
    # Get questions for quiz
    questions = await Question.find({
        "subject": quiz_data.subject,
        "difficulty": quiz_data.difficulty,
        "is_active": True
    }).limit(quiz_data.question_count * 2).to_list()
    
    if len(questions) < quiz_data.question_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough questions available for {quiz_data.subject} at {quiz_data.difficulty} level"
        )
    
    # Select random questions
    selected_questions = random.sample(questions, quiz_data.question_count)
    
    # Create room data
    room_data = {
        "id": f"quiz_{random.randint(10000, 99999)}",
        "title": quiz_data.title,
        "description": quiz_data.description,
        "subject": quiz_data.subject,
        "difficulty": quiz_data.difficulty,
        "room_code": room_code,
        "created_by": user_id,
        "creator_name": user.username,
        "max_participants": quiz_data.max_participants,
        "current_participants": 0,
        "status": "waiting",
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type.value,
                "options": [{"id": opt.id, "text": opt.text} for opt in q.answer_options],
                "correct_answer": q.correct_answer,
                "time_limit_seconds": 30,
                "points": q.base_xp
            }
            for q in selected_questions
        ],
        "time_limit_minutes": quiz_data.time_limit_minutes,
        "created_at": datetime.utcnow(),
        "participants": {},
        "current_question": 0,
        "started_at": None
    }
    
    # Add to quiz manager
    room_id = quiz_manager.create_room(room_data)
    
    return {
        "room_id": room_id,
        "room_code": room_code,
        "message": "Quiz room created successfully"
    }

@router.post("/join-room")
async def join_quiz_room(
    request: Request,
    join_data: JoinQuizRequest,
    user_id: str = Depends(get_current_user_required)
):
    """Join a quiz room using room code"""
    
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Find room by code
    room_id = None
    room_data = None
    for rid, data in quiz_manager.active_rooms.items():
        if data["room_code"] == join_data.room_code:
            room_id = rid
            room_data = data
            break
    
    if not room_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz room not found"
        )
    
    if room_data["status"] != "waiting":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz has already started or ended"
        )
    
    if room_data["current_participants"] >= room_data["max_participants"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz room is full"
        )
    
    # Join room
    success = quiz_manager.join_room(room_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not join quiz room"
        )
    
    # Add participant info
    room_data["participants"][user_id] = {
        "username": user.username,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "score": 0,
        "answers": [],
        "joined_at": datetime.utcnow()
    }
    
    return {
        "room_id": room_id,
        "room_title": room_data["title"],
        "current_participants": room_data["current_participants"],
        "message": "Successfully joined quiz room"
    }

@router.get("/room/{room_id}")
async def get_quiz_room(
    room_id: str,
    request: Request,
    user_id: str = Depends(get_current_user_required)
):
    """Get quiz room details"""
    
    if room_id not in quiz_manager.active_rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz room not found"
        )
    
    room_data = quiz_manager.active_rooms[room_id]
    
    # Check if user is participant
    if user_id not in quiz_manager.room_participants[room_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this quiz"
        )
    
    return {
        "room_id": room_id,
        "title": room_data["title"],
        "description": room_data["description"],
        "subject": room_data["subject"],
        "status": room_data["status"],
        "current_participants": room_data["current_participants"],
        "max_participants": room_data["max_participants"],
        "created_by": room_data["created_by"],
        "creator_name": room_data["creator_name"],
        "participants": list(room_data["participants"].values()),
        "current_question": room_data["current_question"],
        "total_questions": len(room_data["questions"]),
        "time_limit_minutes": room_data["time_limit_minutes"],
        "started_at": room_data["started_at"]
    }

@router.post("/room/{room_id}/start")
async def start_quiz(
    room_id: str,
    request: Request,
    user_id: str = Depends(get_current_user_required)
):
    """Start the quiz (creator only)"""
    
    if room_id not in quiz_manager.active_rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz room not found"
        )
    
    room_data = quiz_manager.active_rooms[room_id]
    
    # Check if user is creator
    if room_data["created_by"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can start the quiz"
        )
    
    if room_data["status"] != "waiting":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz has already started"
        )
    
    # Start quiz
    room_data["status"] = "active"
    room_data["started_at"] = datetime.utcnow()
    room_data["current_question"] = 0
    
    return {"message": "Quiz started successfully"}

@router.get("/room/{room_id}/question")
async def get_current_question(
    room_id: str,
    request: Request,
    user_id: str = Depends(get_current_user_required)
):
    """Get current quiz question"""
    
    if room_id not in quiz_manager.active_rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz room not found"
        )
    
    room_data = quiz_manager.active_rooms[room_id]
    
    if user_id not in quiz_manager.room_participants[room_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this quiz"
        )
    
    if room_data["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz is not active"
        )
    
    current_q_index = room_data["current_question"]
    if current_q_index >= len(room_data["questions"]):
        return {"message": "Quiz completed", "status": "completed"}
    
    question = room_data["questions"][current_q_index]
    
    return {
        "question_number": current_q_index + 1,
        "total_questions": len(room_data["questions"]),
        "question": {
            "id": question["id"],
            "text": question["question_text"],
            "type": question["question_type"],
            "options": question["options"],  # Don't include correct answer
            "time_limit_seconds": question["time_limit_seconds"],
            "points": question["points"]
        }
    }

@router.post("/room/{room_id}/answer")
async def submit_quiz_answer(
    room_id: str,
    request: Request,
    answer: str,
    user_id: str = Depends(get_current_user_required)
):
    """Submit answer to current question"""
    
    if room_id not in quiz_manager.active_rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz room not found"
        )
    
    room_data = quiz_manager.active_rooms[room_id]
    
    if user_id not in quiz_manager.room_participants[room_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this quiz"
        )
    
    current_q_index = room_data["current_question"]
    question = room_data["questions"][current_q_index]
    
    # Check answer
    is_correct = False
    if question["question_type"] == "multiple_choice":
        correct_option = next((opt for opt in question["options"] if opt["id"] == question["correct_answer"]), None)
        is_correct = correct_option and correct_option["id"] == answer
    else:
        is_correct = question["correct_answer"].lower() == answer.lower()
    
    # Update participant score
    if is_correct:
        room_data["participants"][user_id]["score"] += question["points"]
    
    room_data["participants"][user_id]["answers"].append({
        "question_id": question["id"],
        "answer": answer,
        "is_correct": is_correct,
        "points_earned": question["points"] if is_correct else 0
    })
    
    return {
        "is_correct": is_correct,
        "points_earned": question["points"] if is_correct else 0,
        "total_score": room_data["participants"][user_id]["score"]
    }

@router.get("/active-rooms")
async def get_active_quiz_rooms(
    request: Request,
    subject: Optional[str] = None
):
    """Get list of active quiz rooms"""
    
    active_rooms = []
    for room_id, room_data in quiz_manager.active_rooms.items():
        if room_data["status"] == "waiting":
            if not subject or room_data["subject"] == subject:
                active_rooms.append({
                    "room_id": room_id,
                    "title": room_data["title"],
                    "subject": room_data["subject"],
                    "difficulty": room_data["difficulty"],
                    "room_code": room_data["room_code"],
                    "current_participants": room_data["current_participants"],
                    "max_participants": room_data["max_participants"],
                    "creator_name": room_data["creator_name"],
                    "created_at": room_data["created_at"]
                })
    
    return {"active_rooms": active_rooms}