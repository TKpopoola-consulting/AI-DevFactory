from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
import os
import json

app = FastAPI(title="Backend Agent", version="1.0.0")

# Try to import the generator, but provide fallback if it fails
try:
    # This would normally import from agent_logic
    # For now, we'll create a mock generator
    GENERATOR_AVAILABLE = False
except Exception as e:
    print(f"⚠️  Warning: BackendGenerator not available: {e}")
    print("⚠️  Using mock generator for testing")
    GENERATOR_AVAILABLE = False

# Request models
class GenerationRequest(BaseModel):
    prompt: str
    framework: str = "fastapi"
    requirements: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None

class ValidationRequest(BaseModel):
    project_structure: Dict[str, Any]
    framework: str

class GenerationResponse(BaseModel):
    status: str
    generated_code: Dict[str, Any]
    framework: str
    endpoints: List[Dict[str, Any]]
    database_schema: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ValidationResponse(BaseModel):
    status: str
    is_valid: bool
    issues: List[str]
    suggestions: List[str]

@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "backend", "generator_available": GENERATOR_AVAILABLE}

@app.post("/generate", response_model=GenerationResponse)
async def generate(request: GenerationRequest):
    """Generate backend code based on prompt and framework"""
    try:
        # Generate mock backend code
        result = create_mock_backend(request.prompt, request.framework)

        return GenerationResponse(
            status="success",
            generated_code=result["code"],
            framework=request.framework,
            endpoints=result["endpoints"],
            database_schema=result.get("database_schema")
        )

    except Exception as e:
        return GenerationResponse(
            status="error",
            generated_code={},
            framework=request.framework,
            endpoints=[],
            error=str(e)
        )

@app.post("/validate", response_model=ValidationResponse)
async def validate(request: ValidationRequest):
    """Validate backend project structure"""
    try:
        issues = []
        suggestions = []

        # Basic validation
        if not request.project_structure.get("endpoints"):
            issues.append("No API endpoints defined")
            suggestions.append("Add at least one REST endpoint")

        if not request.project_structure.get("models"):
            issues.append("No data models defined")
            suggestions.append("Define data models for your entities")

        # Framework-specific validation
        if request.framework == "fastapi":
            if not any("FastAPI" in str(item) for item in request.project_structure.values()):
                issues.append("Missing FastAPI application setup")
                suggestions.append("Add FastAPI app initialization")

        elif request.framework == "express":
            if not any("express()" in str(item) for item in request.project_structure.values()):
                issues.append("Missing Express app setup")
                suggestions.append("Add Express app initialization")

        elif request.framework == "django":
            if not any("Django" in str(item) for item in request.project_structure.values()):
                issues.append("Missing Django project structure")
                suggestions.append("Ensure Django settings and URLs are configured")

        is_valid = len(issues) == 0

        return ValidationResponse(
            status="success",
            is_valid=is_valid,
            issues=issues,
            suggestions=suggestions
        )

    except Exception as e:
        return ValidationResponse(
            status="error",
            is_valid=False,
            issues=[f"Validation error: {str(e)}"],
            suggestions=["Check the project structure format"]
        )

def create_mock_backend(prompt: str, framework: str) -> Dict[str, Any]:
    """Create mock backend code based on prompt and framework"""
    prompt_lower = prompt.lower()

    # Determine what type of backend is needed
    if any(keyword in prompt_lower for keyword in ["api", "rest", "endpoint"]):
        endpoints = create_api_endpoints(prompt_lower, framework)
        code = create_api_code(framework, endpoints)
    elif any(keyword in prompt_lower for keyword in ["auth", "login", "user"]):
        endpoints = create_auth_endpoints(framework)
        code = create_auth_code(framework)
    elif any(keyword in prompt_lower for keyword in ["database", "crud", "model"]):
        endpoints = create_crud_endpoints(prompt_lower, framework)
        code = create_crud_code(framework, endpoints)
    else:
        endpoints = create_default_endpoints(framework)
        code = create_default_code(framework)

    return {
        "code": code,
        "endpoints": endpoints,
        "database_schema": create_database_schema(prompt_lower)
    }

