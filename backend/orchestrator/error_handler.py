import logging
from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    code: str
    job_id: str = None
    details: dict = None

class AgentCommunicationError(Exception):
    def __init__(self, message, agent_type):
        super().__init__(message)
        self.agent_type = agent_type

class WorkflowTimeoutError(Exception):
    pass

def handle_exceptions(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
            
        except AgentCommunicationError as e:
            logging.error(f"Agent error: {e.agent_type} - {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    error="Service unavailable",
                    code="AGENT_COMMUNICATION_FAILURE",
                    details={"agent": e.agent_type}
                ).dict()
            )
            
        except WorkflowTimeoutError as e:
            logging.error(f"Workflow timeout: {str(e)}")
            raise HTTPException(
                status_code=504,
                detail=ErrorResponse(
                    error="Processing timeout",
                    code="WORKFLOW_TIMEOUT"
                ).dict()
            )
            
        except Exception as e:
            logging.exception("Unexpected error")
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error="Internal server error",
                    code="INTERNAL_ERROR"
                ).dict()
            )
    return wrapper