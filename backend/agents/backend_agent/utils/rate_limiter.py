# backend/agents/backend_agent/utils/rate_limiter.py
"""
Rate limiting utilities to prevent API quota exhaustion
"""
import time
import asyncio
import logging
from functools import wraps
from typing import Dict, Any, Callable
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TokenBucket:
    """Token bucket algorithm for rate limiting"""
    
    def __init__(self, rate: float, capacity: int):
        """
        Args:
            rate: Tokens added per second
            capacity: Maximum tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Consume tokens, returns True if successful"""
        now = time.time()
        
        # Refill tokens based on time elapsed
        elapsed = now - self.last_refill
        refill_tokens = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + refill_tokens)
        self.last_refill = now
        
        # Try to consume
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def get_wait_time(self) -> float:
        """Get time until next token is available"""
        if self.tokens >= 1:
            return 0
        return (1 - self.tokens) / self.rate


class RateLimiter:
    """Rate limiter with per-user/per-IP tracking"""
    
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self.default_rate = 10  # calls per minute
        self.default_capacity = 10
        self.user_limits: Dict[str, tuple] = {
            'premium': (50, 50),  # (rate per minute, capacity)
            'standard': (10, 10),
            'trial': (5, 5)
        }
    
    def get_bucket(self, key: str, user_tier: str = 'standard') -> TokenBucket:
        """Get or create token bucket for a key"""
        if key not in self.buckets:
            rate, capacity = self.user_limits.get(user_tier, (self.default_rate, self.default_capacity))
            # Convert rate from per minute to per second
            rate_per_second = rate / 60.0
            self.buckets[key] = TokenBucket(rate_per_second, capacity)
        return self.buckets[key]
    
    def is_allowed(self, key: str, user_tier: str = 'standard', tokens: int = 1) -> tuple[bool, float]:
        """Check if request is allowed, returns (allowed, wait_time)"""
        bucket = self.get_bucket(key, user_tier)
        
        if bucket.consume(tokens):
            return True, 0
        return False, bucket.get_wait_time()


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    def __init__(self, wait_time: float, limit: int):
        self.wait_time = wait_time
        self.limit = limit
        super().__init__(f"Rate limit exceeded. Try again in {wait_time:.1f} seconds")


def rate_limit(calls: int = 10, period: int = 60):
    """
    Decorator for rate limiting
    
    Args:
        calls: Maximum number of calls
        period: Time period in seconds
    """
    limiter = RateLimiter()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get user identifier from kwargs or context
            user_id = kwargs.get('user_id', 'anonymous')
            user_tier = kwargs.get('user_tier', 'standard')
            
            allowed, wait_time = limiter.is_allowed(user_id, user_tier)
            
            if not allowed:
                raise RateLimitError(wait_time, calls)
            
            return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id', 'anonymous')
            user_tier = kwargs.get('user_tier', 'standard')
            
            allowed, wait_time = limiter.is_allowed(user_id, user_tier)
            
            if not allowed:
                raise RateLimitError(wait_time, calls)
            
            return await func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


class AsyncRateLimiter:
    """Async rate limiter with sliding window"""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.window_size = 60  # seconds
        self.max_requests = 10
    
    async def acquire(self, key: str, max_requests: int = None, window: int = None) -> bool:
        """Acquire permission to make request"""
        max_req = max_requests or self.max_requests
        window_sec = window or self.window_size
        
        now = time.time()
        window_start = now - window_sec
        
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        
        if len(self.requests[key]) >= max_req:
            oldest = self.requests[key][0]
            wait_time = oldest + window_sec - now
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                return await self.acquire(key, max_req, window_sec)
        
        self.requests[key].append(now)
        return True


# Usage example in agent_logic.py
from utils.rate_limiter import rate_limit, RateLimitError

class BackendAgent:
    @rate_limit(calls=10, period=60)  # 10 calls per minute
    def generate_backend(self, description: str, framework: str, requirements: List[str], user_id: str = 'anonymous'):
        # Existing implementation...
        pass
