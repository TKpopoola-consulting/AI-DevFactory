import logging
import traceback
from fastapi import HTTPException
from pydantic import BaseModel

logger = logging.getLogger("orchestrator")

class ErrorResponse(BaseModel):
    error: str
    code: str
    job_id: str = None
    details: dict = None

def log_error(message: str):
    logger.error(f"{message}\n{traceback.format_exc()}")

def handle_exceptions(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            log_error(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error="Internal server error",
                    code="INTERNAL_ERROR"
                ).dict()
            )
    return wrapper