# backend/orchestrator/utils/loop_prevention.py
"""
Endless loop prevention and human intervention system
"""
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LoopState(Enum):
    """State of quality improvement loop"""
    NORMAL = "normal"
    PLATEAU = "plateau"
    OSCILLATING = "oscillating"
    DEGRADING = "degrading"
    STUCK = "stuck"
    HUMAN_INTERVENTION = "human_intervention"
    ABORTED = "aborted"


class LoopPreventionSystem:
    """
    Prevents endless loops with multiple safeguards
    """
    
    def __init__(self, max_loops: int = 5, quality_threshold: float = 90.0):
        self.max_loops = max_loops
        self.quality_threshold = quality_threshold
        self.history: Dict[str, List[Dict]] = {}
        self.alert_channels = ["websocket", "email", "webhook"]
        
    async def monitor_loop(self, job_id: str, quality_scores: List[float]) -> LoopState:
        """
        Monitor quality improvement loop and detect stagnation
        
        Args:
            job_id: Job identifier
            quality_scores: List of quality scores from each iteration
            
        Returns:
            Current loop state
        """
        
        # 1. Check iteration count
        if len(quality_scores) >= self.max_loops:
            logger.warning(f"Job {job_id}: Max loops reached ({self.max_loops})")
            await self._trigger_human_intervention(job_id, "max_loops_reached")
            return LoopState.ABORTED
        
        # 2. Detect plateau (no improvement in last 3 iterations)
        if len(quality_scores) >= 3:
            last_3 = quality_scores[-3:]
            if all(score == last_3[0] for score in last_3):
                logger.warning(f"Job {job_id}: Quality plateau detected")
                await self._trigger_human_intervention(job_id, "quality_plateau")
                return LoopState.PLATEAU
        
        # 3. Detect oscillation (quality bouncing)
        if len(quality_scores) >= 4:
            last_4 = quality_scores[-4:]
            if (last_4[0] > last_4[1] < last_4[2] > last_4[3] or
                last_4[0] < last_4[1] > last_4[2] < last_4[3]):
                logger.warning(f"Job {job_id}: Quality oscillation detected")
                await self._trigger_human_intervention(job_id, "quality_oscillation")
                return LoopState.OSCILLATING
        
        # 4. Detect degradation (quality getting worse)
        if len(quality_scores) >= 3:
            if quality_scores[-1] < quality_scores[-2] < quality_scores[-3]:
                logger.warning(f"Job {job_id}: Quality degrading")
                await self._trigger_human_intervention(job_id, "quality_degrading")
                return LoopState.DEGRADING
        
        # 5. Check if stuck on same issues
        if await self._detect_stuck_issues(job_id):
            await self._trigger_human_intervention(job_id, "stuck_issues")
            return LoopState.STUCK
        
        return LoopState.NORMAL
    
    async def _detect_stuck_issues(self, job_id: str) -> bool:
        """
        Detect if the same issues keep appearing across iterations
        """
        if job_id not in self.history:
            return False
        
        history = self.history[job_id]
        if len(history) < 3:
            return False
        
        # Get issue fingerprints from last 3 iterations
        issue_sets = []
        for iteration in history[-3:]:
            issues = iteration.get("issues", [])
            issue_fingerprints = {self._fingerprint_issue(issue) for issue in issues}
            issue_sets.append(issue_fingerprints)
        
        # Check if issues are identical across iterations
        if issue_sets[0] == issue_sets[1] == issue_sets[2]:
            logger.info(f"Job {job_id}: Same issues persisting across 3 iterations")
            return True
        
        return False
    
    def _fingerprint_issue(self, issue: Dict) -> str:
        """Create unique fingerprint for an issue"""
        return f"{issue.get('type')}:{issue.get('file')}:{issue.get('line', '')}"
    
    async def _trigger_human_intervention(self, job_id: str, reason: str):
        """
        Trigger human intervention with multiple channels
        """
        intervention_data = {
            "job_id": job_id,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "history": self.history.get(job_id, []),
            "action_needed": "human_review"
        }
        
        # 1. Send via WebSocket (real-time)
        await self._send_websocket_alert(job_id, intervention_data)
        
        # 2. Store in database for dashboard
        await self._store_intervention_request(job_id, intervention_data)
        
        # 3. Send email (optional)
        await self._send_email_alert(job_id, intervention_data)
        
        logger.info(f"Human intervention triggered for job {job_id}: {reason}")
    
    async def _send_websocket_alert(self, job_id: str, data: Dict):
        """Send alert via WebSocket"""
        from main import manager
        await manager.send_progress(job_id, {
            "type": "human_intervention_required",
            "data": data
        })
    
    async def _store_intervention_request(self, job_id: str, data: Dict):
        """Store intervention request in database"""
        from database import JobDB
        db = JobDB()
        db.update_job(job_id, {
            "needs_intervention": True,
            "intervention_data": data,
            "status": "waiting_for_human"
        })
    
    async def _send_email_alert(self, job_id: str, data: Dict):
        """Send email notification"""
        # Implementation with SendGrid/Postmark
        pass
    
    def record_iteration(self, job_id: str, iteration_data: Dict):
        """Record iteration for analysis"""
        if job_id not in self.history:
            self.history[job_id] = []
        
        self.history[job_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "quality_score": iteration_data.get("quality_score"),
            "issues": iteration_data.get("issues", []),
            "fixes_applied": iteration_data.get("fixes_applied", [])
        })
        
        # Keep only last 10 iterations
        if len(self.history[job_id]) > 10:
            self.history[job_id] = self.history[job_id][-10:]


class CircuitBreaker:
    """
    Prevents infinite retry loops with state tracking
    """
    
    def __init__(self, failure_threshold: int = 3, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection
        """
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                logger.info("Circuit breaker: Half-open state")
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
                logger.info("Circuit breaker: Closed (successful call)")
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker: Opened after {self.failure_count} failures")
            
            raise


class CircuitBreakerOpenError(Exception):
    pass


class QualityStuckDetector:
    """
    Detect when quality improvement stalls
    """
    
    def __init__(self, min_improvement: float = 0.5, window_size: int = 3):
        self.min_improvement = min_improvement
        self.window_size = window_size
    
    def is_stuck(self, quality_scores: List[float]) -> bool:
        """
        Check if quality is stuck (no meaningful improvement)
        """
        if len(quality_scores) < self.window_size:
            return False
        
        recent = quality_scores[-self.window_size:]
        improvement = recent[-1] - recent[0]
        
        return improvement < self.min_improvement
    
    def get_stuck_message(self, quality_scores: List[float]) -> str:
        """Get human-readable stuck message"""
        if not self.is_stuck(quality_scores):
            return ""
        
        return f"""
        Quality improvement has stalled after {len(quality_scores)} iterations.
        Current score: {quality_scores[-1]:.1f}%
        Improvement over last {self.window_size} iterations: {quality_scores[-1] - quality_scores[-self.window_size]:.1f}%
        
        Possible reasons:
        1. Complex issues requiring human expertise
        2. Conflicting requirements
        3. Architecture limitations
        4. External dependencies
        
        Please review manually.
        """
