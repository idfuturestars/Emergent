"""
Learning engine endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

from app.middleware.auth import get_current_user_required
from app.models.user import User
from app.models.question import Question, QuestionSet, DifficultyLevel, QuestionType
from app.models.session import Session, SessionType, QuestionAttempt
from app.models.achievement import Achievement, UserAchievement
from app.models.analytics import Analytics, EventType

router = APIRouter()

class QuestionResponse(BaseModel):
    id: str
    title: str
    question_text: str
    question_type: QuestionType
    answer_options: List[Dict[str, Any]]
    difficulty: DifficultyLevel
    subject: str
    topic: str
    base_xp: int
    hints: List[Dict[str, Any]]
    time_limit_seconds: Optional[int]

class AnswerSubmission(BaseModel):
    question_id: str
    user_answer: str
    time_taken_seconds: int
    hints_used: int = 0
    session_id: Optional[str] = None

class LearningSession(BaseModel):
    session_type: SessionType
    subject: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    question_count: int = 10

@router.post("/start-session")
async def start_learning_session(
    request: Request,
    session_data: LearningSession,
    user_id: str = Depends(get_current_user_required)
):
    """Start a new learning session"""
    
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create new session
    session = Session(
        user_id=user_id,
        session_type=session_data.session_type,
        subject=session_data.subject,
        topic=session_data.topic,
        total_questions=session_data.question_count
    )
    await session.insert()
    
    # Get questions for session
    questions = await _get_adaptive_questions(
        user=user,
        subject=session_data.subject,
        topic=session_data.topic,
        difficulty=session_data.difficulty,
        count=session_data.question_count
    )
    
    # Log analytics
    await Analytics(
        user_id=user_id,
        event_type=EventType.SESSION_STARTED,
        event_data={
            "session_type": session_data.session_type.value,
            "subject": session_data.subject,
            "topic": session_data.topic,
            "question_count": session_data.question_count
        },
        session_id=session.id
    ).insert()
    
    return {
        "session_id": session.id,
        "questions": [
            QuestionResponse(
                id=q.id,
                title=q.title,
                question_text=q.question_text,
                question_type=q.question_type,
                answer_options=[{
                    "id": opt.id,
                    "text": opt.text,
                    "is_correct": False  # Never send correct answer to frontend
                } for opt in q.answer_options],
                difficulty=q.difficulty,
                subject=q.subject,
                topic=q.topic,
                base_xp=q.base_xp,
                hints=[{
                    "level": hint.level,
                    "text": hint.text,
                    "xp_penalty": hint.xp_penalty
                } for hint in q.hints],
                time_limit_seconds=q.time_limit_seconds
            )
            for q in questions
        ]
    }

@router.post("/submit-answer")
async def submit_answer(
    request: Request,
    submission: AnswerSubmission,
    user_id: str = Depends(get_current_user_required)
):
    """Submit answer to a question"""
    
    # Get question
    question = await Question.get(submission.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Get user and session
    user = await User.get(user_id)
    session = None
    if submission.session_id:
        session = await Session.get(submission.session_id)
    
    # Check answer
    is_correct = _check_answer(question, submission.user_answer)
    
    # Calculate XP earned
    xp_earned = _calculate_xp(question, is_correct, submission.hints_used, submission.time_taken_seconds)
    
    # Create question attempt
    attempt = QuestionAttempt(
        question_id=submission.question_id,
        user_answer=submission.user_answer,
        is_correct=is_correct,
        time_taken_seconds=submission.time_taken_seconds,
        hints_used=submission.hints_used,
        xp_earned=xp_earned
    )
    
    # Update session if exists
    if session:
        session.questions_attempted.append(attempt)
        session.total_xp_earned += xp_earned
        if is_correct:
            session.correct_answers += 1
        session.accuracy_rate = session.correct_answers / len(session.questions_attempted)
        session.last_activity = datetime.utcnow()
        await session.save()
    
    # Update user stats and progress
    user.stats.total_questions_answered += 1
    if is_correct:
        user.stats.correct_answers += 1
    user.stats.accuracy_rate = user.stats.correct_answers / user.stats.total_questions_answered
    user.progress.total_xp += xp_earned
    
    # Check for level up
    old_level = user.progress.current_level
    new_level = _calculate_level(user.progress.total_xp)
    if new_level > old_level:
        user.progress.current_level = new_level
    
    user.progress.last_activity = datetime.utcnow()
    await user.save()
    
    # Update question analytics
    question.times_attempted += 1
    if is_correct:
        question.times_correct += 1
    await question.save()
    
    # Log analytics
    await Analytics(
        user_id=user_id,
        event_type=EventType.QUESTION_ANSWERED,
        event_data={
            "question_id": submission.question_id,
            "is_correct": is_correct,
            "xp_earned": xp_earned,
            "time_taken": submission.time_taken_seconds,
            "hints_used": submission.hints_used
        },
        session_id=submission.session_id
    ).insert()
    
    # Check for achievements
    achievements = await _check_achievements(user, is_correct, xp_earned, new_level > old_level)
    
    return {
        "is_correct": is_correct,
        "correct_answer": question.correct_answer if question.question_type != QuestionType.MULTIPLE_CHOICE else None,
        "correct_option": next((opt.text for opt in question.answer_options if opt.is_correct), None) if question.question_type == QuestionType.MULTIPLE_CHOICE else None,
        "explanation": question.explanation,
        "xp_earned": xp_earned,
        "total_xp": user.progress.total_xp,
        "current_level": user.progress.current_level,
        "level_up": new_level > old_level,
        "achievements_earned": achievements
    }

@router.get("/daily-challenge")
async def get_daily_challenge(
    request: Request,
    user_id: str = Depends(get_current_user_required)
):
    """Get today's daily challenge"""
    
    from app.models.session import DailyChallenge
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get today's challenge
    challenge = await DailyChallenge.find_one({"date": today, "is_active": True})
    
    if not challenge:
        # Create today's challenge
        challenge = await _create_daily_challenge(today)
    
    # Check if user has completed
    has_completed = user_id in challenge.completions
    has_participated = user_id in challenge.participants
    
    # Get challenge questions
    questions = await Question.find({"id": {"$in": challenge.question_ids}}).to_list()
    
    return {
        "challenge_id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "xp_reward": challenge.xp_reward,
        "badge_reward": challenge.badge_reward,
        "time_limit_minutes": challenge.time_limit_minutes,
        "has_completed": has_completed,
        "has_participated": has_participated,
        "completion_rate": challenge.completion_rate,
        "total_participants": len(challenge.participants),
        "questions": [
            QuestionResponse(
                id=q.id,
                title=q.title,
                question_text=q.question_text,
                question_type=q.question_type,
                answer_options=[{
                    "id": opt.id,
                    "text": opt.text,
                    "is_correct": False
                } for opt in q.answer_options],
                difficulty=q.difficulty,
                subject=q.subject,
                topic=q.topic,
                base_xp=q.base_xp,
                hints=[],  # No hints in daily challenges
                time_limit_seconds=None
            )
            for q in questions
        ]
    }

