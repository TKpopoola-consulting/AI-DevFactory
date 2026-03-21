# backend/orchestrator/main.py (Final)
"""
Complete Orchestrator with all production features
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from workflow_manager import WorkflowManager
from models import JobRequest, JobResponse
from utils.security import verify_token, require_role
from utils.error_handler import handle_exceptions
from utils.rate_limiter import DistributedRateLimiter, RateLimitMiddleware
from utils.metrics import MetricsMiddleware, track_job_duration
from utils.tracing import setup_tracing
from utils.health import HealthChecker
from database import JobDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logger.info("Starting Orchestrator...")
    
    # Initialize connections
    app.state.rate_limiter = DistributedRateLimiter()
    app.state.health_checker = HealthChecker()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Orchestrator...")


app = FastAPI(
    title="AI DevFactory Orchestrator",
    description="Central workflow coordinator for AI-generated applications",
    version="2.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)
app.add_middleware(RateLimitMiddleware, limiter=app.state.rate_limiter)
app.add_middleware(MetricsMiddleware)

# Setup OpenTelemetry tracing
tracer = setup_tracing(app, "orchestrator")


# Connection Manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
    
    async def send_progress(self, job_id: str, progress: Dict):
        if job_id in self.active_connections:
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(progress)
                except:
                    pass


manager = ConnectionManager()


@app.post("/jobs", response_model=JobResponse)
@handle_exceptions
@track_job_duration("full_workflow")
async def create_job(
    request: JobRequest,
    req: Request,
    user: dict = Depends(require_role("create-job"))
):
    """Create a new job"""
    wm = WorkflowManager()
    job_id = await wm.initiate_workflow(
        prompt=request.prompt,
        user_id=user.user_id,
        output_config=request.output_config.dict()
    )
    
    # Track metrics
    from utils.metrics import job_requests_total
    job_requests_total.labels(status="created", user_tier=user.get("tier", "free")).inc()
    
    return {"job_id": job_id, "status": "processing"}


@app.get("/jobs/{job_id}", response_model=JobResponse)
@handle_exceptions
async def get_job_status(job_id: str, user: dict = Depends(verify_token)):
    """Get job status"""
    wm = WorkflowManager()
    job = wm.db.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["user_id"] != user.user_id and "admin" not in user.roles:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job.get("progress"),
        "artifacts": job.get("artifacts"),
        "estimated_cost": job.get("estimated_cost")
    }


@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket for real-time updates"""
    await manager.connect(websocket, job_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.startswith("command:cancel"):
                wm = WorkflowManager()
                await wm.cancel_job(job_id)
                await websocket.send_json({"type": "cancelled"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)


@app.get("/jobs/{job_id}/stream")
async def stream_job_logs(job_id: str, user: dict = Depends(verify_token)):
    """Server-sent events for logs"""
    from fastapi.responses import StreamingResponse
    
    async def event_generator():
        db = JobDB()
        last_log_count = 0
        
        while True:
            job = db.get_job(job_id)
            if job:
                logs = job.get("logs", [])
                new_logs = logs[last_log_count:]
                
                for log in new_logs:
                    yield f"data: {json.dumps(log)}\n\n"
                
                last_log_count = len(logs)
                
                if job.get("status") in ["completed", "failed"]:
                    yield f"data: {json.dumps({'type': 'complete', 'status': job['status']})}\n\n"
                    break
            
            await asyncio.sleep(1)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi import Response
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    checker = HealthChecker()
    return await checker.check_all()


@app.get("/health/liveness")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive"}


@app.get("/health/readiness")
async def readiness_check():
    """Kubernetes readiness probe"""
    checker = HealthChecker()
    health = await checker.check_all()
    
    if health["status"] == "healthy":
        return {"status": "ready"}
    raise HTTPException(status_code=503, detail="Not ready")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI DevFactory Orchestrator",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": [
            "/jobs",
            "/jobs/{id}",
            "/ws/{id}",
            "/metrics",
            "/health"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
