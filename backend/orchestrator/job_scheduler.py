import asyncio
from queue import PriorityQueue
from datetime import datetime
from utils.state_manager import JobState

class JobScheduler:
    def __init__(self):
        self.queue = PriorityQueue()
        self.current_jobs = {}
        self.logger = logging.getLogger("job_scheduler")

    def add_job(self, job_id: str, priority: int = 5):
        """Add job to scheduling queue"""
        self.queue.put((priority, datetime.now(), job_id))
        
    async def process_queue(self):
        """Continuously process jobs from queue"""
        while True:
            if not self.queue.empty():
                priority, timestamp, job_id = self.queue.get()
                state = JobState(job_id)
                
                if state.get("status") != "canceled":
                    self.current_jobs[job_id] = asyncio.create_task(
                        self.execute_job(job_id)
                )
            
            await asyncio.sleep(1)
    
    async def execute_job(self, job_id: str):
        """Execute job workflow"""
        state = JobState(job_id)
        try:
            # Retrieve job details
            prompt = state.get("prompt")
            config = state.get("config")
            
            # Execute workflow (would integrate with WorkflowManager)
            # ...
            
            state.set("status", "completed")
        
        except Exception as e:
            state.set("status", "failed")
            state.set("error", str(e))
            self.logger.exception(f"Job {job_id} failed")
    
    def cancel_job(self, job_id: str):
        """Cancel a scheduled or running job"""
        state = JobState(job_id)
        state.set("status", "canceled")
        
        # Cancel running task if exists
        if job_id in self.current_jobs:
            self.current_jobs[job_id].cancel()
            del self.current_jobs[job_id]