"""
Distributed rate limiting utilities
"""
import time
import logging
from typing import Dict, Tuple, Optional
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class DistributedRateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}
        self.limits = {
            "free": {"requests": 10, "window": 60},
            "basic": {"requests": 50, "window": 60},
            "premium": {"requests": 200, "window": 60}
        }
    
    async def check_rate_limit(
        self, 
        user_id: str, 
        tier: str = "free",
        endpoint: str = ""
    ) -> Tuple[bool, int, Dict]:
        """Check if request is allowed"""
        limits = self.limits.get(tier, self.limits["free"])
        key = f"{user_id}:{endpoint}"
        window = limits["window"]
        max_requests = limits["requests"]
        
        now = time.time()
        window_start = now - window
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        
        if len(self.requests[key]) >= max_requests:
            oldest = self.requests[key][0]
            retry_after = int(oldest + window - now)
            return False, retry_after, {
                "limit": max_requests,
                "remaining": 0,
                "reset": int(now + retry_after)
            }
        
        self.requests[key].append(now)
        remaining = max_requests - len(self.requests[key])
        
        return True, 0, {
            "limit": max_requests,
            "remaining": remaining,
            "reset": int(now + window)
        }
    
    async def get_user_tier(self, user_id: str) -> str:
        """Get user tier"""
        return "free"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, limiter: DistributedRateLimiter):
        super().__init__(app)
        self.limiter = limiter
    
    async def dispatch(self, request: Request, call_next):
        user_id = getattr(request.state, "user_id", "anonymous")
        user_tier = getattr(request.state, "user_tier", "free")
        
        allowed, retry_after, info = await self.limiter.check_rate_limit(
            user_id, user_tier, request.url.path
        )
        
        response = await call_next(request)
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds",
                headers={"Retry-After": str(retry_after)}
            )
        
        response.headers["X-RateLimit-Limit"] = str(info.get("limit", ""))
        response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", ""))
        response.headers["X-RateLimit-Reset"] = str(info.get("reset", ""))
        
        return response
