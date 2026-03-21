# backend/orchestrator/workflow_manager.py
"""
Complete Workflow Manager with parallel agent execution
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from database import JobDB
from agent_coordinator import AgentCoordinator, AgentTask
from models import JobRequest, AgentResult
from utils.cache import JobCache
from utils.artifact_integrator import ArtifactIntegrator
from utils.cost_calculator import CostCalculator
from utils.state_manager import CheckpointManager
from utils.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    INITIALIZING = "initializing"
    GENERATING_SPECS = "generating_specs"
    PARALLEL_AGENTS = "parallel_agents"
    QA_VALIDATION = "qa_validation"
    PACKAGING = "packaging"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowManager:
    """Manages the complete workflow from prompt to packaged application"""
    
    def __init__(self, db: JobDB = None, cache: JobCache = None):
        self.db = db or JobDB()
        self.cache = cache or JobCache()
        self.agent_coordinator = AgentCoordinator()
        self.artifact_integrator = ArtifactIntegrator()
        self.cost_calculator = CostCalculator()
        self.checkpoint_manager = CheckpointManager()
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        
        # Configuration
        self.config = {
            "continue_on_error": False,
            "monorepo": False,
            "max_parallel_agents": 3,
            "agent_timeout": 300
        }
        
    async def initiate_workflow(self, prompt: str, user_id: str, output_config: dict) -> str:
        """Create a new job and start the workflow"""
        try:
            # Create job record
            job_id = self.db.create_job(user_id, prompt, output_config)
            
            # Cache initial state
            self.cache.set_job(job_id, {
                "status": WorkflowStage.INITIALIZING.value,
                "progress": 0,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat()
            })
            
            # Start async workflow execution
            asyncio.create_task(self._execute_workflow(job_id, prompt, output_config))
            
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to initiate workflow: {e}")
            raise
    
    async def _execute_workflow(self, job_id: str, prompt: str, config: dict):
        """Main workflow execution with parallel agents"""
        
        try:
            # Create initial checkpoint
            await self.checkpoint_manager.create_checkpoint(job_id, WorkflowStage.INITIALIZING.value, {})
            
            # Phase 1: Generate specifications (sequential)
            await self._update_progress(job_id, WorkflowStage.GENERATING_SPECS.value, 5)
            specs = await self._generate_specifications(prompt, config)
            await self.checkpoint_manager.create_checkpoint(job_id, WorkflowStage.GENERATING_SPECS.value, {"specs": specs})
            
            # Phase 2: Parallel agent execution (FRONTEND, BACKEND, INFRA)
            await self._update_progress(job_id, WorkflowStage.PARALLEL_AGENTS.value, 10)
            parallel_results = await self._execute_parallel_agents(job_id, specs, config)
            await self.checkpoint_manager.create_checkpoint(job_id, WorkflowStage.PARALLEL_AGENTS.value, parallel_results)
            
            # Phase 3: QA validation
            await self._update_progress(job_id, WorkflowStage.QA_VALIDATION.value, 60)
            qa_results = await self._run_qa_validation(job_id, parallel_results, specs)
            
            # Phase 4: Artifact integration and packaging
            await self._update_progress(job_id, WorkflowStage.PACKAGING.value, 80)
            final_artifacts = await self._integrate_and_package(
                job_id, parallel_results, qa_results, config
            )
            await self.checkpoint_manager.create_checkpoint(job_id, WorkflowStage.PACKAGING.value, final_artifacts)
            
            # Phase 5: Export based on output configuration
            await self._update_progress(job_id, WorkflowStage.EXPORTING.value, 95)
            export_urls = await self._export_artifacts(job_id, final_artifacts, config)
            
            # Phase 6: Complete job
            await self._update_progress(job_id, WorkflowStage.COMPLETED.value, 100)
            total_cost = await self.cost_calculator.calculate_total_cost(job_id)
            
            self.db.update_job(job_id, {
                "status": WorkflowStage.COMPLETED.value,
                "artifacts": export_urls,
                "completed_at": datetime.utcnow().isoformat(),
                "actual_cost": total_cost
            })
            
            self.cache.set_job(job_id, {
                "status": WorkflowStage.COMPLETED.value,
                "progress": 100,
                "export_urls": export_urls
            })
            
        except Exception as e:
            logger.error(f"Workflow failed for job {job_id}: {e}")
            await self._handle_workflow_failure(job_id, str(e))
    
    async def _execute_parallel_agents(self, job_id: str, specs: dict, config: dict) -> Dict[str, Any]:
        """
        Execute frontend, backend, and infra agents in parallel
        
        This is the CORE missing piece that enables true parallel execution
        """
        logger.info(f"Starting parallel agent execution for job {job_id}")
        
        # Create tasks for parallel execution
        tasks = []
        task_names = []
        
        # Frontend Agent
        if config.get("frontend"):
            task_names.append("frontend")
            tasks.append(self._execute_frontend_agent(job_id, specs, config))
        
        # Backend Agent
        if config.get("backend"):
            task_names.append("backend")
            tasks.append(self._execute_backend_agent(job_id, specs, config))
        
        # Infrastructure Agent
        if config.get("infra") or config.get("cloud"):
            task_names.append("infra")
            tasks.append(self._execute_infra_agent(job_id, specs, config))
        
        # QA Agent (runs in parallel with others but will wait for completion)
        task_names.append("qa")
        tasks.append(self._execute_qa_agent(job_id, specs, config))
        
        # Execute all agents in parallel
        logger.info(f"Executing {len(tasks)} agents in parallel: {task_names}")
        
        # Use asyncio.gather with return_exceptions to handle failures gracefully
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle failures
        artifacts = {}
        failures = []
        
        for i, result in enumerate(results):
            agent_name = task_names[i]
            
            if isinstance(result, Exception):
                logger.error(f"Agent {agent_name} failed: {result}")
                failures.append({
                    "agent": agent_name,
                    "error": str(result)
                })
                
                if not self.config.get("continue_on_error"):
                    raise result
            else:
                artifacts.update(result)
                logger.info(f"Agent {agent_name} completed successfully")
        
        # Record failures in job if any
        if failures:
            self.db.update_job(job_id, {
                "agent_failures": failures,
                "partial_completion": len(artifacts) > 0
            })
        
        return artifacts
    
    async def _execute_frontend_agent(self, job_id: str, specs: dict, config: dict) -> Dict:
        """Execute frontend agent with circuit breaker protection"""
        
        task = AgentTask(
            agent_type="frontend_agent",
            parameters={
                "job_id": job_id,
                "prompt": specs.get("ui_requirements", specs.get("prompt", "")),
                "framework": config.get("frontend", "react"),
                "platforms": config.get("platforms", ["web"]),
                "styling": config.get("styling", "tailwind"),
                "state_management": config.get("state_management", "context")
            },
            timeout=self.config.get("agent_timeout", 300)
        )
        
        try:
            # Use circuit breaker to protect against failing agents
            result = await self.circuit_breaker.call(
                self.agent_coordinator.execute_task,
                task
            )
            return {"frontend": result.get("artifacts", result)}
        except Exception as e:
            logger.error(f"Frontend agent failed: {e}")
            raise
    
    async def _execute_backend_agent(self, job_id: str, specs: dict, config: dict) -> Dict:
        """Execute backend agent with circuit breaker protection"""
        
        task = AgentTask(
            agent_type="backend_agent",
            parameters={
                "job_id": job_id,
                "description": specs.get("api_requirements", specs.get("prompt", "")),
                "framework": config.get("backend", "fastapi"),
                "database": config.get("database", "postgresql"),
                "api_specs": specs.get("api_specs", {}),
                "auth_required": config.get("auth_required", True)
            },
            timeout=self.config.get("agent_timeout", 300)
        )
        
        try:
            result = await self.circuit_breaker.call(
                self.agent_coordinator.execute_task,
                task
            )
            return {"backend": result.get("artifacts", result)}
        except Exception as e:
            logger.error(f"Backend agent failed: {e}")
            raise
    
    async def _execute_infra_agent(self, job_id: str, specs: dict, config: dict) -> Dict:
        """Execute infrastructure agent"""
        
        task = AgentTask(
            agent_type="infra_agent",
            parameters={
                "job_id": job_id,
                "cloud_provider": config.get("cloud", "azure"),
                "services": self._determine_services(config),
                "scaling": config.get("scaling", {}),
                "environment": config.get("environment", "dev"),
                "region": config.get("region", "eastus")
            },
            timeout=self.config.get("agent_timeout", 300)
        )
        
        try:
            result = await self.circuit_breaker.call(
                self.agent_coordinator.execute_task,
                task
            )
            return {"infra": result.get("templates", result)}
        except Exception as e:
            logger.error(f"Infra agent failed: {e}")
            raise
    
    async def _execute_qa_agent(self, job_id: str, specs: dict, config: dict) -> Dict:
        """Execute QA agent for validation"""
        
        # QA agent runs in parallel but will wait for other agents to complete
        # We'll use a separate task that monitors completion
        
        task = AgentTask(
            agent_type="qa_agent",
            parameters={
                "job_id": job_id,
                "language": self._determine_language(config),
                "framework": config.get("backend", "fastapi"),
                "test_coverage": config.get("test_coverage", 70)
            },
            timeout=180
        )
        
        try:
            # Wait for other agents to complete (monitor job status)
            await self._wait_for_agents_completion(job_id)
            
            # Run QA analysis
            result = await self.agent_coordinator.execute_task(task)
            return {"qa": result.get("report", result)}
        except Exception as e:
            logger.error(f"QA agent failed: {e}")
            return {"qa": {"error": str(e), "status": "failed"}}
    
    async def _wait_for_agents_completion(self, job_id: str, timeout: int = 300):
        """Wait for frontend/backend/infra agents to complete"""
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).seconds < timeout:
            job = self.db.get_job(job_id)
            if job:
                agents_status = job.get("agents_status", {})
                completed = all(
                    status.get("status") == "completed"
                    for status in agents_status.values()
                )
                if completed:
                    return
            await asyncio.sleep(2)
        
        logger.warning(f"Timeout waiting for agents completion for job {job_id}")
    
    async def _generate_specifications(self, prompt: str, config: dict) -> dict:
        """Generate technical specifications"""
        # Use spec agent to generate specs
        task = AgentTask(
            agent_type="spec_agent",
            parameters={
                "prompt": prompt,
                "config": config,
                "requirements": self._extract_requirements(prompt)
            },
            timeout=60
        )
        
        try:
            result = await self.agent_coordinator.execute_task(task)
            return {
                "api_specs": result.get("api_specs", {}),
                "database_schema": result.get("database_schema", {}),
                "ui_components": result.get("ui_components", []),
                "security_requirements": result.get("security", {}),
                "scalability_needs": result.get("scalability", {}),
                "prompt": prompt
            }
        except Exception as e:
            logger.error(f"Spec generation failed: {e}")
            # Fallback: create basic specs from prompt
            return {
                "prompt": prompt,
                "ui_requirements": prompt,
                "api_requirements": prompt
            }
    
    async def _run_qa_validation(self, job_id: str, artifacts: Dict, specs: dict) -> Dict:
        """Run QA validation on generated code"""
        # QA results already collected from parallel execution
        return artifacts.get("qa", {})
    
    async def _integrate_and_package(self, job_id: str, artifacts: Dict, qa_results: Dict, config: dict) -> Dict:
        """Integrate all artifacts and package final project"""
        return await self.artifact_integrator.merge_artifacts(job_id, artifacts, config)
    
    async def _export_artifacts(self, job_id: str, artifacts: Dict, config: dict) -> Dict:
        """Export artifacts based on output configuration"""
        export_urls = {}
        
        if config.get("export_to_github"):
            export_urls["github"] = await self._export_to_github(job_id, artifacts)
        
        if config.get("export_to_blob"):
            export_urls["blob"] = await self._export_to_blob(job_id, artifacts)
        
        if config.get("export_as_zip"):
            export_urls["zip"] = await self._export_as_zip(job_id, artifacts)
        
        return export_urls
    
    async def _update_progress(self, job_id: str, stage: str, progress: int):
        """Update job progress"""
        self.cache.set_job(job_id, {
            "status": stage,
            "progress": progress,
            "stage": stage
        })
        
        self.db.update_job(job_id, {
            "status": stage,
            "progress": progress
        })
    
    async def _handle_workflow_failure(self, job_id: str, error: str):
        """Handle workflow failure"""
        self.cache.set_job(job_id, {
            "status": WorkflowStage.FAILED.value,
            "error": error
        })
        
        self.db.update_job(job_id, {
            "status": WorkflowStage.FAILED.value,
            "error": error,
            "failed_at": datetime.utcnow().isoformat()
        })
        
        # Try to restore from last checkpoint if available
        await self.checkpoint_manager.restore_last_checkpoint(job_id)
    
    def _determine_services(self, config: dict) -> List[str]:
        """Determine infrastructure services needed"""
        services = []
        
        if config.get("frontend"):
            services.append("compute")
        if config.get("backend"):
            services.append("compute")
        if config.get("database"):
            services.append("database")
        if config.get("storage"):
            services.append("storage")
        
        # Add default services
        services.extend(["monitoring", "networking"])
        
        return list(set(services))
    
    def _determine_language(self, config: dict) -> str:
        """Determine programming language from config"""
        backend = config.get("backend", "fastapi")
        
        if backend in ["fastapi", "django", "flask"]:
            return "python"
        elif backend in ["express", "nestjs", "nodejs"]:
            return "javascript"
        
        return "python"
    
    def _extract_requirements(self, prompt: str) -> List[str]:
        """Extract requirements from prompt"""
        # Simple extraction - in production, use NLP
        requirements = []
        
        keywords = ["must have", "requires", "needs to", "should"]
        for keyword in keywords:
            if keyword in prompt.lower():
                # Extract sentences containing keywords
                sentences = prompt.split(".")
                for sentence in sentences:
                    if keyword in sentence.lower():
                        requirements.append(sentence.strip())
        
        return requirements[:5]  # Limit to 5 requirements