def create_api_endpoints(prompt: str, framework: str) -> List[Dict[str, Any]]:
    """Create API endpoints based on prompt"""
    endpoints = []

    if "todo" in prompt:
        endpoints = [
            {
                "method": "GET",
                "path": "/api/todos",
                "description": "Get all todo items",
                "response_type": "List[Todo]"
            },
            {
                "method": "POST",
                "path": "/api/todos",
                "description": "Create a new todo item",
                "request_body": "TodoCreate",
                "response_type": "Todo"
            },
            {
                "method": "GET",
                "path": "/api/todos/{id}",
                "description": "Get a specific todo item",
                "response_type": "Todo"
            },
            {
                "method": "PUT",
                "path": "/api/todos/{id}",
                "description": "Update a todo item",
                "request_body": "TodoUpdate",
                "response_type": "Todo"
            },
            {
                "method": "DELETE",
                "path": "/api/todos/{id}",
                "description": "Delete a todo item",
                "response_type": "None"
            }
        ]
    elif "user" in prompt:
        endpoints = [
            {
                "method": "GET",
                "path": "/api/users",
                "description": "Get all users",
                "response_type": "List[User]"
            },
            {
                "method": "POST",
                "path": "/api/users",
                "description": "Create a new user",
                "request_body": "UserCreate",
                "response_type": "User"
            },
            {
                "method": "GET",
                "path": "/api/users/{id}",
                "description": "Get a specific user",
                "response_type": "User"
            }
        ]
    else:
        endpoints = [
            {
                "method": "GET",
                "path": "/api/health",
                "description": "Health check endpoint",
                "response_type": "Dict"
            },
            {
                "method": "GET",
                "path": "/api/data",
                "description": "Get sample data",
                "response_type": "List[Dict]"
            }
        ]

    return endpoints

def create_auth_endpoints(framework: str) -> List[Dict[str, Any]]:
    """Create authentication endpoints"""
    return [
        {
            "method": "POST",
            "path": "/api/auth/register",
            "description": "Register a new user",
            "request_body": "UserRegister",
            "response_type": "AuthResponse"
        },
        {
            "method": "POST",
            "path": "/api/auth/login",
            "description": "Login user",
            "request_body": "UserLogin",
            "response_type": "AuthResponse"
        },
        {
            "method": "POST",
            "path": "/api/auth/logout",
            "description": "Logout user",
            "response_type": "Dict"
        },
        {
            "method": "GET",
            "path": "/api/auth/me",
            "description": "Get current user info",
            "response_type": "User"
        }
    ]

def create_crud_endpoints(prompt: str, framework: str) -> List[Dict[str, Any]]:
    """Create CRUD endpoints"""
    entity = "item"

    if "product" in prompt:
        entity = "product"
    elif "order" in prompt:
        entity = "order"
    elif "post" in prompt:
        entity = "post"

    return [
        {
            "method": "GET",
            "path": f"/api/{entity}s",
            "description": f"Get all {entity}s",
            "response_type": f"List[{entity.capitalize()}]"
        },
        {
            "method": "POST",
            "path": f"/api/{entity}s",
            "description": f"Create a new {entity}",
            "request_body": f"{entity.capitalize()}Create",
            "response_type": f"{entity.capitalize()}"
        },
        {
            "method": "GET",
            "path": f"/api/{entity}s/{{id}}",
            "description": f"Get a specific {entity}",
            "response_type": f"{entity.capitalize()}"
        },
        {
            "method": "PUT",
            "path": f"/api/{entity}s/{{id}}",
            "description": f"Update a {entity}",
            "request_body": f"{entity.capitalize()}Update",
            "response_type": f"{entity.capitalize()}"
        },
        {
            "method": "DELETE",
            "path": f"/api/{entity}s/{{id}}",
            "description": f"Delete a {entity}",
            "response_type": "None"
        }
    ]

def create_default_endpoints(framework: str) -> List[Dict[str, Any]]:
    """Create default endpoints"""
    return [
        {
            "method": "GET",
            "path": "/",
            "description": "Root endpoint",
            "response_type": "Dict"
        },
        {
            "method": "GET",
            "path": "/api/health",
            "description": "Health check",
            "response_type": "Dict"
        }
    ]

