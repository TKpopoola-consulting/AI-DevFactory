from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import os
import json

app = FastAPI(title="Frontend Agent", version="1.0.0")

# Try to import the generator, but provide fallback if it fails
try:
    from gemini_handler import FrontendGenerator
    generator = FrontendGenerator()
    GENERATOR_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Warning: FrontendGenerator not available: {e}")
    print("⚠️  Using mock generator for testing")
    GENERATOR_AVAILABLE = False
    generator = None

# Request models
class GenerationRequest(BaseModel):
    prompt: str
    framework: str = "react"
    requirements: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None

class GenerationResponse(BaseModel):
    status: str
    generated_code: Dict[str, Any]
    framework: str
    validation_results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "frontend", "generator_available": GENERATOR_AVAILABLE}

@app.post("/generate", response_model=GenerationResponse)
async def generate(request: GenerationRequest):
    """Generate frontend code based on prompt and framework"""
    try:
        if not GENERATOR_AVAILABLE:
            # Return mock response for testing
            mock_result = create_mock_frontend(request.prompt, request.framework)
            validation_result = validate_generated_code(mock_result, request.framework)

            return GenerationResponse(
                status="success",
                generated_code=mock_result,
                framework=request.framework,
                validation_results=validation_result
            )

        # Generate code using the Gemini handler
        result = generator.generate_frontend(
            prompt=request.prompt,
            framework=request.framework,
            requirements=request.requirements or {}
        )

        # Validate the generated code
        validation_result = validate_generated_code(result, request.framework)

        return GenerationResponse(
            status="success",
            generated_code=result,
            framework=request.framework,
            validation_results=validation_result
        )

    except Exception as e:
        return GenerationResponse(
            status="error",
            generated_code={},
            framework=request.framework,
            error=str(e)
        )

def create_mock_frontend(prompt: str, framework: str) -> Dict[str, Any]:
    """Create mock frontend code for testing when Gemini is not available"""
    components = []

    if "login" in prompt.lower():
        components = [
            {
                "name": "LoginForm",
                "code": f"""
// {framework} Login Component
import React, {{ useState }} from 'react';
import './LoginForm.css';

const LoginForm = () => {{
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {{
    e.preventDefault();
    console.log('Logging in with:', {{ email, password }});
  }};

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={{handleSubmit}}>
        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            value={{email}}
            onChange={{(e) => setEmail(e.target.value)}}
            placeholder="Enter your email"
          />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            value={{password}}
            onChange={{(e) => setPassword(e.target.value)}}
            placeholder="Enter your password"
          />
        </div>
        <button type="submit">Login</button>
      </form>
    </div>
  );
}};

export default LoginForm;
"""
            }
        ]
    elif "dashboard" in prompt.lower():
        components = [
            {
                "name": "Dashboard",
                "code": f"""
// {framework} Dashboard Component
import React from 'react';
import './Dashboard.css';

const Dashboard = () => {{
  const stats = [
    {{ label: 'Users', value: '1,234' }},
    {{ label: 'Revenue', value: '$45,678' }},
    {{ label: 'Orders', value: '567' }},
    {{ label: 'Growth', value: '+12.5%' }}
  ];

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <div className="stats-grid">
        {{stats.map((stat, index) => (
          <div key={{index}} className="stat-card">
            <h3>{{stat.value}}</h3>
            <p>{{stat.label}}</p>
          </div>
        ))}}
      </div>
    </div>
  );
}};

export default Dashboard;
"""
            }
        ]
    else:
        components = [
            {
                "name": "App",
                "code": f"""
// {framework} App Component
import React from 'react';
import './App.css';

const App = () => {{
  return (
    <div className="App">
      <h1>Welcome to My App</h1>
      <p>Generated from prompt: "{prompt}"</p>
    </div>
  );
}};

export default App;
"""
            }
        ]

    return {
        "components": components,
        "styling": {
            "css": """
/* Generated CSS */
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  background-color: #007bff;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}

.dashboard {
  padding: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.stat-card {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: center;
}

.stat-card h3 {
  margin: 0;
  font-size: 24px;
  color: #007bff;
}

.stat-card p {
  margin: 5px 0 0;
  color: #666;
}
"""
        },
        "routing": {
            "routes": [
                {"path": "/", "component": "App"},
                {"path": "/login", "component": "LoginForm"},
                {"path": "/dashboard", "component": "Dashboard"}
            ]
        },
        "state_management": {
            "store": """
// Redux store configuration
import {{ createStore }} from 'redux';

const initialState = {{
  user: null,
  loading: false,
  error: null
}};

function rootReducer(state = initialState, action) {{
  switch (action.type) {{
    case 'LOGIN_REQUEST':
      return {{ ...state, loading: true, error: null }};
    case 'LOGIN_SUCCESS':
      return {{ ...state, loading: false, user: action.payload }};
    case 'LOGIN_FAILURE':
      return {{ ...state, loading: false, error: action.payload }};
    default:
      return state;
  }}
}}

const store = createStore(rootReducer);
export default store;
"""
        }
    }

def validate_generated_code(code: Dict[str, Any], framework: str) -> Dict[str, Any]:
    """Validate generated frontend code"""
    validation_result = {
        "has_components": len(code.get("components", [])) > 0,
        "has_styling": bool(code.get("styling")),
        "has_routing": bool(code.get("routing")),
        "has_state_management": bool(code.get("state_management")),
        "errors": []
    }

    # Framework-specific validation
    if framework == "react":
        if not any("useState" in str(comp.get("code", "")) for comp in code.get("components", [])):
            validation_result["errors"].append("Missing React state hooks")

    elif framework == "flutter":
        if not any("StatefulWidget" in str(comp.get("code", "")) for comp in code.get("components", [])):
            validation_result["errors"].append("Missing StatefulWidget")

    elif framework == "vue":
        if not any("ref(" in str(comp.get("code", "")) for comp in code.get("components", [])):
            validation_result["errors"].append("Missing Vue 3 Composition API")

    validation_result["is_valid"] = len(validation_result["errors"]) == 0

    return validation_result

@app.post("/test")
async def test_generation():
    """Test endpoint to verify agent is working"""
    test_prompt = "Create a login page with email and password fields"

    try:
        if GENERATOR_AVAILABLE:
            result = generator.generate_frontend(test_prompt, "react")
        else:
            result = create_mock_frontend(test_prompt, "react")

        return {
            "status": "success",
            "test": "passed",
            "components_generated": len(result.get("components", [])),
            "has_styling": bool(result.get("styling")),
            "generator_used": "real" if GENERATOR_AVAILABLE else "mock"
        }
    except Exception as e:
        return {
            "status": "error",
            "test": "failed",
            "error": str(e)
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Starting Frontend Agent on port {port}")
    print(f"📍 Endpoint: http://localhost:{port}/generate")
    print(f"📚 Docs: http://localhost:{port}/docs")
    print(f"⚡ Generator available: {GENERATOR_AVAILABLE}")

    uvicorn.run(app, host="0.0.0.0", port=port)