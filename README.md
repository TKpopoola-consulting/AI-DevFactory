📌 README.md — AI DevFactory: Continuous AI Coding System
🚀 AI DevFactory
AI DevFactory is an open-source, AI-driven continuous coding system that turns natural language requirements into production-ready code — iteratively, collaboratively, and flexibly.
It lets you build or modify software products using AI agents, Visual Studio Code workspaces, and your own cloud storage or GitHub.

🎯 Key Goals
✅ Automate code generation with AI
✅ Support any programming language or framework
✅ Keep humans in control with feedback loops
✅ Store code securely — on GitHub or Azure Blob Storage
✅ Scale to advanced uses like game engine coding
✅ Enable a collaborative, extensible community

⚙️ How It Works
less
Copy
Edit
graph TD
  A[User] -->|Prompt + Requirements| B[Flutter Web UI]
  B --> C[Orchestrator API]
  C --> D[AI Agent + VS Code Server]
  D --> E[Workspace Storage (Azure Blob)]
  E -->|Checkpoints| D
  D -->|Intermediate Results| B
  B -->|Feedback| D
  B -->|Finalize| F[Output Gateway]
  F -->|Push to GitHub| G[GitHub Repo]
  F -->|Save to Azure Blob| H[Blob Storage]
  F -->|Download ZIP| I[ZIP Archive]
1️⃣ Submit Prompt
Describe what you want (e.g., “Build a Flask API with JWT auth”).
Add requirements using the Requirement Viewer.

2️⃣ AI Generates Code
A selected AI agent (Azure AI or your private model) writes code inside an isolated VS Code workspace.

3️⃣ Live Iteration
You review intermediate results, check logs, and give feedback — the AI updates code until you approve.

4️⃣ Final Output
When you’re ready, export:

Push to your GitHub repo as a PR

Save to Azure Blob Storage

Or Download as a ZIP file

🧩 Tech Stack
Frontend:

Flutter Web App

Prompt input

Requirement Viewer

Model Selector (choose AI)

Monitoring & Logging Panel

Output Destination Selector

Backend:

Custom Orchestrator API (Python FastAPI or Node.js NestJS)

VS Code Server (e.g., code-server) for live workspaces

AI Agents (OpenAI, Azure AI, or private ONNX models)

Azure Blob Storage for persistent workspaces

GitHub for final delivery

📂 Repo Structure
bash
Copy
Edit
/frontend/   # Flutter Web App
/backend/    # Orchestrator, VS Code server config, AI runners
/infra/      # Deployment scripts, Dockerfiles, ARM templates
/docs/       # Architecture, workflows, API docs
/.github/    # Issues, PR templates, workflows
✨ Key Features
✅ Natural Language → Code

✅ Multi-agent: OpenAI, Azure AI, or self-hosted

✅ Visual Studio Code integration — real file editing

✅ Requirements Viewer — track project scope

✅ Monitoring & Logging — watch every step

✅ Checkpointing — safe version history

✅ Export anywhere — GitHub PR, Azure Blob, or ZIP

💪 Why Open Source?
We believe coding with AI should be transparent and community-driven.
Everyone can:

Add new AI agents

Improve the orchestrator

Contribute connectors for new game engines or frameworks

Help test, debug, and secure the system

🤝 How to Contribute
🍴 Fork this repo

🗂️ Check the open issues

✍️ Submit a pull request

🗨️ Join discussions to shape features

✅ Follow CONTRIBUTING.md for coding standards

🚧 Roadmap
 GPU-based agents for 3D game engine coding

 Real-time pair programming with VS Code Live Share

 Plugin marketplace for new AI tools

 Built-in doc generator for every code output

📜 License
Open-source under the MIT License.

📬 Contact
Questions? Ideas?
Open an issue or email devs@sartorfit.com.

Let’s build the future of coding — together!



