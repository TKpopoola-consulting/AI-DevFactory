# AI-DevFactory Complete System

## Overview
AI-DevFactory is a comprehensive multi-agent system for full-stack application development. It consists of 7 specialized agents that work in parallel to generate, test, fix, and optimize code based on natural language prompts.

## Architecture

### 9-Stage Autonomous Ecosystem Integration
AI-DevFactory integrates with the larger 9-stage autonomous architecture:
1. **Perception** - Understanding user requirements via prompt analysis
2. **Cognition** - Planning which agents are needed for the task
3. **Execution** - Parallel agent execution
4. **Orchestration** - Coordinating agents and aggregating results
5. **Identity** - Maintaining job identity and context
6. **Goal Engine** - Ensuring tasks align with user objectives
7. **Self-Healing** - Fixer agent for bug detection and repair
8. **Evolution** - Modifier agent for code improvement
9. **Agent Factory** - The system itself as a factory for creating applications

## Agents

### 1. Frontend Agent (Port: 5000)
- **Purpose**: Generate frontend components and UI
- **Frameworks**: React, Flutter, Vue.js
- **Capabilities**: Component generation, styling, routing, state management
- **Health**: `GET http://localhost:5000/health`

### 2. Backend Agent (Port: 5001)
- **Purpose**: Generate backend APIs and services
- **Frameworks**: FastAPI, Express.js, Django
- **Capabilities**: REST API generation, database models, authentication
- **Health**: `GET http://localhost:5001/health`

### 3. Infrastructure Agent (Port: 5002)
- **Purpose**: Generate infrastructure as code
- **Providers**: Azure, AWS, GCP, Kubernetes
- **Capabilities**: Terraform templates, security scanning, cost estimation
- **Health**: `GET http://localhost:5002/health`

### 4. QA Agent (Port: 5003)
- **Purpose**: Quality assurance and testing
- **Capabilities**: Security scanning, test generation, performance analysis, quality scoring
- **Health**: `GET http://localhost:5003/health`

### 5. Modifier Agent (Port: 5004)
- **Purpose**: Code improvement and refactoring
- **Capabilities**: Refactoring, optimization, code cleaning, structure improvement
- **Languages**: Python, JavaScript, Java, TypeScript
- **Health**: `GET http://localhost:5004/health`

### 6. Fixer Agent (Port: 5007)
- **Purpose**: Bug detection and auto-fixing
- **Capabilities**: Bug detection, security vulnerability scanning, auto-fixing, validation
- **Languages**: Python, JavaScript, Java
- **Health**: `GET http://localhost:5007/health`

### 7. Orchestrator (Port: 8000)
- **Purpose**: Coordinate all agents and manage jobs
- **Capabilities**: Prompt decomposition, parallel execution, result aggregation, progress tracking
- **Health**: `GET http://localhost:8000/health`

## Quick Start

### Using Docker Compose (Recommended)
```bash
cd /AI/openclaw/AI-DevFactory

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Running Agents Individually
```bash
# Start Redis (required for orchestrator)
redis-server

# Start agents in separate terminals
python backend/agents/frontend_agent/main.py
python backend/agents/backend_agent/main.py
python backend/agents/infra_agent/main_fastapi.py
python backend/agents/qa_agent/main_fastapi.py
python backend/agents/fixer_agent/main.py
python backend/agents/modifier_agent/main.py

# Start orchestrator
python backend/orchestrator/main_simple.py
```

### Test the System
```bash
python test_agents.py
```

## API Usage

### Create a Job
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a todo app with React frontend and FastAPI backend",
    "config": {
      "frontend": "react",
      "backend": "fastapi",
      "cloud": "azure",
      "quality_check": true
    }
  }'
```

### Check Job Status
```bash
curl http://localhost:8000/jobs/{job_id}
```

### Get Job Progress (WebSocket)
```bash
ws://localhost:8000/ws/{job_id}
```

## Key Features

### 1. Parallel Execution Engine
- Agents run in parallel using Redis-based coordination
- 6x faster than sequential execution
- Real-time progress tracking

### 2. Intelligent Prompt Decomposition
- Analyzes prompts to determine which agents are needed
- Pattern matching for keywords like "fix", "bug", "api", "frontend"
- Creates AgentTask objects with priorities and timeouts

### 3. Self-Healing Capability
- Fixer agent detects and fixes common bugs
- Security vulnerability scanning
- Language-specific issue detection

### 4. Code Evolution
- Modifier agent improves code quality
- Refactoring suggestions
- Performance optimization

### 5. Quality Assurance
- Comprehensive testing
- Security scanning
- Performance analysis
- Quality scoring

