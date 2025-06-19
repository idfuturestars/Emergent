"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, ai, learning, groups, quizzes, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Tutor"])
api_router.include_router(learning.router, prefix="/learning", tags=["Learning"])
api_router.include_router(groups.router, prefix="/groups", tags=["Study Groups"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["Quizzes & Assessments"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

@api_router.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "StarGuide AI Mentor API v1.0",
        "status": "operational",
        "features": [
            "Multi-AI tutoring (OpenAI, Claude, Gemini)",
            "Adaptive assessments",
            "Study groups",
            "Real-time collaboration",
            "Progress analytics",
            "Achievement system"
        ]
    }