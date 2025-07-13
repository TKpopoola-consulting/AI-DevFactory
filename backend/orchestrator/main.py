from fastapi import FastAPI, HTTPException, Depends
from workflow_manager import WorkflowManager
from models import JobRequest, JobResponse
from utils.security import verify_token, require_role
from utils.error_handler import handle_exceptions

app = FastAPI(
    title="AI DevFactory Orchestrator",
    description="Central workflow coordinator for AI-generated applications",
    version="1.0.0"
)

@app.post("/jobs", response_model=JobResponse)
@handle_exceptions
async def create_job(
    request: JobRequest,
    user: dict = Depends(require_role("create-job"))
):
    manager = WorkflowManager()
    job_id = await manager.initiate_workflow(
        prompt=request.prompt,
        user_id=user.user_id,
        output_config=request.output_config
    )
    return {"job_id": job_id, "status": "processing"}

@app.get("/jobs/{job_id}", response_model=JobResponse)
@handle_exceptions
async def get_job_status(
    job_id: str,
    user: dict = Depends(verify_token)
):
    manager = WorkflowManager()
    job = manager.db.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check ownership
    if job["user_id"] != user.user_id and "admin" not in user.roles:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job.get("progress"),
        "artifacts": job.get("artifacts"),
        "estimated_cost": job.get("estimated_cost")
    }

# ... other endpoints ...