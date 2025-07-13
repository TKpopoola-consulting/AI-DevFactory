from fastapi import APIRouter
from models.base import HealthCheck

router = APIRouter()

@router.get("/health", response_model=HealthCheck)
async def health_check():
    return {"status": "OK", "service": "{{app_name}}"}