"""
Prompt Decomposer for AI-DevFactory
Analyzes user prompts and decomposes them into agent tasks
"""

import re
import json
from typing import List, Dict
from enum import Enum

from .models import AgentTask, JobConfig, FrameworkSpec


class AgentType(Enum):
    FRONTEND = "frontend_agent"
    BACKEND = "backend_agent"
    INFRA = "infra_agent"
    QA = "qa_agent"
    SPEC = "spec_agent"
    PACKAGING = "packaging_agent"
    FIXER = "fixer_agent"
    MODIFIER = "modifier_agent"


class PromptDecomposer:
    """Decomposes user prompts into agent tasks"""

    def __init__(self):
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict:
        """Load patterns for detecting agent needs"""
        return {
            "frontend": [
                r"frontend", r"ui", r"user.?interface", r"react", r"vue", r"flutter",
                r"button", r"form", r"layout", r"component", r"css", r"html", r"design"
            ],
            "backend": [
                r"backend", r"api", r"server", r"database", r"authentication",
                r"endpoint", r"rest", r"graphql", r"python", r"node", r"java",
                r"spring", r"django", r"flask", r"express", r"fastapi"
            ],
            "infrastructure": [
                r"infrastructure", r"cloud", r"aws", r"azure", r"gcp", r"docker",
                r"kubernetes", r"deploy", r"ci.?cd", r"terraform", r"serverless",
                r"container", r"orchestration"
            ],
            "quality": [
                r"test", r"qa", r"quality", r"security", r"performance", r"bug",
                r"error", r"validate", r"check", r"scan", r"audit", r"coverage"
            ],
            "specification": [
                r"spec", r"requirement", r"document", r"plan", r"architecture",
                r"design.?pattern", r"uml", r"diagram", r"flow.?chart"
            ],
            "packaging": [
                r"package", r"deploy", r"release", r"build", r"distribute",
                r"install", r"configure", r"setup", r"environment"
            ],
            "fixer": [
                r"fix", r"bug", r"error", r"crash", r"broken", r"not.?working",
                r"issue", r"problem", r"debug", r"troubleshoot", r"repair"
            ],
            "modifier": [
                r"improve", r"refactor", r"optimize", r"enhance", r"clean.?up",
                r"restructure", r"reorganize", r"modernize", r"update", r"upgrade"
            ]
        }

    def decompose_prompt(self, prompt: str, config: JobConfig) -> List[AgentTask]:
        """Decompose a prompt into agent tasks"""
        prompt_lower = prompt.lower()

        # Determine which agents are needed
        needed_agents = self._detect_needed_agents(prompt_lower, config)

        # Create agent tasks
        agent_tasks = []
        for agent_type in needed_agents:
            task = self._create_agent_task(agent_type, prompt, config)
            agent_tasks.append(task)

        return agent_tasks

    def _detect_needed_agents(self, prompt: str, config: JobConfig) -> List[str]:
        """Detect which agents are needed based on prompt and config"""
        agents = set()

        # Check patterns for each agent type
        for agent_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    agents.add(agent_type)

        # Ensure at least frontend and backend for full app requests
        if self._is_full_application_request(prompt):
            agents.add("frontend")
            agents.add("backend")
            agents.add("infrastructure")
            agents.add("quality")

        # Check config for explicit agent requirements
        if config.agents:
            for agent in config.agents:
                if agent in self.patterns:
                    agents.add(agent)

        # Map to actual agent types
        agent_types = []
        for agent in agents:
            if agent == "frontend":
                agent_types.append(AgentType.FRONTEND.value)
            elif agent == "backend":
                agent_types.append(AgentType.BACKEND.value)
            elif agent == "infrastructure":
                agent_types.append(AgentType.INFRA.value)
            elif agent == "quality":
                agent_types.append(AgentType.QA.value)
            elif agent == "specification":
                agent_types.append(AgentType.SPEC.value)
            elif agent == "packaging":
                agent_types.append(AgentType.PACKAGING.value)
            elif agent == "fixer":
                agent_types.append(AgentType.FIXER.value)
            elif agent == "modifier":
                agent_types.append(AgentType.MODIFIER.value)

        return agent_types

    def _is_full_application_request(self, prompt: str) -> bool:
        """Check if this is a request for a full application"""
        full_app_keywords = [
            r"create.?app", r"build.?app", r"full.?stack", r"complete.?application",
            r"web.?app", r"mobile.?app", r"enterprise.?app", r"production.?ready"
        ]

        for keyword in full_app_keywords:
            if re.search(keyword, prompt, re.IGNORECASE):
                return True

        return False

    def _create_agent_task(self, agent_type: str, prompt: str, config: JobConfig) -> AgentTask:
        """Create an AgentTask for a specific agent type"""
        parameters = {
            "prompt": prompt,
            "config": config.dict()
        }

        # Add agent-specific parameters
        if agent_type == AgentType.FRONTEND.value:
            parameters["framework"] = config.frameworks.frontend
            parameters["requirements"] = config.requirements
        elif agent_type == AgentType.BACKEND.value:
            parameters["framework"] = config.frameworks.backend
            parameters["requirements"] = config.requirements
        elif agent_type == AgentType.INFRA.value:
            parameters["cloud_provider"] = config.cloud_provider
            parameters["deployment_target"] = config.deployment_target
        elif agent_type == AgentType.QA.value:
            parameters["test_framework"] = config.test_framework
            parameters["security_scan"] = config.security_scan

        return AgentTask(
            agent_type=agent_type,
            parameters=parameters,
            priority=self._get_agent_priority(agent_type),
            timeout=300  # 5 minutes default timeout
        )

    def _get_agent_priority(self, agent_type: str) -> int:
        """Get priority for agent execution order"""
        priority_map = {
            AgentType.SPEC.value: 1,          # First: specifications
            AgentType.FRONTEND.value: 2,      # Second: frontend
            AgentType.BACKEND.value: 2,       # Second: backend
            AgentType.INFRA.value: 3,         # Third: infrastructure
            AgentType.QA.value: 4,            # Fourth: quality assurance
            AgentType.PACKAGING.value: 5,     # Fifth: packaging
            AgentType.FIXER.value: 2,         # Second: fixing (parallel with dev)
            AgentType.MODIFIER.value: 2       # Second: modification
        }

        return priority_map.get(agent_type, 3)

    def estimate_complexity(self, prompt: str, config: JobConfig) -> Dict:
        """Estimate complexity of the request"""
        agent_tasks = self.decompose_prompt(prompt.lower(), config)

        complexity_score = len(agent_tasks) * 10

        if self._is_full_application_request(prompt.lower()):
            complexity_score += 30

        # Add points for each framework/technology
        if config.frameworks.frontend:
            complexity_score += 5
        if config.frameworks.backend:
            complexity_score += 5
        if config.cloud_provider:
            complexity_score += 5

        # Categorize complexity
        if complexity_score < 20:
            level = "simple"
        elif complexity_score < 40:
            level = "medium"
        elif complexity_score < 60:
            level = "complex"
        else:
            level = "very complex"

        return {
            "level": level,
            "score": complexity_score,
            "agents_needed": len(agent_tasks),
            "estimated_time_minutes": complexity_score * 2  # Rough estimate
        }