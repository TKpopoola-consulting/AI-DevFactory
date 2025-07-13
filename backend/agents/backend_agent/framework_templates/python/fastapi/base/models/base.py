from pydantic import BaseModel
from typing import Optional

class HealthCheck(BaseModel):
    status: str
    version: str = "1.0.0"
    service: Optional[str] = None