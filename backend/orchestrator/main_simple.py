"""
AI DevFactory Orchestrator - Simple Working Version
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import uuid
import sqlite3
import json
from datetime import datetime

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

if __name__ == "__main__":
    print("🚀 Starting AI DevFactory Orchestrator...")
    print("📍 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
