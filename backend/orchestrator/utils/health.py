# backend/orchestrator/utils/health.py
"""
Enhanced health check with dependency status
"""
from typing import Dict, Any
import asyncio
import redis
import psycopg2
from azure.storage.blob import BlobServiceClient


class HealthChecker:
    """Health checker for all dependencies"""
    
    async def check_all(self) -> Dict[str, Any]:
        """Check all dependencies"""
        checks = await asyncio.gather(
            self.check_redis(),
            self.check_database(),
            self.check_blob_storage(),
            self.check_agent_services(),
            return_exceptions=True
        )
        
        redis_status, db_status, blob_status, agents_status = checks
        
        return {
            "status": "healthy" if all([
                redis_status.get("status") == "healthy",
                db_status.get("status") == "healthy"
            ]) else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "redis": redis_status,
                "database": db_status,
                "blob_storage": blob_status,
                "agents": agents_status
            }
        }
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                socket_connect_timeout=5
            )
            client.ping()
            return {"status": "healthy", "latency_ms": 0}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", 5432),
                database=os.getenv("DB_NAME", "aidevfactory"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", ""),
                connect_timeout=5
            )
            conn.close()
            return {"status": "healthy", "latency_ms": 0}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def check_blob_storage(self) -> Dict[str, Any]:
        """Check Azure Blob Storage connectivity"""
        try:
            client = BlobServiceClient.from_connection_string(
                os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
            )
            # List containers (just to test connectivity)
            list(client.list_containers(max_results=1))
            return {"status": "healthy", "latency_ms": 0}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def check_agent_services(self) -> Dict[str, Any]:
        """Check agent service health"""
        agents = ["frontend", "backend", "infra", "qa"]
        agent_status = {}
        
        for agent in agents:
            agent_status[agent] = await self._check_agent_health(agent)
        
        return agent_status
    
    async def _check_agent_health(self, agent: str) -> Dict[str, Any]:
        """Check individual agent health"""
        import httpx
        
        service_url = os.getenv(f"{agent.upper()}_AGENT_URL", f"http://{agent}-agent:5000")
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{service_url}/health")
                if response.status_code == 200:
                    return {"status": "healthy", "url": service_url}
                return {"status": "degraded", "url": service_url, "code": response.status_code}
        except Exception as e:
            return {"status": "unhealthy", "url": service_url, "error": str(e)}


# Add to main.py
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
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