def create_api_code(framework: str, endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create API code based on framework"""
    if framework == "fastapi":
        return create_fastapi_code(endpoints)
    elif framework == "express":
        return create_express_code(endpoints)
    elif framework == "django":
        return create_django_code(endpoints)
    else:
        return create_fastapi_code(endpoints)  # Default to FastAPI

def create_fastapi_code(endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create FastAPI code"""
    main_code = """
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Backend API", version="1.0.0")

# Data Models
class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# In-memory database
todos = []
next_id = 1

@app.get("/")
async def root():
    return {"message": "Welcome to the API", "docs": "/docs"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "backend-api"}
"""

    # Add endpoint code
    endpoint_code = ""
    for endpoint in endpoints:
        if endpoint["path"] == "/api/todos":
            if endpoint["method"] == "GET":
                endpoint_code += """
@app.get("/api/todos")
async def get_todos():
    return todos
"""
            elif endpoint["method"] == "POST":
                endpoint_code += """
@app.post("/api/todos")
async def create_todo(todo: TodoCreate):
    global next_id
    new_todo = Todo(
        id=next_id,
        title=todo.title,
        description=todo.description
    )
    todos.append(new_todo)
    next_id += 1
    return new_todo
"""

    main_code += endpoint_code
    main_code += """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

    return {
        "main.py": main_code,
        "requirements.txt": "fastapi==0.104.1\nuvicorn[standard]==0.24.0\npydantic==2.5.0",
        "models.py": """
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
"""
    }

def create_express_code(endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create Express.js code"""
    return {
        "index.js": """
const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

// Sample data
let todos = [];
let nextId = 1;

// Root endpoint
app.get('/', (req, res) => {
    res.json({ message: 'Welcome to Express API', docs: 'See /api endpoints' });
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'healthy', service: 'express-api' });
});

// TODO endpoints
app.get('/api/todos', (req, res) => {
    res.json(todos);
});

app.post('/api/todos', (req, res) => {
    const { title, description } = req.body;
    const newTodo = {
        id: nextId++,
        title,
        description: description || '',
        completed: false
    };
    todos.push(newTodo);
    res.status(201).json(newTodo);
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
""",
        "package.json": """
{
  "name": "express-backend",
  "version": "1.0.0",
  "description": "Express.js backend API",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
"""
    }

def create_django_code(endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create Django code"""
    return {
        "manage.py": """#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)
""",
        "backend/settings.py": """
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
"""
    }

def create_default_code(framework: str) -> Dict[str, Any]:
    """Create default backend code"""
    return {
        "main.py": f"""
# {framework.upper()} Backend Application
# Generated from AI-DevFactory Backend Agent

import os
from typing import Optional

print("Starting {framework} backend application...")
print("This is a generated backend application.")
print("Replace this with your actual implementation.")
""",
        "README.md": f"""
# {framework.upper()} Backend

This backend was generated by AI-DevFactory Backend Agent.

## Setup
1. Install dependencies
2. Configure environment variables
3. Run the application

## Endpoints
- GET / - Health check
- GET /api/health - Service health
"""
    }

def create_database_schema(prompt: str) -> Optional[Dict[str, Any]]:
    """Create database schema based on prompt"""
    if any(keyword in prompt for keyword in ["todo", "task", "item"]):
        return {
            "tables": [
                {
                    "name": "todos",
                    "columns": [
                        {"name": "id", "type": "INTEGER", "primary_key": True},
                        {"name": "title", "type": "VARCHAR(255)", "nullable": False},
                        {"name": "description", "type": "TEXT", "nullable": True},
                        {"name": "completed", "type": "BOOLEAN", "default": "false"},
                        {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
                    ]
                }
            ]
        }
    elif any(keyword in prompt for keyword in ["user", "auth"]):
        return {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "INTEGER", "primary_key": True},
                        {"name": "username", "type": "VARCHAR(100)", "unique": True},
                        {"name": "email", "type": "VARCHAR(255)", "unique": True},
                        {"name": "password_hash", "type": "VARCHAR(255)"},
                        {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
                    ]
                }
            ]
        }

    return None

@app.post("/test")
async def test_generation():
    """Test endpoint to verify agent is working"""
    test_prompt = "Create a todo API with CRUD operations"

    try:
        result = create_mock_backend(test_prompt, "fastapi")

        return {
            "status": "success",
            "test": "passed",
            "endpoints_generated": len(result["endpoints"]),
            "has_database_schema": bool(result.get("database_schema")),
            "generator_used": "mock"  # Will be "real" when generator is available
        }
    except Exception as e:
        return {
            "status": "error",
            "test": "failed",
            "error": str(e)
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"🚀 Starting Backend Agent on port {port}")
    print(f"📍 Endpoint: http://localhost:{port}/generate")
    print(f"📚 Docs: http://localhost:{port}/docs")
    print(f"⚡ Generator available: {GENERATOR_AVAILABLE}")

    uvicorn.run(app, host="0.0.0.0", port=port)