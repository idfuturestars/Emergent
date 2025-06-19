"""
User management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.middleware.auth import get_current_user_required
from app.models.user import User, UserUpdate, UserResponse

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    request: Request,
    user_id: str = Depends(get_current_user_required)
):
    """Get current user's profile"""
    
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        status=user.status,
        avatar_url=user.avatar_url,
        bio=user.bio,
        grade_level=user.grade_level,
        school=user.school,
        progress=user.progress,
        stats=user.stats,
        created_at=user.created_at,
        last_login=user.last_login
    )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    request: Request,
    update_data: UserUpdate,
    user_id: str = Depends(get_current_user_required)
):
    """Update current user's profile"""
    
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    await user.save()
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        status=user.status,
        avatar_url=user.avatar_url,
        bio=user.bio,
        grade_level=user.grade_level,
        school=user.school,
        progress=user.progress,
        stats=user.stats,
        created_at=user.created_at,
        last_login=user.last_login
    )

@router.get("/leaderboard")
async def get_leaderboard(
    request: Request,
    subject: Optional[str] = None,
    time_period: str = "weekly",
    limit: int = 50
):
    """Get user leaderboard"""
    
    # Build query
    query = {"status": "active"}
    if subject:
        query["stats.subjects_mastered"] = subject
    
    # Get users sorted by XP
    users = await User.find(query).sort([("progress.total_xp", -1)]).limit(limit).to_list()
    
    leaderboard = []
    for i, user in enumerate(users):
        leaderboard.append({
            "rank": i + 1,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "total_xp": user.progress.total_xp,
            "current_level": user.progress.current_level,
            "streak_days": user.progress.streak_days,
            "achievements_count": len(user.progress.achievements_earned)
        })
    
    return {
        "leaderboard": leaderboard,
        "subject": subject,
        "time_period": time_period,
        "total_users": len(leaderboard)
    }