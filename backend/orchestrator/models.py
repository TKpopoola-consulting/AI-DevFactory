from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class OutputConfig(BaseModel):
    frontend: str = Field("react", description="Frontend framework")
    backend: str = Field("fastapi", description="Backend framework")
    cloud: str = Field("azure", description="Cloud provider")
    platforms: List[str] = Field(["web"], description="Target platforms")
    database: str = Field("postgresql", description="Database type")
    monorepo: bool = Field(False, description="Use monorepo structure")

class JobRequest(BaseModel):
    prompt: str = Field(..., description="Natural language requirements")
    user_id: str = Field(..., description="User identifier")
    output_config: OutputConfig = Field(default_factory=OutputConfig)

class JobResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[float] = None
    artifacts: Optional[List[str]] = None
    estimated_cost: Optional[float] = None
    error: Optional[str] = None

class AgentTask(BaseModel):
    agent_type: str
    parameters: Dict[str, Any]
    dependencies: List[str] = []
    timeout: int = 300

class AgentResult(BaseModel):
    agent_type: str
    status: str
    artifacts: Dict[str, Any] = {}
    error: Optional[str] = None
    duration: Optional[float] = None

class WorkflowStatus(BaseModel):
    job_id: str
    status: str
    current_stage: str
    progress: int
    agents_status: Dict[str, str] = {}
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None

class Checkpoint(BaseModel):
    id: str
    job_id: str
    stage: str
    timestamp: datetime
    artifacts: Dict[str, Any] = {}
    is_restorable: bool = True
