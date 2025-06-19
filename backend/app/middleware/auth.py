"""
Authentication middleware
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import jwt

from app.core.config import settings
from app.core.auth import verify_token
from app.models.user import User

# Security scheme
security = HTTPBearer(auto_error=False)

class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for JWT tokens"""
    
    # Public endpoints that don't require authentication
    PUBLIC_PATHS = {
        "/health",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/docs",
        "/api/redoc"
    }
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)
        
        # Check for authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # Verify token
                payload = verify_token(token)
                user_id = payload.get("sub")
                
                # Add user info to request state
                request.state.user_id = user_id
                request.state.user_role = payload.get("role")
                request.state.organization_id = payload.get("organization_id")
                
            except HTTPException:
                # Token invalid, but continue to let route handlers decide
                request.state.user_id = None
        else:
            request.state.user_id = None
        
        return await call_next(request)

async def get_current_user(request: Request) -> Optional[str]:
    """Get current user ID from request state"""
    return getattr(request.state, "user_id", None)

async def get_current_user_required(request: Request) -> str:
    """Get current user ID, raise exception if not authenticated"""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user_id

async def require_role(request: Request, required_role: str):
    """Check if user has required role"""
    user_role = getattr(request.state, "user_role", None)
    if not user_role or user_role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{required_role}' required"
        )