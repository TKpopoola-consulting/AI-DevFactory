"""
Task Processor for AI-DevFactory
Handles parallel execution of agents with Redis/Celery backend
"""

import asyncio
import json
import sqlite3
import logging
import os
import redis
from typing import Dict, List, Optional
from datetime import datetime

from .agent_coordinator import AgentCoordinator
from .models import AgentTask, JobConfig, FrameworkSpec
from .prompt_decomposer import PromptDecomposer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task_processor")

DB_PATH = "/production/AI-DevFactory/jobs.db"


class TaskProcessor:
    """Process jobs and coordinate parallel agent execution"""

    def __init__(self):
        self.coordinator = AgentCoordinator()
        self.decomposer = PromptDecomposer()
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )

    def update_job_status(self, job_id: str, status: str, progress: int = 0,
                         message: str = "", agents: Dict = None):
        """Update job status in database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE jobs
               SET status = ?, progress = ?, updated_at = ?, message = ?
               WHERE job_id = ?""",
            (status, progress, datetime.now().isoformat(), message, job_id)
        )

        if agents:
            cursor.execute(
                """UPDATE jobs
                   SET agent_status = ?
                   WHERE job_id = ?""",
                (json.dumps(agents), job_id)
            )

        conn.commit()
        conn.close()

    async def process_job(self, job_id: str, prompt: str, config: JobConfig):
        """Main job processing pipeline"""
        try:
            # Step 1: Update status to processing
            self.update_job_status(job_id, "processing", 10, "Analyzing prompt...")

            # Step 2: Decompose prompt into agent tasks
            agent_tasks = self.decomposer.decompose_prompt(prompt, config)

            # Step 3: Execute agents in parallel
            self.update_job_status(job_id, "processing", 30, "Executing agents in parallel...")
            results = await self.execute_parallel_agents(agent_tasks, job_id)

            # Step 4: Aggregate results
            self.update_job_status(job_id, "processing", 70, "Aggregating results...")
            aggregated = self.aggregate_results(results)

            # Step 5: Finalize job
            self.update_job_status(job_id, "completed", 100, "Job completed successfully")

            return {
                "job_id": job_id,
                "status": "completed",
                "results": aggregated,
                "agents_executed": len(agent_tasks)
            }

        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}")
            self.update_job_status(job_id, "failed", 0, f"Error: {str(e)}")
            raise

    async def execute_parallel_agents(self, agent_tasks: List[AgentTask], job_id: str) -> Dict:
        """Execute multiple agents in parallel"""
        agent_results = {}

        # Create tasks for all agents
        tasks = []
        for task in agent_tasks:
            tasks.append(self.execute_agent_with_tracking(task, job_id))

        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, (task, result) in enumerate(zip(agent_tasks, results)):
            agent_name = task.agent_type
            if isinstance(result, Exception):
                logger.error(f"Agent {agent_name} failed: {result}")
                agent_results[agent_name] = {
                    "status": "failed",
                    "error": str(result)
                }
            else:
                agent_results[agent_name] = {
                    "status": "completed",
                    "result": result
                }

        return agent_results

    async def execute_agent_with_tracking(self, task: AgentTask, job_id: str):
        """Execute single agent with progress tracking"""
        try:
            # Update agent status in Redis for real-time tracking
            agent_key = f"job:{job_id}:agent:{task.agent_type}"
            self.redis_client.hset(agent_key, "status", "processing")
            self.redis_client.hset(agent_key, "started_at", datetime.now().isoformat())

            # Execute agent
            result = await self.coordinator.execute_task(task)

            # Update completion
            self.redis_client.hset(agent_key, "status", "completed")
            self.redis_client.hset(agent_key, "completed_at", datetime.now().isoformat())
            self.redis_client.hset(agent_key, "result", json.dumps(result))

            return result

        except Exception as e:
            self.redis_client.hset(agent_key, "status", "failed")
            self.redis_client.hset(agent_key, "error", str(e))
            raise

    def aggregate_results(self, agent_results: Dict) -> Dict:
        """Aggregate results from all agents into final output"""
        aggregated = {
            "frontend": None,
            "backend": None,
            "infrastructure": None,
            "quality_report": None,
            "specifications": None,
            "package": None,
            "fixes": None,
            "modifications": None
        }

        for agent_name, result in agent_results.items():
            if result["status"] == "completed":
                if agent_name == "frontend_agent":
                    aggregated["frontend"] = result["result"]
                elif agent_name == "backend_agent":
                    aggregated["backend"] = result["result"]
                elif agent_name == "infra_agent":
                    aggregated["infrastructure"] = result["result"]
                elif agent_name == "qa_agent":
                    aggregated["quality_report"] = result["result"]
                elif agent_name == "spec_agent":
                    aggregated["specifications"] = result["result"]
                elif agent_name == "packaging_agent":
                    aggregated["package"] = result["result"]
                elif agent_name == "fixer_agent":
                    aggregated["fixes"] = result["result"]
                elif agent_name == "modifier_agent":
                    aggregated["modifications"] = result["result"]

        return aggregated

    def get_job_progress(self, job_id: str) -> Dict:
        """Get real-time progress of a job"""
        agent_keys = self.redis_client.keys(f"job:{job_id}:agent:*")
        agents = {}

        for key in agent_keys:
            agent_name = key.split(":")[-1]
            agent_data = self.redis_client.hgetall(key)
            agents[agent_name] = agent_data

        return {
            "agents": agents,
            "overall_progress": self.calculate_overall_progress(agents)
        }

    def calculate_overall_progress(self, agents: Dict) -> int:
        """Calculate overall progress from agent statuses"""
        if not agents:
            return 0

        completed = sum(1 for a in agents.values() if a.get("status") == "completed")
        total = len(agents)

        return int((completed / total) * 100) if total > 0 else 0