"""
Redis cache utilities
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class JobCache:
    """Simple cache for jobs"""
    
    def __init__(self):
        self.cache = {}
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        return self.cache.get(job_id)
    
    def set_job(self, job_id: str, data: Dict):
        self.cache[job_id] = data
