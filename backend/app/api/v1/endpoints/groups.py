"""
Study Groups endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.middleware.auth import get_current_user_required
from app.models.user import User
from app.models.study_group import StudyGroup, StudyGroupType, GroupMember, StudySession
from app.models.analytics import Analytics, EventType

router = APIRouter()

class CreateGroupRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    subject: str
    group_type: StudyGroupType = StudyGroupType.PUBLIC
    grade_level: Optional[str] = None
    max_members: int = Field(default=20, ge=5, le=100)

class GroupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    subject: str
    group_type: StudyGroupType
    join_code: str
    member_count: int
    max_members: int
    created_by: str
    created_at: datetime
    is_member: bool = False

class JoinGroupRequest(BaseModel):
    join_code: str

@router.post("/create", response_model=GroupResponse)
async def create_study_group(
    request: Request,
    group_data: CreateGroupRequest,
    user_id: str = Depends(get_current_user_required)
):
    """Create a new study group"""
    
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create study group
    group = StudyGroup(
        name=group_data.name,
        description=group_data.description,
        subject=group_data.subject,
        group_type=group_data.group_type,
        grade_level=group_data.grade_level,
        max_members=group_data.max_members,
        created_by=user_id,
        organization_id=user.organization_id
    )
    
    # Add creator as admin member
    creator_member = GroupMember(
        user_id=user_id,
        role="admin"
    )
    group.members.append(creator_member)
    group.member_count = 1
    
    await group.insert()
    
    # Add group to user's groups
    user.study_groups.append(group.id)
    await user.save()
    
    # Log analytics
    await Analytics(
        user_id=user_id,
        event_type=EventType.GROUP_JOINED,
        event_data={
            "group_id": group.id,
            "group_name": group.name,
            "action": "created"
        }
    ).insert()
    
    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        subject=group.subject,
        group_type=group.group_type,
        join_code=group.join_code,
        member_count=group.member_count,
        max_members=group.max_members,
        created_by=group.created_by,
        created_at=group.created_at,
        is_member=True
    )

@router.post("/join")
async def join_study_group(
    request: Request,
    join_data: JoinGroupRequest,
    user_id: str = Depends(get_current_user_required)
):
    """Join a study group using join code"""
    
    # Find group by join code
    group = await StudyGroup.find_one({"join_code": join_data.join_code, "is_active": True})
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study group not found"
        )
    
    # Check if already a member
    existing_member = next((m for m in group.members if m.user_id == user_id), None)
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a member of this group"
        )
    
    # Check if group is full
    if group.member_count >= group.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Study group is full"
        )
    
    # Add user as member
    new_member = GroupMember(user_id=user_id)
    group.members.append(new_member)
    group.member_count += 1
    group.last_activity = datetime.utcnow()
    await group.save()
    
    # Add group to user's groups
    user = await User.get(user_id)
    if group.id not in user.study_groups:
        user.study_groups.append(group.id)
        await user.save()
    
    # Log analytics
    await Analytics(
        user_id=user_id,
        event_type=EventType.GROUP_JOINED,
        event_data={
            "group_id": group.id,
            "group_name": group.name,
            "action": "joined"
        }
    ).insert()
    
    return {"message": "Successfully joined the study group", "group_name": group.name}

@router.get("/my-groups", response_model=List[GroupResponse])
async def get_my_groups(
    request: Request,
    user_id: str = Depends(get_current_user_required)
):
    """Get user's study groups"""
    
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user's groups
    groups = await StudyGroup.find({"id": {"$in": user.study_groups}}).to_list()
    
    return [
        GroupResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            subject=group.subject,
            group_type=group.group_type,
            join_code=group.join_code,
            member_count=group.member_count,
            max_members=group.max_members,
            created_by=group.created_by,
            created_at=group.created_at,
            is_member=True
        )
        for group in groups
    ]

@router.get("/discover", response_model=List[GroupResponse])
async def discover_groups(
    request: Request,
    subject: Optional[str] = None,
    grade_level: Optional[str] = None,
    limit: int = 20,
    user_id: str = Depends(get_current_user_required)
):
    """Discover public study groups"""
    
    user = await User.get(user_id)
    
    # Build query
    query = {"group_type": StudyGroupType.PUBLIC, "is_active": True}
    if subject:
        query["subject"] = subject
    if grade_level:
        query["grade_level"] = grade_level
    
    groups = await StudyGroup.find(query).limit(limit).to_list()
    
    return [
        GroupResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            subject=group.subject,
            group_type=group.group_type,
            join_code=group.join_code,
            member_count=group.member_count,
            max_members=group.max_members,
            created_by=group.created_by,
            created_at=group.created_at,
            is_member=group.id in user.study_groups
        )
        for group in groups
    ]

@router.get("/{group_id}")
async def get_group_details(
    group_id: str,
    request: Request,
    user_id: str = Depends(get_current_user_required)
):
    """Get detailed group information"""
    
    group = await StudyGroup.get(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study group not found"
        )
    
    # Check if user is a member
    is_member = any(m.user_id == user_id for m in group.members)
    if not is_member and group.group_type == StudyGroupType.PRIVATE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to private group"
        )
    
    # Get member details
    member_users = await User.find({"id": {"$in": [m.user_id for m in group.members]}}).to_list()
    member_details = []
    
    for member in group.members:
        user_info = next((u for u in member_users if u.id == member.user_id), None)
        if user_info:
            member_details.append({
                "user_id": member.user_id,
                "username": user_info.username,
                "full_name": user_info.full_name,
                "avatar_url": user_info.avatar_url,
                "role": member.role,
                "joined_at": member.joined_at,
                "is_active": member.is_active
            })
    
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "subject": group.subject,
        "group_type": group.group_type,
        "join_code": group.join_code if is_member else None,
        "member_count": group.member_count,
        "max_members": group.max_members,
        "created_by": group.created_by,
        "created_at": group.created_at,
        "last_activity": group.last_activity,
        "is_member": is_member,
        "members": member_details,
        "upcoming_sessions": group.upcoming_sessions,
        "settings": group.settings if is_member else {}
    }

@router.post("/{group_id}/leave")
async def leave_group(
    group_id: str,
    request: Request,
    user_id: str = Depends(get_current_user_required)
):
    """Leave a study group"""
    
    group = await StudyGroup.get(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study group not found"
        )
    
    # Check if user is a member
    member = next((m for m in group.members if m.user_id == user_id), None)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a member of this group"
        )
    
    # Remove member
    group.members = [m for m in group.members if m.user_id != user_id]
    group.member_count = len(group.members)
    
    # If no members left, deactivate group
    if group.member_count == 0:
        group.is_active = False
    
    await group.save()
    
    # Remove group from user's groups
    user = await User.get(user_id)
    if group_id in user.study_groups:
        user.study_groups.remove(group_id)
        await user.save()
    
    return {"message": "Successfully left the study group"}

@router.get("/{group_id}/sessions")
async def get_group_sessions(
    group_id: str,
    request: Request,
    user_id: str = Depends(get_current_user_required)
):
    """Get group study sessions"""
    
    group = await StudyGroup.get(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study group not found"
        )
    
    # Check if user is a member
    is_member = any(m.user_id == user_id for m in group.members)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be a group member to view sessions"
        )
    
    return {
        "upcoming_sessions": group.upcoming_sessions,
        "total_sessions": group.total_sessions
    }