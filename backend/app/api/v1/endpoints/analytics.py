"""
Analytics and reporting endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.middleware.auth import get_current_user_required, require_role
from app.models.user import User, UserRole
from app.models.analytics import Analytics, UserLearningMetrics, PlatformMetrics
from app.models.session import Session
from app.models.achievement import UserAchievement

router = APIRouter()

@router.get("/dashboard")
async def get_user_dashboard(
    request: Request,
    user_id: str = Depends(get_current_user_required)
):
    """Get user's learning dashboard"""
    
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get recent sessions
    recent_sessions = await Session.find(
        {"user_id": user_id}
    ).sort([("started_at", -1)]).limit(10).to_list()
    
    # Get recent achievements
    recent_achievements = await UserAchievement.find(
        {"user_id": user_id}
    ).sort([("earned_at", -1)]).limit(5).to_list()
    
    # Calculate weekly stats
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_metrics = await UserLearningMetrics.find({
        "user_id": user_id,
        "date": {"$gte": week_ago}
    }).to_list()
    
    # Aggregate weekly data
    weekly_stats = {
        "total_study_time": sum(m.total_study_time_minutes for m in weekly_metrics),
        "questions_answered": sum(m.questions_answered for m in weekly_metrics),
        "accuracy_rate": sum(m.accuracy_rate for m in weekly_metrics) / len(weekly_metrics) if weekly_metrics else 0,
        "xp_earned": sum(m.xp_earned for m in weekly_metrics),
        "ai_interactions": sum(m.ai_interactions for m in weekly_metrics)
    }
    
    # Subject performance
    subject_performance = {}
    for session in recent_sessions:
        if session.subject:
            if session.subject not in subject_performance:
                subject_performance[session.subject] = {
                    "sessions": 0,
                    "accuracy": 0,
                    "total_questions": 0,
                    "correct_answers": 0
                }
            
            subject_performance[session.subject]["sessions"] += 1
            subject_performance[session.subject]["total_questions"] += len(session.questions_attempted)
            subject_performance[session.subject]["correct_answers"] += session.correct_answers
    
    # Calculate accuracy per subject
    for subject in subject_performance:
        total_q = subject_performance[subject]["total_questions"]
        if total_q > 0:
            subject_performance[subject]["accuracy"] = subject_performance[subject]["correct_answers"] / total_q
    
    return {
        "user_progress": {
            "total_xp": user.progress.total_xp,
            "current_level": user.progress.current_level,
            "streak_days": user.progress.streak_days,
            "lessons_completed": user.progress.lessons_completed,
            "achievements_count": len(user.progress.achievements_earned)
        },
        "user_stats": {
            "total_study_time": user.stats.total_study_time,
            "total_questions_answered": user.stats.total_questions_answered,
            "accuracy_rate": user.stats.accuracy_rate,
            "subjects_mastered": user.stats.subjects_mastered
        },
        "weekly_stats": weekly_stats,
        "recent_sessions": [
            {
                "id": s.id,
                "type": s.session_type.value,
                "subject": s.subject,
                "accuracy": s.accuracy_rate,
                "xp_earned": s.total_xp_earned,
                "duration": s.total_time_minutes,
                "started_at": s.started_at
            }
            for s in recent_sessions
        ],
        "recent_achievements": [
            {
                "id": a.id,
                "achievement_id": a.achievement_id,
                "xp_earned": a.xp_earned,
                "earned_at": a.earned_at
            }
            for a in recent_achievements
        ],
        "subject_performance": subject_performance
    }

