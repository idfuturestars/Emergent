"""
Authentication endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from typing import Optional

from app.core.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token
)
from app.core.config import settings
from app.models.user import User, UserCreate, UserResponse
from app.middleware.auth import get_current_user_required

router = APIRouter()

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = await User.find_one(
        {"$or": [{"email": user_data.email}, {"username": user_data.username}]}
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        grade_level=user_data.grade_level,
        school=user_data.school
    )
    
    await user.insert()
    
    # Return user response (excluding sensitive data)
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

@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user with email/username and password"""
    
    # Find user by email or username
    user = await User.find_one(
        {"$or": [{"email": form_data.username}, {"username": form_data.username}]}
    )
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is not active"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await user.save()
    
    # Create tokens
    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "organization_id": user.organization_id
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": user.id})
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
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
    )

@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_data: RefreshRequest):
    """Refresh access token using refresh token"""
    
    try:
        # Verify refresh token
        payload = verify_token(refresh_data.refresh_token, "refresh")
        user_id = payload.get("sub")
        
        # Get user
        user = await User.get(user_id)
        if not user or user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "organization_id": user.organization_id
        }
        
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(request: Request, user_id: str = Depends(get_current_user_required)):
    """Get current user information"""
    
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

@router.post("/logout")
async def logout(request: Request, user_id: str = Depends(get_current_user_required)):
    """Logout user (client should discard tokens)"""
    
    # In a production system, you might want to maintain a blacklist of tokens
    # For now, we'll just return success and rely on client to discard tokens
    
    return {"message": "Successfully logged out"}