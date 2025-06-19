"""
Rate limiting middleware
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict, deque
from typing import Dict, Deque
import asyncio

from app.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window"""
    
    def __init__(self, app, per_minute: int = None, per_hour: int = None):
        super().__init__(app)
        self.per_minute = per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.per_hour = per_hour or settings.RATE_LIMIT_PER_HOUR
        
        # Store request timestamps per IP
        self.minute_requests: Dict[str, Deque[float]] = defaultdict(deque)
        self.hour_requests: Dict[str, Deque[float]] = defaultdict(deque)
        
        # Cleanup task
        asyncio.create_task(self._cleanup_old_entries())
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Check rate limits
        if self._is_rate_limited(client_ip, current_time):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Record request
        self.minute_requests[client_ip].append(current_time)
        self.hour_requests[client_ip].append(current_time)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers first (for reverse proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client is rate limited"""
        # Clean old entries
        self._clean_old_entries(self.minute_requests[client_ip], current_time, 60)
        self._clean_old_entries(self.hour_requests[client_ip], current_time, 3600)
        
        # Check limits
        minute_count = len(self.minute_requests[client_ip])
        hour_count = len(self.hour_requests[client_ip])
        
        return minute_count >= self.per_minute or hour_count >= self.per_hour
    
    def _clean_old_entries(self, requests: Deque[float], current_time: float, window_seconds: int):
        """Remove old entries outside the time window"""
        cutoff_time = current_time - window_seconds
        while requests and requests[0] < cutoff_time:
            requests.popleft()
    
    async def _cleanup_old_entries(self):
        """Periodic cleanup of old entries"""
        while True:
            await asyncio.sleep(300)  # Cleanup every 5 minutes
            current_time = time.time()
            
            # Clean minute requests (keep last 2 minutes)
            for ip in list(self.minute_requests.keys()):
                self._clean_old_entries(self.minute_requests[ip], current_time, 120)
                if not self.minute_requests[ip]:
                    del self.minute_requests[ip]
            
            # Clean hour requests (keep last 2 hours)
            for ip in list(self.hour_requests.keys()):
                self._clean_old_entries(self.hour_requests[ip], current_time, 7200)
                if not self.hour_requests[ip]:
                    del self.hour_requests[ip]