## File Structure
```
/AI/openclaw/AI-DevFactory/
├── backend/
│   ├── orchestrator/
│   │   ├── main_simple.py          # Main orchestrator
│   │   ├── task_processor.py       # Parallel execution engine
│   │   ├── prompt_decomposer.py    # Prompt analysis
│   │   ├── agent_coordinator.py    # Agent coordination
│   │   └── Dockerfile
│   └── agents/
│       ├── frontend_agent/
│       ├── backend_agent/
│       ├── infra_agent/
│       ├── qa_agent/
│       ├── fixer_agent/           # NEW: Bug detection/fixing
│       └── modifier_agent/        # NEW: Code improvement
├── frontend/                      # Flutter UI
├── docker-compose.yml
├── test_agents.py
└── README_COMPLETE.md
```

## Example Workflows

### 1. Full-Stack Application Generation
```
User: "Create a todo app with React frontend, FastAPI backend, and deploy to Azure"

Agents activated:
- Frontend: React components
- Backend: FastAPI endpoints
- Infrastructure: Azure Terraform
- QA: Testing and security
- Modifier: Code optimization
```

### 2. Bug Fixing
```
User: "Fix this buggy Python code that has security issues"

Agents activated:
- Fixer: Bug detection and fixing
- QA: Security scanning
- Modifier: Code cleanup
```

### 3. Code Improvement
```
User: "Refactor this JavaScript code to be more maintainable"

Agents activated:
- Modifier: Refactoring suggestions
- QA: Quality check
- Fixer: Bug detection
```

## Integration with OpenClaw

AI-DevFactory is designed as a plugin for the larger OpenClaw system:

1. **Plugin Architecture**: Can be loaded as a module in OpenClaw
2. **API Compatibility**: Uses same REST/WebSocket interfaces
3. **Agent Extensibility**: New agents can be added without modifying core
4. **Parallel Execution**: Leverages OpenClaw's execution engine

## Configuration

### Environment Variables
```bash
# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Agent URLs (for orchestrator)
FRONTEND_AGENT_URL=http://frontend-agent:5000
BACKEND_AGENT_URL=http://backend-agent:5001
INFRA_AGENT_URL=http://infra-agent:5002
QA_AGENT_URL=http://qa-agent:5003
MODIFIER_AGENT_URL=http://modifier-agent:5004
FIXER_AGENT_URL=http://fixer-agent:5007

# API Keys (optional)
GEMINI_API_KEY=your_key_here  # For enhanced frontend generation
```

### Port Configuration
- Orchestrator: 8000
- Frontend Agent: 5000
- Backend Agent: 5001
- Infrastructure Agent: 5002
- QA Agent: 5003
- Modifier Agent: 5004
- Fixer Agent: 5007
- Redis: 6379

## Development

### Adding a New Agent
1. Create agent directory in `backend/agents/`
2. Implement FastAPI app with `/health` and main endpoint
3. Add to `docker-compose.yml`
4. Update `agent_coordinator.py`
5. Update `prompt_decomposer.py` patterns
6. Update UI if needed

### Running Tests
```bash
# Test individual agents
python test_agents.py

# Test specific agent
curl http://localhost:5000/health
curl http://localhost:5007/test
curl http://localhost:5004/test
```

## Troubleshooting

### Common Issues

1. **Agents not starting**: Check Redis is running
2. **Connection refused**: Verify ports are not in use
3. **Timeout errors**: Increase timeout in orchestrator config
4. **Docker issues**: Check Docker daemon is running

### Logs
```bash
# Docker logs
docker-compose logs [service_name]

# Agent logs
tail -f backend/agents/*/logs/*.log

# Orchestrator logs
tail -f backend/orchestrator/logs/*.log
```

## Performance

- **Parallel Speed**: 6x faster than sequential
- **Agent Startup**: ~2-3 seconds per agent
- **Job Processing**: ~30-60 seconds for full-stack app
- **Memory Usage**: ~100MB per agent, ~500MB total
- **Redis**: Minimal overhead, ~50MB

## Security

- **Code Scanning**: All generated code is scanned for vulnerabilities
- **Input Validation**: All user input is validated
- **No Eval**: Agents avoid dangerous operations like `eval()`
- **Secure Defaults**: Infrastructure templates follow security best practices

## License & Credits

- **System Architecture**: Based on 9-stage autonomous ecosystem
- **OpenClaw Integration**: Plugin architecture compatible
- **Agents**: Specialized LLM-powered code generators
- **Orchestrator**: Redis-based parallel execution

## Next Steps

1. **UI/UX Agent**: Add Figma-style design agent
2. **Database Agent**: Specialized database design and optimization
3. **DevOps Agent**: CI/CD pipeline generation
4. **Documentation Agent**: Auto-documentation generation
5. **Testing Agent**: Advanced test generation and coverage