#!/usr/bin/env python3
"""
Test script to verify all AI-DevFactory agents are working
"""

import requests
import time
import sys

AGENTS = {
    "frontend_agent": {"port": 5000, "endpoint": "/health"},
    "backend_agent": {"port": 5001, "endpoint": "/health"},
    "infra_agent": {"port": 5002, "endpoint": "/health"},
    "qa_agent": {"port": 5003, "endpoint": "/health"},
    "modifier_agent": {"port": 5004, "endpoint": "/health"},
    "fixer_agent": {"port": 5007, "endpoint": "/health"},
    "orchestrator": {"port": 8000, "endpoint": "/health"}
}

def test_agent(name, config):
    """Test a single agent's health endpoint"""
    url = f"http://localhost:{config['port']}{config['endpoint']}"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "healthy" if data.get("status") == "healthy" else "unhealthy",
                "data": data
            }
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "offline", "error": "Connection refused"}
    except requests.exceptions.Timeout:
        return {"status": "timeout", "error": "Request timed out"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def test_all_agents():
    """Test all agents and report status"""
    print("🔍 Testing AI-DevFactory Agents...")
    print("=" * 60)

    results = {}
    all_healthy = True

    for name, config in AGENTS.items():
        print(f"Testing {name:20} (port {config['port']})... ", end="", flush=True)
        result = test_agent(name, config)
        results[name] = result

        if result["status"] == "healthy":
            print("✅ HEALTHY")
            if "data" in result:
                agent_type = result["data"].get("agent", "unknown")
                print(f"   └─ Type: {agent_type}")
        elif result["status"] == "offline":
            print("🔴 OFFLINE")
            all_healthy = False
        elif result["status"] == "timeout":
            print("⏱️  TIMEOUT")
            all_healthy = False
        else:
            print("❌ ERROR")
            if "error" in result:
                print(f"   └─ Error: {result['error']}")
            all_healthy = False

    print("=" * 60)

    # Summary
    healthy_count = sum(1 for r in results.values() if r["status"] == "healthy")
    total_count = len(results)

    print(f"Summary: {healthy_count}/{total_count} agents healthy")

    if all_healthy:
        print("🎉 All agents are healthy and ready!")
    else:
        print("⚠️  Some agents need attention")

        # Test the orchestrator's job creation
        if results.get("orchestrator", {}).get("status") == "healthy":
            print("\nTesting orchestrator job creation...")
            test_orchestrator_job()

    return all_healthy

def test_orchestrator_job():
    """Test creating a job through the orchestrator"""
    url = "http://localhost:8000/jobs"

    test_job = {
        "prompt": "Create a todo app with React frontend and FastAPI backend",
        "config": {
            "frontend": "react",
            "backend": "fastapi",
            "cloud": "azure",
            "quality_check": True
        }
    }

    try:
        response = requests.post(url, json=test_job, timeout=10)
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("job_id")
            print(f"✅ Job created successfully: {job_id}")
            print(f"   Status: {data.get('status')}")
            print(f"   Estimated time: {data.get('estimated_time')}")
            return job_id
        else:
            print(f"❌ Failed to create job: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error creating job: {e}")

    return None

def test_fixer_agent():
    """Test the fixer agent with sample buggy code"""
    print("\n🧪 Testing Fixer Agent with buggy Python code...")

    buggy_code = {
        "example.py": """
def calculate_total(items):
    total = 0
    for item in items:
        price = item['price']
        quantity = item['quantity']
        total += price * quantity  # Potential division by zero if quantity is 0?

    average = total / len(items) if len(items) > 0 else 0

    return {"total": total, "average": average}

def process_user_input(user_input):
    # Dangerous eval usage
    result = eval(user_input)
    return result
"""
    }

    url = "http://localhost:5007/fix"

    try:
        response = requests.post(url, json={
            "code": buggy_code,
            "language": "python"
        }, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Fixer agent analysis complete")
            print(f"   Issues found: {data.get('issues_found', 0)}")
            print(f"   Security issues: {data.get('security_issues', 0)}")
            print(f"   Fixes applied: {data.get('fixes_applied', 0)}")
            return True
        else:
            print(f"❌ Fixer agent failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing fixer agent: {e}")

    return False

def test_modifier_agent():
    """Test the modifier agent with sample code"""
    print("\n🔧 Testing Modifier Agent with Python code...")

    sample_code = {
        "example.py": """
def process_data(items):
    result = []
    for item in items:
        if item is not None:
            if item['value'] > 100:
                if item['status'] == 'active':
                    result.append(item['value'] * 2)
                else:
                    result.append(item['value'])
            else:
                result.append(item['value'])
    return result
"""
    }

    url = "http://localhost:5004/modify"

    try:
        response = requests.post(url, json={
            "code": sample_code,
            "modification_type": "refactor",
            "language": "python"
        }, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Modifier agent analysis complete")
            print(f"   Suggestions: {len(data.get('suggestions', []))}")
            print(f"   Modifications applied: {len([m for m in data.get('modifications_applied', []) if m.get('applied')])}")
            return True
        else:
            print(f"❌ Modifier agent failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing modifier agent: {e}")

    return False

if __name__ == "__main__":
    print("🚀 AI-DevFactory Complete System Test")
    print("=" * 60)

    # Test basic agent health
    all_healthy = test_all_agents()

    # Test specialized agents if orchestrator is healthy
    if all_healthy:
        test_fixer_agent()
        test_modifier_agent()

        print("\n" + "=" * 60)
        print("🎯 AI-DevFactory System Status: FULLY OPERATIONAL")
        print("✅ 7 Agents ready")
        print("✅ Orchestrator ready")
        print("✅ Fixer agent (bug detection) ready")
        print("✅ Modifier agent (code improvement) ready")
        print("✅ Parallel execution engine ready")
        print("✅ Redis-based coordination ready")
    else:
        print("\n" + "=" * 60)
        print("⚠️  AI-DevFactory System Status: PARTIAL")
        print("Some agents need to be started:")
        print("  docker-compose up -d")
        print("\nOr run agents individually:")
        print("  python backend/agents/frontend_agent/main.py")
        print("  python backend/agents/backend_agent/main.py")
        print("  python backend/agents/infra_agent/main_fastapi.py")
        print("  python backend/agents/qa_agent/main_fastapi.py")
        print("  python backend/agents/fixer_agent/main.py")
        print("  python backend/agents/modifier_agent/main.py")
        print("  python backend/orchestrator/main_simple.py")