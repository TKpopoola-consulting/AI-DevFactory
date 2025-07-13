import json
import redis
from redis.exceptions import RedisError
from .error_handler import log_error

class JobCache:
    def __init__(self, host='redis', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db)
        self.ttl = 300  # 5 minutes cache expiration

    def get_job(self, job_id: str) -> dict:
        try:
            cached = self.redis.get(f"job:{job_id}")
            return json.loads(cached) if cached else None
        except RedisError as e:
            log_error(f"Cache error: {str(e)}")
            return None

    def set_job(self, job_id: str, data: dict):
        try:
            self.redis.setex(
                f"job:{job_id}",
                self.ttl,
                json.dumps(data)
            )
        except RedisError as e:
            log_error(f"Cache set error: {str(e)}")