# backend/orchestrator/human_intervention.py
"""
Human intervention management system
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json

router = APIRouter(prefix="/intervention", tags=["human_intervention"])


class InterventionRequest(BaseModel):
    job_id: str
    reason: str
    current_quality: float
    issues: List[Dict]
    suggestions: List[str]
    created_at: str


@router.get("/pending")
async def get_pending_interventions():
    """Get all jobs waiting for human intervention"""
    from database import JobDB
    db = JobDB()
    pending_jobs = db.get_jobs_by_status("waiting_for_human")
    
    return {
        "count": len(pending_jobs),
        "jobs": pending_jobs
    }


@router.post("/{job_id}/resolve")
async def resolve_intervention(job_id: str, action: str, feedback: Optional[str] = None):
    """
    Resolve human intervention
    
    Args:
        job_id: Job identifier
        action: "continue", "abort", "manual_fix"
        feedback: Human-provided feedback
    """
    from database import JobDB
    from workflow_manager import WorkflowManager
    
    db = JobDB()
    job = db.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.get("status") != "waiting_for_human":
        raise HTTPException(status_code=400, detail="Job not waiting for intervention")
    
    if action == "continue":
        # Continue with feedback
        wm = WorkflowManager()
        await wm.continue_with_feedback(job_id, feedback)
        return {"status": "continued", "job_id": job_id}
    
    elif action == "abort":
        # Abort job
        db.update_job(job_id, {"status": "aborted", "aborted_at": datetime.utcnow()})
        return {"status": "aborted", "job_id": job_id}
    
    elif action == "manual_fix":
        # Mark as manually fixed
        db.update_job(job_id, {
            "status": "manual_fix_applied",
            "manual_feedback": feedback,
            "fixed_at": datetime.utcnow()
        })
        return {"status": "manual_fix_recorded", "job_id": job_id}
    
    raise HTTPException(status_code=400, detail="Invalid action")


@router.get("/{job_id}/details")
async def get_intervention_details(job_id: str):
    """Get detailed information for human intervention"""
    from database import JobDB
    
    db = JobDB()
    job = db.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job_id,
        "original_prompt": job.get("prompt"),
        "quality_history": job.get("quality_history", []),
        "issues_detected": job.get("issues", []),
        "suggested_fixes": job.get("suggestions", []),
        "code_preview": await _get_code_preview(job_id),
        "recommended_action": _recommend_action(job)
    }


async def _get_code_preview(job_id: str) -> Dict:
    """Get code preview for human review"""
    from utils.artifact_integrator import ArtifactIntegrator
    integrator = ArtifactIntegrator()
    
    # Get latest artifacts
    artifacts = await integrator.get_artifacts(job_id)
    
    return {
        "frontend_files": list(artifacts.get("frontend", {}).keys())[:5],
        "backend_files": list(artifacts.get("backend", {}).keys())[:5],
        "total_size_mb": _calculate_size(artifacts)
    }


def _recommend_action(job: Dict) -> str:
    """Recommend action based on job state"""
    quality_history = job.get("quality_history", [])
    
    if len(quality_history) >= 5:
        return "abort"  # Too many attempts
    
    if quality_history and quality_history[-1] < 50:
        return "abort"  # Very low quality
    
    return "continue_with_feedback"
