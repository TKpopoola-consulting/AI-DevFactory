"""
Value Alignment Engine for AI-DevFactory and Plugin Ecosystem

Ensures all actions align with human values and system constraints.
Implements ethical guidelines, compliance checks, and value alignment scoring.
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
from enum import Enum
import re
import json
from datetime import datetime

class ValueCategory(Enum):
    """Categories of values to align with."""
    SAFETY = "safety"
    ETHICS = "ethics"
    LEGAL = "legal"
    PRIVACY = "privacy"
    FAIRNESS = "fairness"
    TRANSPARENCY = "transparency"
    HUMAN_CONTROL = "human_control"
    BENEFICENCE = "beneficence"  # Doing good
    NON_MALEFICENCE = "non_maleficence"  # Avoiding harm

class AlignmentScore(BaseModel):
    """Score for value alignment."""
    category: ValueCategory
    score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    issues: List[str] = []
    recommendations: List[str] = []

class ActionType(Enum):
    """Types of actions to evaluate."""
    CODE_GENERATION = "code_generation"
    CODE_MODIFICATION = "code_modification"
    BUG_FIX = "bug_fix"
    SECURITY_OPERATION = "security_operation"
    DATA_ACCESS = "data_access"
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    SELF_MODIFICATION = "self_modification"
    PLUGIN_CREATION = "plugin_creation"
    USER_INTERACTION = "user_interaction"

class ValueAlignmentRequest(BaseModel):
    """Request for value alignment evaluation."""
    action_type: ActionType
    action_description: str
    proposed_code: Optional[str] = None
    context: Dict[str, Any] = {}
    user_intent: Optional[str] = None
    strict_mode: bool = False  # If True, requires higher alignment scores

class ValueAlignmentResult(BaseModel):
    """Result of value alignment evaluation."""
    request_id: str
    overall_score: float  # 0.0-1.0
    passed: bool
    category_scores: List[AlignmentScore]
    critical_issues: List[str] = []
    warnings: List[str] = []
    approval_required: bool = False
    approval_level: str = "none"  # "none", "automated", "human", "escalated"
    recommendations: List[str] = []
    audit_trail: List[Dict[str, Any]] = []

class ValueAlignmentEngine:
    """Engine for evaluating value alignment."""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.value_guidelines = self._load_value_guidelines()
        self.ethical_frameworks = self._load_ethical_frameworks()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration for value alignment."""
        default_config = {
            "min_score_threshold": 0.7,
            "strict_mode_threshold": 0.9,
            "critical_issue_threshold": 0.3,
            "require_human_approval_for": [
                "self_modification",
                "system_config_change",
                "security_operation.high_risk"
            ],
            "blocked_patterns": [
                r"eval\s*\(",
                r"exec\s*\(",
                r"__import__\s*\(",
                r"os\.system\s*\(",
                r"subprocess\.Popen\s*\("
            ],
            "sensitive_patterns": [
                r"password\s*=",
                r"api_key\s*=",
                r"secret\s*=",
                r"token\s*="
            ]
        }
        return default_config

    def _load_value_guidelines(self) -> Dict[str, List[str]]:
        """Load value alignment guidelines."""
        return {
            "safety": [
                "Avoid actions that could harm users or systems",
                "Ensure code doesn't contain security vulnerabilities",
                "Validate all inputs and sanitize outputs",
                "Include error handling and fail-safes"
            ],
            "ethics": [
                "Respect user autonomy and consent",
                "Avoid deception or manipulation",
                "Ensure transparency about capabilities and limitations",
                "Respect intellectual property rights"
            ],
            "legal": [
                "Comply with applicable laws and regulations",
                "Respect terms of service and licensing",
                "Avoid illegal or prohibited activities",
                "Respect copyright and trademark laws"
            ],
            "privacy": [
                "Protect user data and privacy",
                "Minimize data collection to what's necessary",
                "Secure sensitive information",
                "Provide transparency about data usage"
            ],
            "fairness": [
                "Avoid bias in algorithms and outputs",
                "Treat all users equitably",
                "Provide equal access to capabilities",
                "Avoid discrimination based on protected characteristics"
            ],
            "transparency": [
                "Be clear about what the system is doing",
                "Explain limitations and uncertainties",
                "Provide audit trails for decisions",
                "Allow users to understand system behavior"
            ],
            "human_control": [
                "Ensure humans remain in control",
                "Provide override mechanisms",
                "Allow human review of significant decisions",
                "Maintain human accountability"
            ],
            "beneficence": [
                "Act to benefit users and society",
                "Improve user experience and outcomes",
                "Solve problems and create value",
                "Enhance capabilities and productivity"
            ],
            "non_maleficence": [
                "First, do no harm",
                "Avoid negative consequences",
                "Minimize risks and side effects",
                "Prevent misuse and abuse"
            ]
        }

    def _load_ethical_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Load ethical frameworks for decision making."""
        return {
            "asimov": {
                "name": "Asimov's Three Laws",
                "principles": [
                    "A robot may not injure a human being or, through inaction, allow a human being to come to harm.",
                    "A robot must obey the orders given it by human beings except where such orders would conflict with the First Law.",
                    "A robot must protect its own existence as long as such protection does not conflict with the First or Second Law."
                ],
                "weight": 0.8
            },
            "acm": {
                "name": "ACM Code of Ethics",
                "principles": [
                    "Contribute to society and human well-being",
                    "Avoid harm to others",
                    "Be honest and trustworthy",
                    "Be fair and take action not to discriminate",
                    "Honor property rights including copyrights and patents",
                    "Give proper credit for intellectual property",
                    "Respect the privacy of others",
                    "Honor confidentiality"
                ],
                "weight": 0.9
            },
            "eu": {
                "name": "EU Ethics Guidelines for Trustworthy AI",
                "principles": [
                    "Human agency and oversight",
                    "Technical robustness and safety",
                    "Privacy and data governance",
                    "Transparency",
                    "Diversity, non-discrimination and fairness",
                    "Societal and environmental well-being",
                    "Accountability"
                ],
                "weight": 0.85
            },
            "simple": {
                "name": "Simple Ethical Framework",
                "principles": [
                    "Is this action helpful?",
                    "Is this action honest?",
                    "Is this action harmless?",
                    "Does this action respect autonomy?",
                    "Can this action be reversed if needed?"
                ],
                "weight": 0.7
            }
        }

    def generate_request_id(self, action_type: ActionType, description: str) -> str:
        """Generate deterministic request ID."""
        import hashlib
        content = f"{action_type.value}:{description}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def evaluate_alignment(self, request: ValueAlignmentRequest) -> ValueAlignmentResult:
        """Evaluate value alignment of an action."""
        request_id = self.generate_request_id(request.action_type, request.action_description)
        audit_trail = []

        # Step 1: Initial safety scan
        safety_scan = self._run_safety_scan(request)
        audit_trail.append({
            "step": "safety_scan",
            "result": safety_scan,
            "timestamp": datetime.now().isoformat()
        })

        # Step 2: Pattern matching for blocked/sensitive content
        pattern_check = self._check_patterns(request)
        audit_trail.append({
            "step": "pattern_check",
            "result": pattern_check,
            "timestamp": datetime.now().isoformat()
        })

        # Step 3: Category-specific evaluation
        category_scores = self._evaluate_categories(request)
        audit_trail.append({
            "step": "category_evaluation",
            "result": {"categories_evaluated": len(category_scores)},
            "timestamp": datetime.now().isoformat()
        })

        # Step 4: Calculate overall score
        overall_score = self._calculate_overall_score(category_scores)

        # Step 5: Check thresholds and determine approval
        thresholds = self._check_thresholds(overall_score, category_scores, request.strict_mode)

        # Step 6: Compile issues and warnings
        all_issues = []
        all_warnings = []
        for score in category_scores:
            all_issues.extend(score.issues)
            all_warnings.extend(score.recommendations)

        # Filter critical issues (scores below critical threshold)
        critical_issues = []
        for score in category_scores:
            if score.score < self.config["critical_issue_threshold"]:
                critical_issues.extend(score.issues)

        # Add pattern check issues
        if pattern_check.get("blocked_patterns_found"):
            critical_issues.append(f"Blocked patterns detected: {pattern_check.get('blocked_patterns_found')}")

        # Determine if passed
        passed = (
            overall_score >= self.config["min_score_threshold"] and
            not critical_issues and
            (not request.strict_mode or overall_score >= self.config["strict_mode_threshold"])
        )

        # Determine approval requirements
        approval_info = self._determine_approval_requirements(
            request.action_type, overall_score, critical_issues, request.strict_mode
        )

        result = ValueAlignmentResult(
            request_id=request_id,
            overall_score=overall_score,
            passed=passed,
            category_scores=category_scores,
            critical_issues=critical_issues,
            warnings=all_warnings,
            approval_required=approval_info["required"],
            approval_level=approval_info["level"],
            recommendations=self._generate_recommendations(category_scores, overall_score, passed),
            audit_trail=audit_trail
        )

        return result

    def _run_safety_scan(self, request: ValueAlignmentRequest) -> Dict[str, Any]:
        """Run initial safety scan on the action."""
        scan_results = {
            "has_code": bool(request.proposed_code),
            "code_length": len(request.proposed_code) if request.proposed_code else 0,
            "description_length": len(request.action_description),
            "action_type_risk": self._get_action_type_risk(request.action_type)
        }

        # Check for dangerous keywords in description
        dangerous_keywords = ["destroy", "corrupt", "hack", "bypass", "exploit", "unauthorized"]
        description_lower = request.action_description.lower()
        found_keywords = [kw for kw in dangerous_keywords if kw in description_lower]

        if found_keywords:
            scan_results["dangerous_keywords_found"] = found_keywords
            scan_results["danger_level"] = "high"
        else:
            scan_results["danger_level"] = "low"

        return scan_results

    def _check_patterns(self, request: ValueAlignmentRequest) -> Dict[str, Any]:
        """Check for blocked or sensitive patterns in code."""
        results = {
            "blocked_patterns_found": [],
            "sensitive_patterns_found": [],
            "code_analyzed": False
        }

        if not request.proposed_code:
            return results

        results["code_analyzed"] = True

        # Check blocked patterns
        for pattern in self.config["blocked_patterns"]:
            if re.search(pattern, request.proposed_code, re.IGNORECASE):
                results["blocked_patterns_found"].append(pattern)

        # Check sensitive patterns
        for pattern in self.config["sensitive_patterns"]:
            if re.search(pattern, request.proposed_code, re.IGNORECASE):
                results["sensitive_patterns_found"].append(pattern)

        return results

    def _evaluate_categories(self, request: ValueAlignmentRequest) -> List[AlignmentScore]:
        """Evaluate each value category."""
        scores = []

        for category in ValueCategory:
            evaluation = self._evaluate_single_category(category, request)
            scores.append(evaluation)

        return scores

    def _evaluate_single_category(self, category: ValueCategory, request: ValueAlignmentRequest) -> AlignmentScore:
        """Evaluate a single value category."""
        issues = []
        recommendations = []
        base_score = 0.5  # Start with neutral score
        confidence = 0.7  # Default confidence

        if category == ValueCategory.SAFETY:
            score, conf, iss, rec = self._evaluate_safety(request)
            return AlignmentScore(
                category=category,
                score=score,
                confidence=conf,
                issues=iss,
                recommendations=rec
            )

        elif category == ValueCategory.ETHICS:
            score, conf, iss, rec = self._evaluate_ethics(request)
            return AlignmentScore(
                category=category,
                score=score,
                confidence=conf,
                issues=iss,
                recommendations=rec
            )

        elif category == ValueCategory.LEGAL:
            score, conf, iss, rec = self._evaluate_legal(request)
            return AlignmentScore(
                category=category,
                score=score,
                confidence=conf,
                issues=iss,
                recommendations=rec
            )

        elif category == ValueCategory.PRIVACY:
            score, conf, iss, rec = self._evaluate_privacy(request)
            return AlignmentScore(
                category=category,
                score=score,
                confidence=conf,
                issues=iss,
                recommendations=rec
            )

        # For other categories, use generic evaluation
        return AlignmentScore(
            category=category,
            score=base_score,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations
        )

    def _evaluate_safety(self, request: ValueAlignmentRequest) -> Tuple[float, float, List[str], List[str]]:
        """Evaluate safety category."""
        score = 0.7
        confidence = 0.8
        issues = []
        recommendations = []

        # Check action type risk
        risk_level = self._get_action_type_risk(request.action_type)
        if risk_level == "high":
            score -= 0.3
            issues.append(f"High-risk action type: {request.action_type.value}")
            recommendations.append("Consider breaking down into lower-risk actions")
        elif risk_level == "medium":
            score -= 0.1

        # Check for safety keywords in description
        safety_keywords = ["safe", "secure", "validate", "test", "backup"]
        danger_keywords = ["unsafe", "dangerous", "experimental", "untested"]

        description_lower = request.action_description.lower()
        has_safety_keywords = any(kw in description_lower for kw in safety_keywords)
        has_danger_keywords = any(kw in description_lower for kw in danger_keywords)

        if has_safety_keywords:
            score += 0.1
        if has_danger_keywords:
            score -= 0.2
            issues.append("Description contains danger-indicating keywords")

        # Check if code includes safety measures
        if request.proposed_code:
            safety_patterns = [r"try:", r"except", r"assert", r"validate", r"check"]
            has_safety_patterns = any(re.search(pattern, request.proposed_code) for pattern in safety_patterns)

            if has_safety_patterns:
                score += 0.1
            else:
                recommendations.append("Consider adding error handling and validation")

        # Clamp score to 0-1
        score = max(0.0, min(1.0, score))

        return score, confidence, issues, recommendations

    def _evaluate_ethics(self, request: ValueAlignmentRequest) -> Tuple[float, float, List[str], List[str]]:
        """Evaluate ethics category."""
        score = 0.6
        confidence = 0.7
        issues = []
        recommendations = []

        # Check for ethical concerns in description
        ethical_concerns = ["deceive", "manipulate", "trick", "exploit", "coerce"]
        description_lower = request.action_description.lower()

        for concern in ethical_concerns:
            if concern in description_lower:
                score -= 0.3
                issues.append(f"Potential ethical concern: '{concern}' in description")
                recommendations.append("Review action for ethical implications")

        # Check user intent
        if request.user_intent:
            positive_intents = ["help", "improve", "fix", "optimize", "create"]
            negative_intents = ["harm", "damage", "break", "destroy", "steal"]

            intent_lower = request.user_intent.lower()
            has_positive = any(intent in intent_lower for intent in positive_intents)
            has_negative = any(intent in intent_lower for intent in negative_intents)

            if has_positive:
                score += 0.2
            if has_negative:
                score -= 0.4
                issues.append("User intent contains negative indicators")

        # Apply ethical frameworks
        framework_scores = []
        for framework_name, framework in self.ethical_frameworks.items():
            framework_score = self._apply_ethical_framework(framework, request)
            weighted_score = framework_score * framework["weight"]
            framework_scores.append(weighted_score)

        if framework_scores:
            avg_framework_score = sum(framework_scores) / len(framework_scores)
            score = (score + avg_framework_score) / 2

        # Clamp score to 0-1
        score = max(0.0, min(1.0, score))

        return score, confidence, issues, recommendations

    def _evaluate_legal(self, request: ValueAlignmentRequest) -> Tuple[float, float, List[str], List[str]]:
        """Evaluate legal category."""
        score = 0.8  # Assume compliance unless evidence otherwise
        confidence = 0.6  # Legal evaluation is complex
        issues = []
        recommendations = []

        # Check for obviously illegal terms
        illegal_indicators = [
            "copyright infringement", "pirate", "crack", "license violation",
            "terms of service violation", "illegal", "prohibited"
        ]

        description_lower = request.action_description.lower()
        for indicator in illegal_indicators:
            if indicator in description_lower:
                score -= 0.5
                issues.append(f"Potential legal issue: '{indicator}' in description")
                recommendations.append("Consult legal review if proceeding")

        # Check context for legal requirements
        if request.context.get("requires_legal_review", False):
            score -= 0.2
            recommendations.append("Legal review recommended for this context")

        # Clamp score to 0-1
        score = max(0.0, min(1.0, score))

        return score, confidence, issues, recommendations

    def _evaluate_privacy(self, request: ValueAlignmentRequest) -> Tuple[float, float, List[str], List[str]]:
        """Evaluate privacy category."""
        score = 0.7
        confidence = 0.75
        issues = []
        recommendations = []

        # Check for privacy-sensitive operations
        privacy_indicators = ["personal data", "user data", "private information", "sensitive data"]
        description_lower = request.action_description.lower()

        has_privacy_indicators = any(indicator in description_lower for indicator in privacy_indicators)

        if has_privacy_indicators:
            score -= 0.2
            issues.append("Action involves privacy-sensitive data")
            recommendations.extend([
                "Ensure data minimization principles are followed",
                "Implement appropriate security measures",
                "Consider privacy impact assessment"
            ])

        # Check code for privacy patterns
        if request.proposed_code:
            privacy_patterns = [
                r"data.*collection", r"user.*data", r"personal.*info",
                r"pii\b", r"gdpr", r"hipaa"
            ]

            has_privacy_code_patterns = any(
                re.search(pattern, request.proposed_code, re.IGNORECASE)
                for pattern in privacy_patterns
            )

            if has_privacy_code_patterns:
                score -= 0.1
                recommendations.append("Review code for privacy compliance")

        # Clamp score to 0-1
        score = max(0.0, min(1.0, score))

        return score, confidence, issues, recommendations

    def _get_action_type_risk(self, action_type: ActionType) -> str:
        """Get risk level for an action type."""
        risk_levels = {
            ActionType.CODE_GENERATION: "low",
            ActionType.CODE_MODIFICATION: "medium",
            ActionType.BUG_FIX: "low",
            ActionType.SECURITY_OPERATION: "high",
            ActionType.DATA_ACCESS: "medium",
            ActionType.SYSTEM_CONFIG_CHANGE: "high",
            ActionType.SELF_MODIFICATION: "high",
            ActionType.PLUGIN_CREATION: "medium",
            ActionType.USER_INTERACTION: "low"
        }
        return risk_levels.get(action_type, "medium")

    def _apply_ethical_framework(self, framework: Dict[str, Any], request: ValueAlignmentRequest) -> float:
        """Apply an ethical framework to the action."""
        # Simplified implementation
        # In practice, this would be more sophisticated
        principles = framework.get("principles", [])

        if not principles:
            return 0.5

        # Check how many principles are likely satisfied
        # This is a placeholder - real implementation would analyze against each principle
        satisfied_principles = len(principles) * 0.7  # Assume 70% satisfaction

        return satisfied_principles / len(principles) if len(principles) > 0 else 0.5

    def _calculate_overall_score(self, category_scores: List[AlignmentScore]) -> float:
        """Calculate overall alignment score."""
        if not category_scores:
            return 0.0

        # Weight safety and ethics more heavily
        weights = {
            ValueCategory.SAFETY: 2.0,
            ValueCategory.ETHICS: 1.5,
            ValueCategory.LEGAL: 1.2,
            ValueCategory.PRIVACY: 1.2,
            ValueCategory.FAIRNESS: 1.0,
            ValueCategory.TRANSPARENCY: 1.0,
            ValueCategory.HUMAN_CONTROL: 1.3,
            ValueCategory.BENEFICENCE: 1.0,
            ValueCategory.NON_MALEFICENCE: 1.5
        }

        weighted_sum = 0.0
        total_weight = 0.0

        for score in category_scores:
            weight = weights.get(score.category, 1.0)
            weighted_sum += score.score * weight * score.confidence
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return weighted_sum / total_weight

    def _check_thresholds(self, overall_score: float, category_scores: List[AlignmentScore], strict_mode: bool) -> Dict[str, Any]:
        """Check if scores meet required thresholds."""
        min_threshold = self.config["min_score_threshold"]
        strict_threshold = self.config["strict_mode_threshold"]
        critical_threshold = self.config["critical_issue_threshold"]

        meets_min = overall_score >= min_threshold
        meets_strict = overall_score >= strict_threshold
        has_critical_issues = any(score.score < critical_threshold for score in category_scores)

        return {
            "meets_min_threshold": meets_min,
            "meets_strict_threshold": meets_strict,
            "has_critical_issues": has_critical_issues,
            "min_threshold": min_threshold,
            "strict_threshold": strict_threshold,
            "critical_threshold": critical_threshold
        }

    def _determine_approval_requirements(self, action_type: ActionType, overall_score: float,
                                        critical_issues: List[str], strict_mode: bool) -> Dict[str, Any]:
        """Determine approval requirements for an action."""
        # Check if action type requires human approval
        requires_human_by_type = action_type.value in [
            "self_modification",
            "system_config_change",
            "security_operation"
        ]

        # Check score-based requirements
        min_threshold = self.config["min_score_threshold"]
        strict_threshold = self.config["strict_mode_threshold"]

        if critical_issues:
            return {
                "required": True,
                "level": "human",
                "reason": "Critical issues detected"
            }

        if strict_mode and overall_score < strict_threshold:
            return {
                "required": True,
                "level": "human",
                "reason": f"Strict mode: score {overall_score:.2f} < {strict_threshold}"
            }

        if overall_score < min_threshold:
            return {
                "required": True,
                "level": "automated",
                "reason": f"Score {overall_score:.2f} below minimum threshold {min_threshold}"
            }

        if requires_human_by_type:
            return {
                "required": True,
                "level": "human",
                "reason": f"Action type {action_type.value} requires human approval"
            }

        return {
            "required": False,
            "level": "none",
            "reason": "Meets all requirements for automatic approval"
        }

    def _generate_recommendations(self, category_scores: List[AlignmentScore],
                                 overall_score: float, passed: bool) -> List[str]:
        """Generate recommendations based on evaluation."""
        recommendations = []

        if not passed:
            recommendations.append("Action requires modification before proceeding")

        # Add recommendations from low-scoring categories
        for score in category_scores:
            if score.score < 0.5:
                recommendations.extend(score.recommendations)

        # Overall score recommendations
        if overall_score < 0.5:
            recommendations.append("Consider revising the action to better align with values")
        elif overall_score < 0.7:
            recommendations.append("Minor improvements could enhance value alignment")

        # Add general recommendations
        recommendations.extend([
            "Document the decision-making process",
            "Maintain audit trail of actions taken",
            "Consider stakeholder impact assessment"
        ])

        return recommendations

    def get_audit_report(self, request_id: str) -> Dict[str, Any]:
        """Generate audit report for a value alignment evaluation."""
        # In a real implementation, this would retrieve from database
        return {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "engine_version": "1.0.0",
            "config_used": self.config,
            "message": "Audit trail would be stored in production"
        }