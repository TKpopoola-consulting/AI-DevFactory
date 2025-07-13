from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class OutputConfig(BaseModel):
    frontend: str = Field("flutter", description="Frontend framework")
    backend: str = Field("fastapi", description="Backend framework")
    cloud: str = Field("azure", description="Cloud provider")
    platforms: List[str] = Field(["web"], description="Target platforms")

class JobRequest(BaseModel):
    prompt: str = Field(..., description="Natural language requirements")
    user_id: str = Field(..., description="User identifier")
    output_config: OutputConfig = Field(default_factory=OutputConfig)

class JobResponse(BaseModel):
    job_id: str
    status: str
    progress: Dict[str, float] = None
    artifacts: List[str] = None
    estimated_cost: float = None
    error: str = None

class AgentTask(BaseModel):
    agent_type: str
    parameters: Dict[str, str]
    dependencies: List[str] = []
    timeout: int = 300  # seconds