async def _get_adaptive_questions(user: User, subject: str, topic: str, difficulty: DifficultyLevel, count: int) -> List[Question]:
    """Get adaptive questions based on user performance"""
    
    # Build query
    query = {"is_active": True}
    if subject:
        query["subject"] = subject
    if topic:
        query["topic"] = topic
    
    # If no specific difficulty, adapt based on user performance
    if not difficulty:
        accuracy = user.stats.accuracy_rate
        if accuracy >= 0.8:
            difficulty = DifficultyLevel.ADVANCED
        elif accuracy >= 0.6:
            difficulty = DifficultyLevel.INTERMEDIATE
        else:
            difficulty = DifficultyLevel.BEGINNER
    
    query["difficulty"] = difficulty
    
    # Get questions
    questions = await Question.find(query).limit(count * 2).to_list()
    
    # Shuffle and return subset
    random.shuffle(questions)
    return questions[:count]

def _check_answer(question: Question, user_answer: str) -> bool:
    """Check if user answer is correct"""
    
    if question.question_type == QuestionType.MULTIPLE_CHOICE:
        # Find the correct option
        correct_option = next((opt for opt in question.answer_options if opt.is_correct), None)
        return correct_option and correct_option.id == user_answer
    else:
        # For other types, compare with correct_answer
        return question.correct_answer.lower().strip() == user_answer.lower().strip()

def _calculate_xp(question: Question, is_correct: bool, hints_used: int, time_taken: int) -> int:
    """Calculate XP earned for answering a question"""
    
    if not is_correct:
        return 0
    
    base_xp = question.base_xp
    
    # Reduce XP for hints used
    for i in range(hints_used):
        if i < len(question.hints):
            base_xp -= question.hints[i].xp_penalty
    
    # Bonus for speed (if there's a time limit)
    if question.time_limit_seconds and time_taken < question.time_limit_seconds * 0.5:
        base_xp = int(base_xp * 1.2)  # 20% bonus
    
    return max(1, base_xp)  # Minimum 1 XP

def _calculate_level(total_xp: int) -> int:
    """Calculate user level based on total XP"""
    
    # Level formula: level = floor(sqrt(total_xp / 100))
    import math
    return max(1, int(math.sqrt(total_xp / 100)))

async def _check_achievements(user: User, is_correct: bool, xp_earned: int, level_up: bool) -> List[str]:
    """Check for newly earned achievements"""
    
    achievements = []
    
    # Simple achievement checks (you can expand this)
    if user.stats.total_questions_answered == 1:
        achievements.append("first_question")
    
    if user.stats.total_questions_answered == 100:
        achievements.append("hundred_questions")
    
    if level_up and user.progress.current_level == 10:
        achievements.append("level_10")
    
    # Save achievements
    for achievement_name in achievements:
        user_achievement = UserAchievement(
            user_id=user.id,
            achievement_id=achievement_name,  # In real app, this would be proper achievement ID
            xp_earned=25  # Default achievement XP
        )
        await user_achievement.insert()
    
    return achievements

async def _create_daily_challenge(date: datetime):
    """Create a new daily challenge"""
    
    from app.models.session import DailyChallenge
    
    # Get random questions for challenge
    questions = await Question.find({"is_active": True}).limit(20).to_list()
    random.shuffle(questions)
    selected_questions = questions[:5]  # 5 questions per challenge
    
    challenge = DailyChallenge(
        date=date,
        title=f"Daily Challenge - {date.strftime('%B %d, %Y')}",
        description="Complete today's challenge to earn XP and badges!",
        question_ids=[q.id for q in selected_questions],
        xp_reward=50,
        subject="mixed"
    )
    
    await challenge.insert()
    return challenge