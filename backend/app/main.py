"""
StarGuide AI Mentor - Main Application
Production-ready FastAPI application with enterprise features
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1.router import api_router
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-powered educational mentoring platform",
        version=settings.APP_VERSION,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom Middleware
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Include API Routes
    app.include_router(api_router, prefix="/api/v1")

    return app

# Create app instance
app = create_application()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }