"""
Capability Escalation Ladder for AI-DevFactory

Prevents uncontrolled self-modification by requiring explicit approval
for each level of capability escalation.
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import hashlib

class CapabilityLevel(Enum):
    """Capability levels with increasing power and restrictions."""
    LEVEL_1_OBSERVE = "observe"  # Can only read and analyze code
    LEVEL_2_GENERATE = "generate"  # Can generate new code from scratch
    LEVEL_3_MODIFY = "modify"  # Can modify existing code (refactor, optimize)
    LEVEL_4_REPAIR = "repair"  # Can fix bugs and security issues
    LEVEL_5_ARCHITECT = "architect"  # Can design system architecture
    LEVEL_6_SELF_MODIFY = "self_modify"  # Can modify its own code (restricted)
    LEVEL_7_PLUGIN_CREATE = "plugin_create"  # Can create new plugins
    LEVEL_8_CORE_MODIFY = "core_modify"  # Can modify core systems (requires human review)

class CapabilityRequest(BaseModel):
    """Request to escalate capabilities."""
    level: CapabilityLevel
    justification: str
    timeout_minutes: int = 60  # How long escalation lasts
    verification_required: bool = True

class CapabilityApproval(BaseModel):
    """Approval record for capability escalation."""
    request_id: str
    level: CapabilityLevel
    approver: str = "system"  # "system", "human", or user ID
    approved_at: str
    expires_at: str
    restrictions: Dict[str, Any] = {}  # Additional restrictions
    audit_trail: list = []  # Actions taken during escalation

class CapabilityLadder:
    """Manages capability escalation with audit trails."""

    def __init__(self, db_path: str = "capabilities.db"):
        import sqlite3
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize capability database."""
        import sqlite3
        from datetime import datetime
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capability_requests (
                request_id TEXT PRIMARY KEY,
                level TEXT NOT NULL,
                justification TEXT NOT NULL,
                requester TEXT NOT NULL,
                requested_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                approved_by TEXT,
                approved_at TEXT,
                expires_at TEXT,
                restrictions TEXT,
                audit_trail TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capability_audit (
                audit_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(request_id) REFERENCES capability_requests(request_id)
            )
        ''')
        conn.commit()
        conn.close()

    def generate_request_id(self, level: CapabilityLevel, justification: str) -> str:
        """Generate deterministic request ID."""
        content = f"{level.value}:{justification}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def request_escalation(self, level: CapabilityLevel, justification: str,
                          requester: str = "system") -> Dict[str, Any]:
        """Request capability escalation."""
        import sqlite3

        request_id = self.generate_request_id(level, justification)
        requested_at = datetime.now().isoformat()

        # Check if agent already has this capability
        current_level = self.get_current_level(requester)
        if current_level and self._level_to_int(current_level) >= self._level_to_int(level):
            return {
                "request_id": request_id,
                "status": "already_granted",
                "level": level.value,
                "message": f"Already at or above level {level.value}"
            }

        # Store request
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO capability_requests (request_id, level, justification, requester, requested_at, status) VALUES (?, ?, ?, ?, ?, ?)",
            (request_id, level.value, justification, requester, requested_at, "pending")
        )
        conn.commit()
        conn.close()

        # Different approval paths based on level
        if self._level_to_int(level) <= 3:  # Levels 1-3: Auto-approve
            return self._auto_approve(request_id, level, requester)
        elif self._level_to_int(level) <= 5:  # Levels 4-5: System verification
            return self._system_verify(request_id, level, requester, justification)
        else:  # Levels 6+: Require human review
            return {
                "request_id": request_id,
                "status": "requires_human_review",
                "level": level.value,
                "message": f"Level {level.value} requires human review",
                "verification_steps": [
                    "Three-body architecture consensus required",
                    "Human approval via dashboard",
                    "Time-limited escalation with monitoring"
                ]
            }

    def _auto_approve(self, request_id: str, level: CapabilityLevel, requester: str) -> Dict[str, Any]:
        """Auto-approve low-risk capability requests."""
        import sqlite3

        approved_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE capability_requests SET status = ?, approved_by = ?, approved_at = ?, expires_at = ? WHERE request_id = ?",
            ("approved", "system_auto", approved_at, expires_at, request_id)
        )
        conn.commit()
        conn.close()

        # Add audit trail
        self._add_audit(request_id, "auto_approve",
                       f"Auto-approved level {level.value} for {requester}")

        return {
            "request_id": request_id,
            "status": "approved",
            "level": level.value,
            "approved_by": "system_auto",
            "approved_at": approved_at,
            "expires_at": expires_at,
            "restrictions": self._get_level_restrictions(level)
        }

    def _system_verify(self, request_id: str, level: CapabilityLevel,
                      requester: str, justification: str) -> Dict[str, Any]:
        """Verify mid-level capability requests."""
        import sqlite3

        # Run verification checks
        verification_checks = self._run_verification_checks(level, justification)

        if verification_checks["passed"]:
            approved_at = datetime.now().isoformat()
            expires_at = (datetime.now() + timedelta(hours=12)).isoformat()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE capability_requests SET status = ?, approved_by = ?, approved_at = ?, expires_at = ?, restrictions = ? WHERE request_id = ?",
                ("approved", "system_verified", approved_at, expires_at,
                 json.dumps(verification_checks["restrictions"]), request_id)
            )
            conn.commit()
            conn.close()

            self._add_audit(request_id, "system_verify",
                           f"System-verified level {level.value}: {verification_checks['summary']}")

            return {
                "request_id": request_id,
                "status": "approved",
                "level": level.value,
                "approved_by": "system_verified",
                "approved_at": approved_at,
                "expires_at": expires_at,
                "restrictions": verification_checks["restrictions"],
                "verification_summary": verification_checks["summary"]
            }
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE capability_requests SET status = ? WHERE request_id = ?",
                ("denied", request_id)
            )
            conn.commit()
            conn.close()

            self._add_audit(request_id, "system_deny",
                           f"System denied level {level.value}: {verification_checks['reason']}")

            return {
                "request_id": request_id,
                "status": "denied",
                "level": level.value,
                "reason": verification_checks["reason"],
                "failed_checks": verification_checks.get("failed_checks", [])
            }

    def _run_verification_checks(self, level: CapabilityLevel, justification: str) -> Dict[str, Any]:
        """Run verification checks for capability requests."""
        checks = []

        # Check 1: Justification quality
        if len(justification) < 20:
            checks.append({"name": "justification_length", "passed": False,
                          "reason": "Justification too short"})
        else:
            checks.append({"name": "justification_length", "passed": True})

        # Check 2: Alignment with system goals
        goal_keywords = ["improve", "fix", "optimize", "secure", "enhance"]
        justification_lower = justification.lower()
        has_goal_alignment = any(keyword in justification_lower for keyword in goal_keywords)
        checks.append({
            "name": "goal_alignment",
            "passed": has_goal_alignment,
            "reason": "Justification doesn't align with system goals" if not has_goal_alignment else None
        })

        # Check 3: Risk assessment based on level
        risk_level = self._level_to_int(level)
        if risk_level >= 6:
            # High-risk capabilities require stronger justification
            high_risk_keywords = ["security", "critical", "essential", "required", "must"]
            has_high_risk_justification = any(keyword in justification_lower for keyword in high_risk_keywords)
            checks.append({
                "name": "high_risk_justification",
                "passed": has_high_risk_justification,
                "reason": "High-risk capability requires stronger justification" if not has_high_risk_justification else None
            })

        # Calculate result
        passed_checks = [c for c in checks if c["passed"]]
        failed_checks = [c for c in checks if not c["passed"]]

        if failed_checks:
            return {
                "passed": False,
                "reason": f"Failed {len(failed_checks)} verification checks",
                "failed_checks": failed_checks,
                "passed_checks": passed_checks
            }

        # Generate restrictions based on level
        restrictions = self._get_level_restrictions(level)

        return {
            "passed": True,
            "summary": f"Passed all {len(checks)} verification checks",
            "restrictions": restrictions,
            "checks": checks
        }

    def _get_level_restrictions(self, level: CapabilityLevel) -> Dict[str, Any]:
        """Get restrictions for a capability level."""
        restrictions = {
            "monitoring_enabled": True,
            "audit_trail_required": True,
            "time_limit_hours": 24
        }

        level_int = self._level_to_int(level)

        if level_int >= 4:  # REPAIR level and above
            restrictions["code_review_required"] = True
            restrictions["test_coverage_required"] = 0.8

        if level_int >= 6:  # SELF_MODIFY level and above
            restrictions["three_body_consensus"] = True
            restrictions["human_notification"] = True
            restrictions["rollback_plan_required"] = True
            restrictions["time_limit_hours"] = 4  # Shorter for high-risk

        if level_int >= 8:  # CORE_MODIFY level
            restrictions["human_approval_required"] = True
            restrictions["multi_factor_verification"] = True
            restrictions["time_limit_hours"] = 1
            restrictions["snapshot_before"] = True

        return restrictions

    def _level_to_int(self, level: CapabilityLevel) -> int:
        """Convert capability level to integer for comparison."""
        level_map = {
            CapabilityLevel.LEVEL_1_OBSERVE: 1,
            CapabilityLevel.LEVEL_2_GENERATE: 2,
            CapabilityLevel.LEVEL_3_MODIFY: 3,
            CapabilityLevel.LEVEL_4_REPAIR: 4,
            CapabilityLevel.LEVEL_5_ARCHITECT: 5,
            CapabilityLevel.LEVEL_6_SELF_MODIFY: 6,
            CapabilityLevel.LEVEL_7_PLUGIN_CREATE: 7,
            CapabilityLevel.LEVEL_8_CORE_MODIFY: 8
        }
        return level_map.get(level, 0)

    def get_current_level(self, requester: str) -> Optional[CapabilityLevel]:
        """Get current capability level for a requester."""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT level, expires_at FROM capability_requests WHERE requester = ? AND status = 'approved' ORDER BY approved_at DESC LIMIT 1",
            (requester,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            level_str, expires_at = row
            # Check if still valid
            if expires_at and datetime.fromisoformat(expires_at) > datetime.now():
                try:
                    return CapabilityLevel(level_str)
                except ValueError:
                    return None

        return None

    def _add_audit(self, request_id: str, action: str, details: str):
        """Add audit trail entry."""
        import sqlite3
        import uuid

        audit_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO capability_audit (audit_id, request_id, action, details, timestamp) VALUES (?, ?, ?, ?, ?)",
            (audit_id, request_id, action, details, timestamp)
        )
        conn.commit()
        conn.close()

    def get_audit_trail(self, request_id: str) -> list:
        """Get audit trail for a capability request."""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT action, details, timestamp FROM capability_audit WHERE request_id = ? ORDER BY timestamp",
            (request_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [{"action": r[0], "details": r[1], "timestamp": r[2]} for r in rows]

    def revoke_capability(self, request_id: str, reason: str, revoked_by: str = "system") -> Dict[str, Any]:
        """Revoke a capability."""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE capability_requests SET status = 'revoked', expires_at = ? WHERE request_id = ?",
            (datetime.now().isoformat(), request_id)
        )
        conn.commit()
        conn.close()

        self._add_audit(request_id, "revoke", f"Revoked by {revoked_by}: {reason}")

        return {
            "request_id": request_id,
            "status": "revoked",
            "reason": reason,
            "revoked_by": revoked_by,
            "revoked_at": datetime.now().isoformat()
        }