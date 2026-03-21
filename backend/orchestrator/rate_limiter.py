# backend/orchestrator/utils/rate_limiter.py
"""
Distributed rate limiting using Redis
"""
import time
import asyncio
from typing import Dict, Tuple, Optional
from redis import Redis
from fastapi import HTTPException, Request
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class DistributedRateLimiter:
    """Redis-based distributed rate limiter"""
    
    def __init__(self, redis_client: Redis = None):
        self.redis = redis_client or Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        
        # Rate limits per user tier (requests per minute)
        self.limits = {
            "free": {"requests": 10, "window": 60},
            "basic": {"requests": 50, "window": 60},
            "premium": {"requests": 200, "window": 60},
            "enterprise": {"requests": 1000, "window": 60}
        }
    
    async def check_rate_limit(
        self, 
        user_id: str, 
        tier: str = "free",
        endpoint: str = ""
    ) -> Tuple[bool, int, Dict]:
        """
        Check if request is allowed
        
        Returns:
            (allowed, retry_after, rate_limit_info)
        """
        limits = self.limits.get(tier, self.limits["free"])
        key = f"rate_limit:{user_id}:{endpoint}"
        window = limits["window"]
        max_requests = limits["requests"]
        
        try:
            # Get current count
            current = self.redis.get(key)
            current_count = int(current) if current else 0
            
            if current_count >= max_requests:
                ttl = self.redis.ttl(key)
                retry_after = ttl if ttl > 0 else window
                return False, retry_after, {
                    "limit": max_requests,
                    "remaining": 0,
                    "reset": int(time.time() + retry_after)
                }
            
            # Increment counter
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            results = pipe.execute()
            
            new_count = results[0]
            
            return True, 0, {
                "limit": max_requests,
                "remaining": max_requests - new_count,
                "reset": int(time.time() + self.redis.ttl(key))
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Fail open - allow request if Redis is down
            return True, 0, {"error": "rate_limiter_unavailable"}
    
    async def get_user_tier(self, user_id: str) -> str:
        """Get user tier from database or cache"""
        # In production, fetch from database
        # For now, return default
        return "free"


# Middleware for FastAPI
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for FastAPI"""
    
    def __init__(self, app, limiter: DistributedRateLimiter):
        super().__init__(app)
        self.limiter = limiter
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for certain endpoints
        if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get user ID from request (from JWT token)
        user_id = getattr(request.state, "user_id", "anonymous")
        user_tier = getattr(request.state, "user_tier", "free")
        
        # Check rate limit
        allowed, retry_after, info = await self.limiter.check_rate_limit(
            user_id, user_tier, request.url.path
        )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(info.get("limit", ""))
        response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", ""))
        response.headers["X-RateLimit-Reset"] = str(info.get("reset", ""))
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                    "limit": info.get("limit")
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        return response


# Decorator for endpoint-specific rate limiting
def rate_limit(requests: int = 10, window: int = 60):
    """Decorator for endpoint-specific rate limiting"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from request context
            request = kwargs.get("request") or args[0] if args else None
            if not request:
                return await func(*args, **kwargs)
            
            user_id = getattr(request.state, "user_id", "anonymous")
            
            # Custom rate limit key for this endpoint
            key = f"{func.__name__}:{user_id}"
            
            # Check rate limit (would need Redis connection)
            # Implementation similar to above
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
