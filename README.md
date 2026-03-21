🤖 AI DevFactory
Transform Ideas into Production-Ready Code with 4 Parallel AI Agents
https://img.shields.io/badge/License-MIT-yellow.svg
https://img.shields.io/badge/python-3.11+-blue.svg
https://img.shields.io/badge/flutter-3.19+-blue.svg
https://img.shields.io/badge/FastAPI-0.104+-green.svg

What is AI DevFactory?
AI DevFactory is an open-source, AI-driven continuous coding system that transforms natural language requirements into production-ready full-stack applications. It uses 4 parallel AI agents working simultaneously to generate frontend, backend, infrastructure, and QA code in minutes.

The Vision: Developer Firm in a Box

AI DevFactory replaces an entire development team:

Frontend Developer

Backend Developer

DevOps Engineer

QA Engineer

Technical Writer

Security Expert

All for less than a cup of coffee.

Key Features
Feature	Description
Natural Language to Code	Describe your app in plain English
Parallel Execution	4 agents work simultaneously (4x faster)
Real-time Updates	Watch live logs and progress via WebSocket
Quality Assurance	Automatic security scans, tests, performance
Multi-Cloud	Deploy to Azure, AWS, or GCP
Checkpoint System	Rollback to any stage
Cost Tracking	Real-time cost estimation
Extensible	Easy to add new agents
Multi-Framework	React, Flutter, Vue.js, FastAPI, Django
Dark Mode	Beautiful UI with light/dark themes
System Architecture
High-Level Architecture
text
USER INTERACTION
        │
        ├──────────────────┬──────────────────┐
        ▼                  ▼                  ▼
  Flutter Web         HTML Frontend      API Direct
        │                  │                  │
        └──────────────────┼──────────────────┘
                          ▼
              ┌─────────────────────┐
              │   ORCHESTRATOR API  │
              │   (FastAPI :8000)   │
              │ • REST Endpoints    │
              │ • WebSocket         │
              │ • Job Management    │
              │ • Agent Coordination│
              └──────────┬──────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   PostgreSQL         Redis           SQLite
   (Jobs DB)         (Cache)         (Fallback)
Agent Architecture - 4 Parallel Agents
text
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  FRONTEND       │  │  BACKEND        │  │  INFRA          │  │  QA             │
│  AGENT          │  │  AGENT          │  │  AGENT          │  │  AGENT          │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ Generates:      │  │ Generates:      │  │ Generates:      │  │ Validates:      │
│ • React         │  │ • FastAPI       │  │ • Azure Bicep   │  │ • Security      │
│ • Flutter       │  │ • Django        │  │ • AWS Terraform │  │ • Tests         │
│ • Vue.js        │  │ • Express       │  │ • GCP Terraform │  │ • Coverage      │
│ • Tailwind      │  │ • PostgreSQL    │  │ • Auto-scaling  │  │ • Performance   │
│ • Redux/Pinia   │  │ • JWT Auth      │  │ • Monitoring    │  │ • Best Practices│
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
        │                    │                    │                    │
        └────────────────────┴────────────────────┴────────────────────┘
                                        │
                                        ▼
                              ┌─────────────────┐
                              │  FINAL OUTPUT   │
                              │  • GitHub PR    │
                              │  • ZIP Download │
                              │  • Azure Blob   │
                              └─────────────────┘
Complete System Flow
Phase 1: Job Submission (0-5 seconds)
User enters prompt: "Build a task management app with user authentication"

User selects stack: React + FastAPI + Azure

User clicks "Generate Application"

Frontend sends POST /jobs to Orchestrator

Orchestrator validates request, creates job record, returns job_id

WebSocket connection opens for real-time updates

Phase 2: Specification Generation (10-30 seconds)
Spec Agent analyzes prompt and generates technical specifications

Output includes: API specifications, database schema, UI components, security requirements

Checkpoint created and saved

Progress updated: 5%

Phase 3: Parallel Agent Execution (2-3 minutes) - 4x Faster!
All 4 agents run simultaneously:

Agent	Input	Output
Frontend Agent	UI specs, components	React components, Tailwind CSS, Redux store
Backend Agent	API specs, DB schema	FastAPI endpoints, PostgreSQL ORM, JWT auth
Infra Agent	Cloud specs, scaling	Azure Bicep, App Service, Cosmos DB
QA Agent	All specs, generated code	Security scan, test results, quality report
Progress updates continuously via WebSocket.

Phase 4: Integration & Packaging (5-10 seconds)
Artifact Integrator merges all outputs into final project structure:

frontend/ - React components

backend/ - FastAPI code

infrastructure/ - Azure Bicep templates

tests/ - Generated tests

docs/ - README.md

docker-compose.yml - Local development setup

Phase 5: Export & Delivery (5-10 seconds)
Based on user's output configuration:

GitHub PR: Creates repository and pull request

Azure Blob: Uploads ZIP archive with signed URL

ZIP Download: Streams ZIP file to user

Phase 6: Completion & Notification (2-5 seconds)
Database updated: status = "completed", progress = 100%

Cost calculated and displayed

WebSocket pushes final status with download URL

