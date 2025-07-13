# ... existing imports ...
from utils.cache import JobCache

class WorkflowManager:
    def __init__(self, db=None, cache=None):
        self.db = db or JobDB()
        self.cache = cache or JobCache()
        # ... rest of initialization ...

    async def initiate_workflow(self, prompt: str, user_id: str, output_config: dict) -> str:
        # ... existing job creation logic ...
        
        # Cache initial job state
        self.cache.set_job(job_id, {
            "status": "created",
            "progress": 0,
            "user_id": user_id
        })
        
        return job_id

    async def execute_workflow(self, job_id: str, prompt: str, config: dict):
        # Get initial state from cache
        job_state = self.cache.get_job(job_id) or {}
        
        try:
            # Update state in cache
            job_state["status"] = "processing"
            job_state["progress"] = 10
            self.cache.set_job(job_id, job_state)
            
            # ... workflow steps ...
            
            # Update progress at each stage
            job_state["progress"] = 50
            self.cache.set_job(job_id, job_state)
            
            # ... more workflow steps ...
            
            # Final update
            job_state["status"] = "completed"
            job_state["progress"] = 100
            self.cache.set_job(job_id, job_state)
            
        except Exception as e:
            job_state["status"] = "failed"
            job_state["error"] = str(e)
            self.cache.set_job(job_id, job_state)
            raise