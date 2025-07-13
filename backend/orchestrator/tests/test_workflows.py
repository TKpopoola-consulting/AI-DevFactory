import pytest
from unittest.mock import AsyncMock, patch
from workflow_manager import WorkflowManager
from models import JobRequest
from database import JobDB
from utils.cache import JobCache

@pytest.fixture
def mock_db():
    db = JobDB()
    db.create_job = AsyncMock(return_value="job123")
    db.update_job = AsyncMock()
    return db

@pytest.fixture
def mock_cache():
    cache = JobCache()
    cache.set_job = AsyncMock()
    return cache

@pytest.mark.asyncio
async def test_workflow_execution(mock_db, mock_cache):
    with patch("agent_coordinator.AgentCoordinator.execute_task") as mock_execute:
        mock_execute.side_effect = [
            {"specifications": {"ui": "flutter", "api": "rest"}},  # spec_agent
            {"artifacts": {"frontend": "flutter_code"}},          # frontend_agent
            {"artifacts": {"backend": "fastapi_code"}},           # backend_agent
            {"artifacts": {"infra": "bicep_code"}},               # infra_agent
            {"passed": True},                                     # qa_agent
            {"package_url": "https://storage/package.zip"}        # packaging_agent
        ]
        
        manager = WorkflowManager(db=mock_db, cache=mock_cache)
        job_id = await manager.initiate_workflow(
            prompt="Create a task management app",
            user_id="user123",
            output_config={"frontend": "flutter", "cloud": "azure"}
        )
        
        assert job_id == "job123"
        assert mock_db.update_job.call_count == 2  # Initial + final update
        assert mock_cache.set_job.call_count == 1