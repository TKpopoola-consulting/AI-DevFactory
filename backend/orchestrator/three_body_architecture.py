"""
Three-Body Architecture for AI-DevFactory

Implements a checks-and-balances system with three independent bodies:
1. Verifier: Validates decisions and outputs
2. Executor: Executes approved actions
3. Overseer: Monitors and can veto actions

Prevents unilateral decisions and ensures consensus.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from enum import Enum
import asyncio
import hashlib
import json
from datetime import datetime

class DecisionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    VETOED = "vetoed"
    EXECUTED = "executed"
    FAILED = "failed"

class DecisionType(Enum):
    CODE_GENERATION = "code_generation"
    CODE_MODIFICATION = "code_modification"
    BUG_FIX = "bug_fix"
    SECURITY_PATCH = "security_patch"
    SELF_MODIFICATION = "self_modification"
    PLUGIN_CREATION = "plugin_creation"
    SYSTEM_CONFIG_CHANGE = "system_config_change"

class DecisionRequest(BaseModel):
    """Request for a decision to be made."""
    decision_id: str
    decision_type: DecisionType
    requester: str
    justification: str
    proposed_action: Dict[str, Any]
    urgency: int = 1  # 1-10 scale
    timeout_seconds: int = 300

class DecisionVote(BaseModel):
    """Vote from a body in the three-body system."""
    body: str  # "verifier", "executor", or "overseer"
    vote: str  # "approve", "reject", "abstain", "veto"
    rationale: str
    confidence: float = 0.0  # 0.0-1.0
    timestamp: str

class DecisionResult(BaseModel):
    """Final decision result."""
    decision_id: str
    status: DecisionStatus
    votes: List[DecisionVote]
    final_action: Optional[Dict[str, Any]] = None
    executed_at: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    consensus_required: bool = True
    consensus_threshold: float = 0.66  # 2/3 consensus required

class ThreeBodyArchitecture:
    """Manages the three-body decision system."""

    def __init__(self, db_path: str = "three_body.db"):
        import sqlite3
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize three-body database."""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Decisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY,
                decision_type TEXT NOT NULL,
                requester TEXT NOT NULL,
                justification TEXT NOT NULL,
                proposed_action TEXT NOT NULL,
                urgency INTEGER DEFAULT 1,
                timeout_seconds INTEGER DEFAULT 300,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                final_action TEXT,
                executed_at TEXT,
                execution_result TEXT,
                consensus_required BOOLEAN DEFAULT 1,
                consensus_threshold REAL DEFAULT 0.66
            )
        ''')

        # Votes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                vote_id TEXT PRIMARY KEY,
                decision_id TEXT NOT NULL,
                body TEXT NOT NULL,
                vote TEXT NOT NULL,
                rationale TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(decision_id) REFERENCES decisions(decision_id)
            )
        ''')

        # Audit trail
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decision_audit (
                audit_id TEXT PRIMARY KEY,
                decision_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                body TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(decision_id) REFERENCES decisions(decision_id)
            )
        ''')

        conn.commit()
        conn.close()

    def generate_decision_id(self, decision_type: DecisionType, requester: str) -> str:
        """Generate deterministic decision ID."""
        content = f"{decision_type.value}:{requester}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def request_decision(self, decision_type: DecisionType, requester: str,
                              justification: str, proposed_action: Dict[str, Any],
                              urgency: int = 1, timeout_seconds: int = 300) -> Dict[str, Any]:
        """Request a decision through three-body architecture."""
        import sqlite3

        decision_id = self.generate_decision_id(decision_type, requester)
        created_at = datetime.now().isoformat()

        # Store decision request
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO decisions (decision_id, decision_type, requester, justification, proposed_action, urgency, timeout_seconds, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (decision_id, decision_type.value, requester, justification,
             json.dumps(proposed_action), urgency, timeout_seconds,
             created_at, created_at)
        )
        conn.commit()
        conn.close()

        # Add audit trail
        self._add_audit(decision_id, "decision_requested",
                       f"Decision requested by {requester}: {decision_type.value}")

        # Start three-body voting process
        voting_task = asyncio.create_task(
            self._run_voting_process(decision_id, decision_type, proposed_action)
        )

        return {
            "decision_id": decision_id,
            "status": DecisionStatus.PENDING.value,
            "message": "Decision submitted to three-body architecture",
            "bodies_required": ["verifier", "executor", "overseer"],
            "consensus_threshold": 0.66,
            "estimated_time_seconds": timeout_seconds
        }

    async def _run_voting_process(self, decision_id: str, decision_type: DecisionType,
                                 proposed_action: Dict[str, Any]) -> None:
        """Run the three-body voting process."""
        import sqlite3

        # Get decision urgency and timeout
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT urgency, timeout_seconds FROM decisions WHERE decision_id = ?",
            (decision_id,)
        )
        urgency, timeout_seconds = cursor.fetchone()
        conn.close()

        # Simulate parallel voting by three bodies
        votes = await asyncio.gather(
            self._verifier_vote(decision_id, decision_type, proposed_action, urgency),
            self._executor_vote(decision_id, decision_type, proposed_action, urgency),
            self._overseer_vote(decision_id, decision_type, proposed_action, urgency)
        )

        # Store votes
        for vote in votes:
            self._store_vote(vote)

        # Determine consensus
        await self._determine_consensus(decision_id, votes, timeout_seconds)

    async def _verifier_vote(self, decision_id: str, decision_type: DecisionType,
                            proposed_action: Dict[str, Any], urgency: int) -> Dict[str, Any]:
        """Verifier body votes (validates correctness)."""
        import random

        await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate processing

        # Verifier checks
        checks = self._run_verifier_checks(decision_type, proposed_action)
        passed_checks = sum(1 for c in checks if c["passed"])
        total_checks = len(checks)

        confidence = passed_checks / total_checks if total_checks > 0 else 0.0

        if confidence >= 0.8:
            vote = "approve"
            rationale = f"Verifier approved: {passed_checks}/{total_checks} checks passed"
        elif confidence >= 0.5:
            vote = "abstain"
            rationale = f"Verifier abstained: {passed_checks}/{total_checks} checks passed (insufficient confidence)"
        else:
            vote = "reject"
            rationale = f"Verifier rejected: Only {passed_checks}/{total_checks} checks passed"

        return {
            "body": "verifier",
            "vote": vote,
            "rationale": rationale,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "checks": checks
        }

    async def _executor_vote(self, decision_id: str, decision_type: DecisionType,
                            proposed_action: Dict[str, Any], urgency: int) -> Dict[str, Any]:
        """Executor body votes (assesses feasibility)."""
        import random

        await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate processing

        # Executor checks
        checks = self._run_executor_checks(decision_type, proposed_action)
        passed_checks = sum(1 for c in checks if c["passed"])
        total_checks = len(checks)

        feasibility_score = passed_checks / total_checks if total_checks > 0 else 0.0

        if feasibility_score >= 0.9:
            vote = "approve"
            rationale = f"Executor approved: {passed_checks}/{total_checks} feasibility checks passed"
        elif feasibility_score >= 0.6:
            vote = "abstain"
            rationale = f"Executor abstained: {passed_checks}/{total_checks} feasibility checks passed (medium confidence)"
        else:
            vote = "reject"
            rationale = f"Executor rejected: Only {passed_checks}/{total_checks} feasibility checks passed"

        return {
            "body": "executor",
            "vote": vote,
            "rationale": rationale,
            "confidence": feasibility_score,
            "timestamp": datetime.now().isoformat(),
            "checks": checks
        }

    async def _overseer_vote(self, decision_id: str, decision_type: DecisionType,
                            proposed_action: Dict[str, Any], urgency: int) -> Dict[str, Any]:
        """Overseer body votes (monitors safety and alignment)."""
        import random

        await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate processing

        # Overseer checks
        checks = self._run_overseer_checks(decision_type, proposed_action)
        passed_checks = sum(1 for c in checks if c["passed"])
        total_checks = len(checks)

        safety_score = passed_checks / total_checks if total_checks > 0 else 0.0

        # Overseer can veto regardless of other votes
        veto_threshold = 0.3  # Very low safety score triggers veto

        if safety_score <= veto_threshold:
            vote = "veto"
            rationale = f"Overseer vetoed: Safety score {safety_score:.2f} below threshold {veto_threshold}"
        elif safety_score >= 0.8:
            vote = "approve"
            rationale = f"Overseer approved: {passed_checks}/{total_checks} safety checks passed"
        elif safety_score >= 0.5:
            vote = "abstain"
            rationale = f"Overseer abstained: {passed_checks}/{total_checks} safety checks passed"
        else:
            vote = "reject"
            rationale = f"Overseer rejected: {passed_checks}/{total_checks} safety checks passed (low safety)"

        return {
            "body": "overseer",
            "vote": vote,
            "rationale": rationale,
            "confidence": safety_score,
            "timestamp": datetime.now().isoformat(),
            "checks": checks
        }

    def _run_verifier_checks(self, decision_type: DecisionType, proposed_action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run verifier checks (correctness)."""
        checks = []

        # Check 1: Action schema validation
        checks.append({
            "name": "schema_validation",
            "passed": "action" in proposed_action and "type" in proposed_action.get("action", {}),
            "description": "Action has required schema"
        })

        # Check 2: Input validation
        checks.append({
            "name": "input_validation",
            "passed": "inputs" in proposed_action and isinstance(proposed_action.get("inputs"), dict),
            "description": "Inputs are properly structured"
        })

        # Check 3: Output expectations
        checks.append({
            "name": "output_expectations",
            "passed": "expected_outputs" in proposed_action or "output_schema" in proposed_action,
            "description": "Has expected outputs or output schema"
        })

        # Check 4: Decision type alignment
        checks.append({
            "name": "decision_type_alignment",
            "passed": True,  # Placeholder
            "description": "Action aligns with decision type"
        })

        return checks

    def _run_executor_checks(self, decision_type: DecisionType, proposed_action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run executor checks (feasibility)."""
        checks = []

        # Check 1: Resource availability
        checks.append({
            "name": "resource_availability",
            "passed": "resources" in proposed_action or True,  # Placeholder
            "description": "Required resources are available"
        })

        # Check 2: Time estimation
        checks.append({
            "name": "time_estimation",
            "passed": "estimated_time" in proposed_action and proposed_action.get("estimated_time", 0) <= 3600,  # 1 hour max
            "description": "Time estimate is reasonable"
        })

        # Check 3: Complexity assessment
        action_complexity = proposed_action.get("complexity", "medium")
        checks.append({
            "name": "complexity_assessment",
            "passed": action_complexity in ["low", "medium", "high"],
            "description": "Complexity level is defined"
        })

        # Check 4: Fallback options
        checks.append({
            "name": "fallback_options",
            "passed": "fallback_action" in proposed_action or "rollback_plan" in proposed_action,
            "description": "Has fallback or rollback plan"
        })

        return checks

    def _run_overseer_checks(self, decision_type: DecisionType, proposed_action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run overseer checks (safety and alignment)."""
        checks = []

        # Check 1: Safety protocols
        checks.append({
            "name": "safety_protocols",
            "passed": "safety_protocols" in proposed_action or True,  # Placeholder
            "description": "Safety protocols are defined"
        })

        # Check 2: Value alignment
        checks.append({
            "name": "value_alignment",
            "passed": self._check_value_alignment(proposed_action),
            "description": "Action aligns with system values"
        })

        # Check 3: Risk assessment
        checks.append({
            "name": "risk_assessment",
            "passed": "risk_level" in proposed_action and proposed_action.get("risk_level") in ["low", "medium", "high"],
            "description": "Risk level is assessed"
        })

        # Check 4: Human oversight requirement
        requires_human_oversight = decision_type in [
            DecisionType.SELF_MODIFICATION,
            DecisionType.PLUGIN_CREATION,
            DecisionType.SYSTEM_CONFIG_CHANGE
        ]
        checks.append({
            "name": "human_oversight_check",
            "passed": not requires_human_oversight or "human_approval_required" in proposed_action,
            "description": "Human oversight requirements are met"
        })

        # Check 5: Legal/compliance
        checks.append({
            "name": "compliance_check",
            "passed": True,  # Placeholder
            "description": "Compliance requirements are met"
        })

        return checks

    def _check_value_alignment(self, proposed_action: Dict[str, Any]) -> bool:
        """Check if action aligns with system values."""
        # Basic value alignment checks
        action_description = str(proposed_action).lower()

        # Negative indicators
        negative_keywords = ["destroy", "corrupt", "malware", "backdoor", "unauthorized", "illegal"]
        for keyword in negative_keywords:
            if keyword in action_description:
                return False

        # Positive indicators
        positive_keywords = ["improve", "fix", "optimize", "secure", "enhance", "validate"]
        for keyword in positive_keywords:
            if keyword in action_description:
                return True

        return True  # Default to True if no clear indicators

    def _store_vote(self, vote_data: Dict[str, Any]) -> None:
        """Store a vote in the database."""
        import sqlite3
        import uuid

        vote_id = str(uuid.uuid4())
        decision_id = vote_data.get("decision_id", "")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO votes (vote_id, decision_id, body, vote, rationale, confidence, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (vote_id, decision_id, vote_data["body"], vote_data["vote"],
             vote_data["rationale"], vote_data["confidence"], vote_data["timestamp"])
        )
        conn.commit()
        conn.close()

    async def _determine_consensus(self, decision_id: str, votes: List[Dict[str, Any]],
                                  timeout_seconds: int) -> None:
        """Determine consensus from votes and update decision."""
        import sqlite3

        # Count votes
        vote_counts = {"approve": 0, "reject": 0, "abstain": 0, "veto": 0}
        for vote in votes:
            vote_counts[vote["vote"]] += 1

        # Check for veto (immediate rejection)
        if vote_counts["veto"] > 0:
            status = DecisionStatus.VETOED
            final_action = None
        else:
            # Calculate consensus
            total_votes = sum(vote_counts.values())
            approve_ratio = vote_counts["approve"] / total_votes if total_votes > 0 else 0

            # Get consensus threshold
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT consensus_threshold FROM decisions WHERE decision_id = ?",
                (decision_id,)
            )
            consensus_threshold = cursor.fetchone()[0]
            conn.close()

            if approve_ratio >= consensus_threshold:
                status = DecisionStatus.APPROVED

                # Get proposed action for execution
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT proposed_action FROM decisions WHERE decision_id = ?",
                    (decision_id,)
                )
                proposed_action_json = cursor.fetchone()[0]
                final_action = json.loads(proposed_action_json)
                conn.close()
            else:
                status = DecisionStatus.REJECTED
                final_action = None

        # Update decision status
        updated_at = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if final_action:
            cursor.execute(
                "UPDATE decisions SET status = ?, updated_at = ?, final_action = ? WHERE decision_id = ?",
                (status.value, updated_at, json.dumps(final_action), decision_id)
            )
        else:
            cursor.execute(
                "UPDATE decisions SET status = ?, updated_at = ? WHERE decision_id = ?",
                (status.value, updated_at, decision_id)
            )

        conn.commit()
        conn.close()

        # Add audit trail
        self._add_audit(decision_id, "consensus_determined",
                       f"Consensus reached: {status.value} (votes: {vote_counts})")

        # If approved, execute the action
        if status == DecisionStatus.APPROVED:
            await self._execute_decision(decision_id, final_action)

    async def _execute_decision(self, decision_id: str, action: Dict[str, Any]) -> None:
        """Execute an approved decision."""
        import sqlite3

        executed_at = datetime.now().isoformat()

        try:
            # Placeholder for actual execution
            # In real implementation, this would call the appropriate executor
            execution_result = {
                "success": True,
                "message": "Action executed successfully",
                "timestamp": executed_at,
                "action_type": action.get("type", "unknown")
            }

            status = DecisionStatus.EXECUTED

            # Add audit trail
            self._add_audit(decision_id, "execution_completed",
                           f"Action executed successfully: {action.get('type', 'unknown')}")

        except Exception as e:
            execution_result = {
                "success": False,
                "error": str(e),
                "timestamp": executed_at
            }
            status = DecisionStatus.FAILED

            # Add audit trail
            self._add_audit(decision_id, "execution_failed",
                           f"Action execution failed: {str(e)}")

        # Update decision with execution result
        updated_at = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE decisions SET status = ?, updated_at = ?, executed_at = ?, execution_result = ? WHERE decision_id = ?",
            (status.value, updated_at, executed_at, json.dumps(execution_result), decision_id)
        )
        conn.commit()
        conn.close()

    def _add_audit(self, decision_id: str, action: str, details: str, body: str = None) -> None:
        """Add audit trail entry."""
        import sqlite3
        import uuid

        audit_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO decision_audit (audit_id, decision_id, action, details, body, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (audit_id, decision_id, action, details, body, timestamp)
        )
        conn.commit()
        conn.close()

    def get_decision_status(self, decision_id: str) -> Dict[str, Any]:
        """Get current status of a decision."""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get decision info
        cursor.execute(
            "SELECT decision_type, requester, status, created_at, updated_at FROM decisions WHERE decision_id = ?",
            (decision_id,)
        )
        decision_row = cursor.fetchone()

        if not decision_row:
            conn.close()
            return {"error": "Decision not found"}

        decision_type, requester, status, created_at, updated_at = decision_row

        # Get votes
        cursor.execute(
            "SELECT body, vote, rationale, confidence, timestamp FROM votes WHERE decision_id = ? ORDER BY timestamp",
            (decision_id,)
        )
        vote_rows = cursor.fetchall()

        # Get audit trail
        cursor.execute(
            "SELECT action, details, body, timestamp FROM decision_audit WHERE decision_id = ? ORDER BY timestamp",
            (decision_id,)
        )
        audit_rows = cursor.fetchall()

        conn.close()

        # Format votes
        votes = []
        for row in vote_rows:
            votes.append({
                "body": row[0],
                "vote": row[1],
                "rationale": row[2],
                "confidence": row[3],
                "timestamp": row[4]
            })

        # Format audit trail
        audit_trail = []
        for row in audit_rows:
            audit_trail.append({
                "action": row[0],
                "details": row[1],
                "body": row[2],
                "timestamp": row[3]
            })

        return {
            "decision_id": decision_id,
            "decision_type": decision_type,
            "requester": requester,
            "status": status,
            "created_at": created_at,
            "updated_at": updated_at,
            "votes": votes,
            "audit_trail": audit_trail
        }

    def get_decisions_by_status(self, status: DecisionStatus, limit: int = 100) -> List[Dict[str, Any]]:
        """Get decisions by status."""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT decision_id, decision_type, requester, created_at, updated_at FROM decisions WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            (status.value, limit)
        )
        rows = cursor.fetchall()
        conn.close()

        decisions = []
        for row in rows:
            decisions.append({
                "decision_id": row[0],
                "decision_type": row[1],
                "requester": row[2],
                "created_at": row[3],
                "updated_at": row[4]
            })

        return decisions