@router.get("/progress-chart")
async def get_progress_chart(
    request: Request,
    days: int = 30,
    user_id: str = Depends(get_current_user_required)
):
    """Get user's progress chart data"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    metrics = await UserLearningMetrics.find({
        "user_id": user_id,
        "date": {"$gte": start_date}
    }).sort([("date", 1)]).to_list()
    
    chart_data = []
    for metric in metrics:
        chart_data.append({
            "date": metric.date.strftime("%Y-%m-%d"),
            "xp_earned": metric.xp_earned,
            "questions_answered": metric.questions_answered,
            "accuracy_rate": metric.accuracy_rate,
            "study_time_minutes": metric.total_study_time_minutes
        })
    
    return {"chart_data": chart_data}

@router.get("/ai-usage")
async def get_ai_usage_stats(
    request: Request,
    days: int = 30,
    user_id: str = Depends(get_current_user_required)
):
    """Get user's AI usage statistics"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get AI interactions from analytics
    ai_events = await Analytics.find({
        "user_id": user_id,
        "event_type": "ai_interaction",
        "timestamp": {"$gte": start_date}
    }).to_list()
    
    # Aggregate by model
    model_usage = {}
    total_tokens = 0
    total_interactions = len(ai_events)
    
    for event in ai_events:
        model = event.event_data.get("model", "unknown")
        tokens = event.event_data.get("tokens_used", 0)
        
        if model not in model_usage:
            model_usage[model] = {"interactions": 0, "tokens": 0}
        
        model_usage[model]["interactions"] += 1
        model_usage[model]["tokens"] += tokens
        total_tokens += tokens
    
    return {
        "total_interactions": total_interactions,
        "total_tokens_used": total_tokens,
        "model_breakdown": model_usage,
        "period_days": days
    }

@router.get("/admin/platform-metrics")
async def get_platform_metrics(
    request: Request,
    days: int = 30,
    user_id: str = Depends(get_current_user_required)
):
    """Get platform-wide metrics (admin only)"""
    
    # Check admin role
    user = await User.get(user_id)
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get platform metrics
    platform_metrics = await PlatformMetrics.find({
        "date": {"$gte": start_date}
    }).sort([("date", -1)]).to_list()
    
    # Get current totals
    total_users = await User.count_documents({})
    active_users_today = await User.count_documents({
        "progress.last_activity": {"$gte": datetime.utcnow() - timedelta(days=1)}
    })
    
    # Recent sessions
    recent_sessions = await Session.count_documents({
        "started_at": {"$gte": start_date}
    })
    
    return {
        "current_stats": {
            "total_users": total_users,
            "active_users_today": active_users_today,
            "sessions_this_period": recent_sessions
        },
        "daily_metrics": [
            {
                "date": m.date.strftime("%Y-%m-%d"),
                "total_users": m.total_users,
                "active_users": m.active_users,
                "new_users": m.new_users,
                "total_sessions": m.total_sessions,
                "ai_interactions": m.ai_interactions,
                "avg_accuracy": m.avg_accuracy_rate
            }
            for m in platform_metrics
        ]
    }

@router.get("/teacher/class-overview")
async def get_class_overview(
    request: Request,
    user_id: str = Depends(get_current_user_required)
):
    """Get class overview for teachers"""
    
    user = await User.get(user_id)
    if user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required"
        )
    
    # Get students in teacher's organization
    students = await User.find({
        "organization_id": user.organization_id,
        "role": UserRole.STUDENT
    }).to_list()
    
    # Get class performance data
    class_stats = {
        "total_students": len(students),
        "active_students": 0,
        "avg_level": 0,
        "avg_accuracy": 0,
        "total_sessions": 0
    }
    
    student_performance = []
    total_levels = 0
    total_accuracy = 0
    
    for student in students:
        # Check if active (activity in last 7 days)
        is_active = student.progress.last_activity and student.progress.last_activity >= datetime.utcnow() - timedelta(days=7)
        if is_active:
            class_stats["active_students"] += 1
        
        total_levels += student.progress.current_level
        total_accuracy += student.stats.accuracy_rate
        
        student_performance.append({
            "id": student.id,
            "name": student.full_name,
            "username": student.username,
            "level": student.progress.current_level,
            "xp": student.progress.total_xp,
            "accuracy": student.stats.accuracy_rate,
            "questions_answered": student.stats.total_questions_answered,
            "last_activity": student.progress.last_activity,
            "is_active": is_active
        })
    
    if students:
        class_stats["avg_level"] = total_levels / len(students)
        class_stats["avg_accuracy"] = total_accuracy / len(students)
    
    return {
        "class_stats": class_stats,
        "student_performance": sorted(student_performance, key=lambda x: x["xp"], reverse=True),
        "organization_id": user.organization_id
    }