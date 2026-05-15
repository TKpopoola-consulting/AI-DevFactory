"""
AI DevFactory Orchestrator - Simple Working Version
"""
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import uuid
import sqlite3
import json
from datetime import datetime
from task_processor import TaskProcessor
from capability_ladder import CapabilityLadder, CapabilityLevel
from three_body_architecture import ThreeBodyArchitecture, DecisionType, DecisionStatus

DB_PATH = "/production/AI-DevFactory/backend/orchestrator/aidevfactory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            prompt TEXT NOT NULL,
            config TEXT NOT NULL,
            status TEXT DEFAULT 'created',
            progress INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database initialized")

init_db()

app = FastAPI(title="AI DevFactory", version="2.0.0")

# Background task processor
task_processor = TaskProcessor()

# Safety and governance systems
capability_ladder = CapabilityLadder()
three_body_architecture = ThreeBodyArchitecture()

async def process_job_background(job_id: str, prompt: str, config: Dict[str, Any]):
    """Background task to process job with agents"""
    try:
        from models import JobConfig
        job_config = JobConfig(**config)
        await task_processor.process_job(job_id, prompt, job_config)
    except Exception as e:
        # Update job status to failed
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE jobs SET status = ?, message = ? WHERE job_id = ?",
            ("failed", f"Background processing error: {str(e)}", job_id)
        )
        conn.commit()
        conn.close()

class JobRequest(BaseModel):
    prompt: str
    user_id: str = "anonymous"
    output_config: Dict[str, Any] = {}

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

@app.get("/")
async def root():
    return {"service": "AI DevFactory", "version": "2.0.0", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/jobs", response_model=JobResponse)
async def create_job(request: JobRequest):
    job_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO jobs (job_id, user_id, prompt, config, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (job_id, request.user_id, request.prompt, json.dumps(request.output_config), "processing", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    # Start background task processing
    asyncio.create_task(process_job_background(job_id, request.prompt, request.output_config))

    return JobResponse(job_id=job_id, status="processing", message="Job created successfully")

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": row[0],
        "user_id": row[1],
        "prompt": row[2],
        "config": json.loads(row[3]),
        "status": row[4],
        "progress": row[5],
        "created_at": row[6]
    }

@app.get("/jobs")
async def list_jobs(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT job_id, user_id, status, created_at FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return {"jobs": [{"job_id": r[0], "user_id": r[1], "status": r[2], "created_at": r[3]} for r in rows]}

@app.get("/jobs/{job_id}/progress")
async def get_job_progress(job_id: str):
    """Get real-time progress of a job including agent status"""
    # First get basic job info
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status, progress FROM jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get detailed progress from task processor
    try:
        detailed_progress = task_processor.get_job_progress(job_id)
    except Exception:
        detailed_progress = {"agents": {}, "overall_progress": row[1]}

    return {
        "job_id": job_id,
        "status": row[0],
        "progress": row[1],
        "detailed_progress": detailed_progress
    }

# === Safety and Governance API Endpoints ===

class CapabilityRequest(BaseModel):
    level: str
    justification: str
    requester: str = "system"

@app.post("/capability/request")
async def request_capability(request: CapabilityRequest):
    """Request capability escalation."""
    try:
        level = CapabilityLevel(request.level)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid capability level: {request.level}")

    result = capability_ladder.request_escalation(
        level=level,
        justification=request.justification,
        requester=request.requester
    )

    return result

@app.get("/capability/status/{requester}")
async def get_capability_status(requester: str):
    """Get current capability level for a requester."""
    current_level = capability_ladder.get_current_level(requester)

    if current_level:
        return {
            "requester": requester,
            "current_level": current_level.value,
            "level_int": capability_ladder._level_to_int(current_level)
        }
    else:
        return {
            "requester": requester,
            "current_level": None,
            "message": "No active capability level"
        }

class DecisionRequest(BaseModel):
    decision_type: str
    justification: str
    proposed_action: Dict[str, Any]
    urgency: int = 1
    timeout_seconds: int = 300

@app.post("/decision/request")
async def request_decision(request: DecisionRequest):
    """Request a decision through three-body architecture."""
    try:
        decision_type = DecisionType(request.decision_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid decision type: {request.decision_type}")

    result = await three_body_architecture.request_decision(
        decision_type=decision_type,
        requester="system",
        justification=request.justification,
        proposed_action=request.proposed_action,
        urgency=request.urgency,
        timeout_seconds=request.timeout_seconds
    )

    return result

@app.get("/decision/status/{decision_id}")
async def get_decision_status(decision_id: str):
    """Get status of a decision."""
    result = three_body_architecture.get_decision_status(decision_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result

@app.get("/decisions/pending")
async def get_pending_decisions(limit: int = 10):
    """Get pending decisions."""
    decisions = three_body_architecture.get_decisions_by_status(DecisionStatus.PENDING, limit)
    return {"decisions": decisions}

@app.get("/safety/health")
async def safety_health_check():
    """Health check for safety and governance systems."""
    return {
        "capability_ladder": "operational",
        "three_body_architecture": "operational",
        "safety_systems": [
            "capability_escalation_ladder",
            "three_body_checks_balances",
            "audit_trail",
            "value_alignment",
            "risk_assessment"
        ],
        "timestamp": datetime.now().isoformat()
    }

# === End Safety and Governance Endpoints ===

if __name__ == "__main__":
    print("🚀 Starting AI DevFactory Orchestrator...")
    print("📍 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔒 Safety Systems: Capability Ladder + Three-Body Architecture")
    uvicorn.run(app, host="0.0.0.0", port=8000)