Real-Time WebSocket Communication Flow
text
FRONTEND                              ORCHESTRATOR
    │                                      │
    │  WebSocket Connection                 │
    ├─────────────────────────────────────►│
    │◄─────────────────────────────────────┤
    │                                      │
    │  Subscribe to job updates             │
    ├─────────────────────────────────────►│
    │                                      │
    │◄─────────── Progress: 5% ────────────┤
    │  {"type":"progress","stage":"specs"}  │
    │                                      │
    │◄─────────── Progress: 10% ───────────┤
    │  {"type":"agent_start","agent":"frontend"}
    │                                      │
    │◄─────────── Log: Frontend 75% ───────┤
    │  {"type":"log","agent":"frontend",    │
    │   "message":"Generating components..."}
    │                                      │
    │◄─────────── Checkpoint Created ──────┤
    │  {"type":"checkpoint","stage":"frontend"}
    │                                      │
    │◄─────────── Quality Report ──────────┤
    │  {"type":"quality","score":85}        │
    │                                      │
    │  User provides feedback (if stuck)   │
    ├─────────────────────────────────────►│
    │  {"type":"feedback","message":"Use ORM"}
    │                                      │
    │◄─────────── Completed ───────────────┤
    │  {"type":"completed","download_url":"..."}
    │                                      │
    │  WebSocket Closed                     │
    └──────────────────────────────────────┘
Error Handling & Recovery
text
AGENT EXECUTION
       │
       ▼
┌─────────────────┐
│  Agent Fails?   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
Network    API Error  Validation
Error      (4xx/5xx)  Error
    │         │          │
    └────┬────┴──────────┘
         ▼
┌─────────────────┐
│  Retry Logic    │
│  Exponential    │
│  Backoff        │
│  Max 3 attempts │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
Success    All Retries
Continue   Failed
              │
              ▼
    ┌─────────────────┐
    │  Circuit Breaker│
    │  Opens after 3  │
    │  failures       │
    └────────┬────────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
Checkpoint Human    Partial
Restore   Interven- Success
          tion
Supported Technologies
Frontend Frameworks
Framework	Status	Features
React 18+	Fully Supported	Hooks, Context, Redux, Tailwind
Flutter 3.19+	Fully Supported	Material Design, Riverpod
Vue.js 3+	Fully Supported	Composition API, Pinia
Backend Frameworks
Framework	Status	Features
FastAPI	Fully Supported	Async, OpenAPI, Pydantic
Django	Fully Supported	ORM, Admin, Migrations
Express.js	Fully Supported	Middleware, Routing
Cloud Providers
Provider	Status	IaC Format
Microsoft Azure	Fully Supported	Bicep
Amazon Web Services	Fully Supported	Terraform
Google Cloud Platform	Fully Supported	Terraform
Quick Start
Prerequisites
Python 3.11+

Flutter 3.19+

Docker (optional)

Git

Installation (5 Minutes)
bash
# Clone the repository
git clone https://github.com/TKpopoola-consulting/AI-DevFactory.git
cd AI-DevFactory

# Set up backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r orchestrator/requirements.txt
pip install -r agents/backend_agent/requirements.txt
pip install -r agents/frontend_agent/requirements.txt
pip install -r agents/infra_agent/requirements.txt
pip install -r agents/qa_agent/requirements.txt

# Set up frontend
cd ../frontend
flutter pub get

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run the system
# Terminal 1: Start orchestrator
cd backend/orchestrator
python main_simple.py

# Terminal 2: Start frontend
cd frontend
flutter run -d chrome
Environment Variables
bash
# .env file
API_URL=http://localhost:8000
WS_URL=ws://localhost:8000
GEMINI_API_KEY=your_gemini_api_key
API Endpoints
Method	Endpoint	Description
GET	/health	Health check
POST	/jobs	Create a new job
GET	/jobs	List all jobs
GET	/jobs/{id}	Get job status
POST	/jobs/{id}/cancel	Cancel job
POST	/jobs/{id}/feedback	Provide feedback
WS	/ws/{id}	WebSocket for real-time updates
What You Can Build
Application Type	Time	Features Generated
E-Commerce Platform	3-4 min	Products, cart, checkout, payments, orders
SaaS Platform	3-4 min	Multi-tenancy, subscriptions, billing
Social Media App	2-3 min	Posts, comments, likes, messaging
Task Management	1-2 min	Projects, tasks, deadlines, comments
CRM System	2-3 min	Contacts, deals, pipelines, reports
Healthcare Portal	3-4 min	Patient records, appointments, compliance
Cost Breakdown
Component	Cost per App
AI Tokens	$0.02 - $0.05
Compute	$0.002
Storage	$0.0001
Total	$0.02 - $0.05
Contributing
We welcome contributions! See CONTRIBUTING.md for details.

Ways to Contribute
Report bugs - Open an issue

Suggest features - Start a discussion

Improve docs - Submit a PR

Add code - New agents, frameworks, or fixes

License
MIT License. See LICENSE for details.

Support
Email: devs@sartorfit.com

GitHub Issues: Create an issue

<div align="center"> <p>Made with ❤️ by TKpopoola Consulting</p> <p>⭐ Star us on GitHub — it motivates us a lot!</p> </div> ```
