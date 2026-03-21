# backend/agents/backend_agent/error_handler.py (Enhanced)
"""
Enhanced error handling with retry logic and detailed error messages
"""
import logging
import asyncio
import time
from functools import wraps
from typing import Callable, Type, Tuple, Optional
from enum import Enum
from flask import jsonify

logger = logging.getLogger(__name__)

class BackendErrorCode(Enum):
    """Enhanced error codes with categories"""
    # Template errors (2000-2099)
    TEMPLATE_LOAD_FAILED = 2001
    TEMPLATE_PARSE_ERROR = 2002
    TEMPLATE_VALIDATION_FAILED = 2003
    
    # Framework errors (2100-2199)
    FRAMEWORK_NOT_SUPPORTED = 2101
    FRAMEWORK_VERSION_MISMATCH = 2102
    
    # Validation errors (2200-2299)
    VALIDATION_FAILED = 2201
    SYNTAX_ERROR = 2202
    DEPENDENCY_MISSING = 2203
    
    # Container errors (2300-2399)
    CONTAINER_VALIDATION_ERROR = 2301
    DOCKER_DAEMON_ERROR = 2302
    
    # AI errors (2400-2499)
    GEMINI_API_ERROR = 2401
    GEMINI_RATE_LIMIT = 2402
    GEMINI_TIMEOUT = 2403
    
    # Network errors (2500-2599)
    NETWORK_ERROR = 2501
    TIMEOUT_ERROR = 2502
    
    # Internal errors (5000-5099)
    INTERNAL_ERROR = 5000
    MEMORY_ERROR = 5001


class BackendAgentError(Exception):
    """Enhanced exception with retry support"""
    
    def __init__(
        self, 
        message: str, 
        code: BackendErrorCode, 
        details: dict = None, 
        retryable: bool = False,
        retry_delay: float = 1.0,
        max_retries: int = 3
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.retryable = retryable
        self.retry_delay = retry_delay
        self.max_retries = max_retries
        super().__init__(message)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response"""
        return {
            "error": self.message,
            "code": self.code.value,
            "code_name": self.code.name,
            "details": self.details,
            "retryable": self.retryable
        }


def retry_with_backoff(
    retries: int = 3, 
    backoff_base: float = 1.0,
    max_backoff: float = 30.0,
    retry_on: Tuple[Type[Exception], ...] = (BackendAgentError,),
    retry_predicate: Optional[Callable] = None
):
    """
    Retry decorator with exponential backoff
    
    Args:
        retries: Maximum number of retry attempts
        backoff_base: Base backoff time in seconds
        max_backoff: Maximum backoff time
        retry_on: Exception types that trigger retry
        retry_predicate: Function that takes exception and returns bool
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry
                    should_retry = False
                    
                    if isinstance(e, retry_on):
                        if hasattr(e, 'retryable') and e.retryable:
                            should_retry = True
                        elif retry_predicate and retry_predicate(e):
                            should_retry = True
                    
                    if not should_retry or attempt == retries:
                        raise
                    
                    # Calculate backoff
                    backoff = min(backoff_base * (2 ** attempt), max_backoff)
                    jitter = backoff * 0.1  # Add 10% jitter
                    sleep_time = backoff + jitter
                    
                    logger.warning(
                        f"Retry {attempt + 1}/{retries} for {func.__name__} "
                        f"after {sleep_time:.2f}s: {str(e)}"
                    )
                    
                    time.sleep(sleep_time)
            
            # Should never reach here
            raise last_exception
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry
                    should_retry = False
                    
                    if isinstance(e, retry_on):
                        if hasattr(e, 'retryable') and e.retryable:
                            should_retry = True
                        elif retry_predicate and retry_predicate(e):
                            should_retry = True
                    
                    if not should_retry or attempt == retries:
                        raise
                    
                    # Calculate backoff
                    backoff = min(backoff_base * (2 ** attempt), max_backoff)
                    jitter = backoff * 0.1
                    sleep_time = backoff + jitter
                    
                    logger.warning(
                        f"Retry {attempt + 1}/{retries} for {func.__name__} "
                        f"after {sleep_time:.2f}s: {str(e)}"
                    )
                    
                    await asyncio.sleep(sleep_time)
            
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def handle_backend_errors(f):
    """Enhanced error handler with detailed responses"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BackendAgentError as e:
            logger.error(
                f"[{e.code.name}] {e.message}",
                extra={"details": e.details}
            )
            return jsonify(e.to_dict()), 400
        except TimeoutError as e:
            logger.error(f"Timeout error: {str(e)}")
            return jsonify({
                "error": "Request timeout",
                "code": 504,
                "retryable": True,
                "details": {"timeout": str(e)}
            }), 504
        except ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            return jsonify({
                "error": "Service unavailable",
                "code": 503,
                "retryable": True,
                "details": {"connection": str(e)}
            }), 503
        except MemoryError as e:
            logger.critical(f"Memory error: {str(e)}")
            return jsonify({
                "error": "Insufficient memory",
                "code": 507,
                "retryable": False
            }), 507
        except Exception as e:
            logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
            return jsonify({
                "error": "Internal server error",
                "code": 500,
                "retryable": True,
                "details": {"exception": str(e)} if os.getenv("DEBUG") else None
            }), 500
    return wrapper


# Updated agent_logic.py with retry for Gemini calls
class BackendAgent:
    @retry_with_backoff(
        retries=3,
        backoff_base=2.0,
        retry_on=(BackendAgentError,),
        retry_predicate=lambda e: e.retryable if hasattr(e, 'retryable') else False
    )
    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini with retry logic"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Determine if retryable
            retryable = any([
                "rate limit" in str(e).lower(),
                "timeout" in str(e).lower(),
                "connection" in str(e).lower()
            ])
            
            raise BackendAgentError(
                message=f"Gemini API error: {str(e)}",
                code=BackendErrorCode.GEMINI_API_ERROR,
                details={"original_error": str(e)},
                retryable=retryable
            ) from e
