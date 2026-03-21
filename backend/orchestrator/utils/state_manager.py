"""
State management with checkpoint system
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manage checkpoints for job recovery"""
    
    def __init__(self):
        self.checkpoints = {}
    
    async def create_checkpoint(self, job_id: str, stage: str, artifacts: Dict) -> str:
        """Create a checkpoint"""
        checkpoint_id = f"{job_id}_{stage}_{int(datetime.now().timestamp())}"
        self.checkpoints[checkpoint_id] = {
            "job_id": job_id,
            "stage": stage,
            "artifacts": artifacts,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"Checkpoint created: {checkpoint_id}")
        return checkpoint_id
    
    async def restore_checkpoint(self, job_id: str, checkpoint_id: str) -> Optional[Dict]:
        """Restore from a checkpoint"""
        return self.checkpoints.get(checkpoint_id)
    
    async def restore_last_checkpoint(self, job_id: str) -> Optional[Dict]:
        """Restore the last checkpoint for a job"""
        job_checkpoints = {k: v for k, v in self.checkpoints.items() if v.get("job_id") == job_id}
        if job_checkpoints:
            last = max(job_checkpoints.keys(), key=lambda x: job_checkpoints[x]["timestamp"])
            return job_checkpoints[last]
        return None
