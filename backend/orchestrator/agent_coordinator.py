import httpx
import logging
from models import AgentTask
from error_handler import AgentCommunicationError

class AgentCoordinator:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.agent_endpoints = {
            "frontend_agent": "http://frontend-agent:5000/generate",
            "backend_agent": "http://backend-agent:5000/generate",
            "infra_agent": "http://infra-agent:5000/generate",
            "qa_agent": "http://qa-agent:5000/analyze",
            "spec_agent": "http://spec-agent:5000/generate-spec",
            "packaging_agent": "http://packaging-agent:5000/package"
        }
        self.logger = logging.getLogger("agent_coordinator")

    async def execute_task(self, task: AgentTask) -> dict:
        endpoint = self.agent_endpoints.get(task.agent_type)
        if not endpoint:
            raise ValueError(f"Unknown agent type: {task.agent_type}")
        
        try:
            response = await self.client.post(
                endpoint,
                json=task.parameters,
                timeout=task.timeout
            )
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Agent error: {e.response.text}")
            raise AgentCommunicationError(
                f"{task.agent_type} returned {e.response.status_code}"
            ) from e
        
        except httpx.RequestError as e:
            self.logger.error(f"Network error: {str(e)}")
            raise AgentCommunicationError(
                f"Network failure contacting {task.agent_type}"
            ) from e