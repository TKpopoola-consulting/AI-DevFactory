# backend/orchestrator/utils/metrics.py
"""
Prometheus metrics for monitoring
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
from functools import wraps
import asyncio

# Define metrics
job_requests_total = Counter(
    'orchestrator_jobs_total',
    'Total number of job requests',
    ['status', 'user_tier']
)

job_duration_seconds = Histogram(
    'orchestrator_job_duration_seconds',
    'Job execution duration',
    ['job_type'],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600]
)

agent_calls_total = Counter(
    'orchestrator_agent_calls_total',
    'Total agent calls',
    ['agent_type', 'status']
)

agent_call_duration = Histogram(
    'orchestrator_agent_call_duration_seconds',
    'Agent call duration',
    ['agent_type'],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60]
)

active_jobs = Gauge(
    'orchestrator_active_jobs',
    'Number of currently active jobs'
)

queue_size = Gauge(
    'orchestrator_queue_size',
    'Current job queue size'
)

api_requests_total = Counter(
    'orchestrator_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'orchestrator_api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5]
)

cost_total = Counter(
    'orchestrator_cost_total',
    'Total cost incurred',
    ['cost_type']
)

error_total = Counter(
    'orchestrator_errors_total',
    'Total errors',
    ['error_type', 'component']
)


class MetricsMiddleware:
    """Middleware to record API metrics"""
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        api_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        api_request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response


def track_job_duration(job_type: str):
    """Decorator to track job duration"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                job_duration_seconds.labels(job_type=job_type).observe(duration)
        return wrapper
    return decorator


def track_agent_call(agent_type: str):
    """Decorator to track agent calls"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                agent_calls_total.labels(agent_type=agent_type, status="success").inc()
                return result
            except Exception as e:
                agent_calls_total.labels(agent_type=agent_type, status="failed").inc()
                error_total.labels(error_type=type(e).__name__, component=agent_type).inc()
                raise
            finally:
                duration = time.time() - start_time
                agent_call_duration.labels(agent_type=agent_type).observe(duration)
        return wrapper
    return decorator


# Add to main.py
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
