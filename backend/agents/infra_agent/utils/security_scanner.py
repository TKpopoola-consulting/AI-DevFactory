# backend/agents/infra_agent/utils/security_scanner.py
"""
Security scanning for infrastructure templates
"""
import re
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class SecurityScanner:
    """Scan infrastructure templates for security issues"""
    
    def __init__(self):
        self.security_rules = self._load_security_rules()
    
    def _load_security_rules(self) -> List[Dict]:
        """Load security rules for scanning"""
        return [
            {
                "id": "SEC001",
                "name": "Public IP exposure",
                "severity": "HIGH",
                "pattern": r'(publicIp|publicIP|public_access).*?true',
                "description": "Resource may be exposed to the internet"
            },
            {
                "id": "SEC002",
                "name": "Missing encryption",
                "severity": "MEDIUM",
                "pattern": r'(encryption|encrypted).*?false',
                "description": "Encryption should be enabled"
            },
            {
                "id": "SEC003",
                "name": "Open firewall rules",
                "severity": "CRITICAL",
                "pattern": r'(0\.0\.0\.0/0|\*)\s*?allow',
                "description": "Firewall allows all traffic"
            },
            {
                "id": "SEC004",
                "name": "Plaintext secrets",
                "severity": "CRITICAL",
                "pattern": r'(password|secret|key).*?=.*?["\'].*?[^$\{]',
                "description": "Hardcoded secrets detected"
            },
            {
                "id": "SEC005",
                "name": "Weak TLS version",
                "severity": "HIGH",
                "pattern": r'(TLS|tls).*?(1\.0|1\.1)',
                "description": "Weak TLS version detected"
            },
            {
                "id": "SEC006",
                "name": "Public storage",
                "severity": "HIGH",
                "pattern": r'(publicAccess|public_read).*?true',
                "description": "Storage publicly accessible"
            }
        ]
    
    async def scan_templates(self, templates: Dict[str, str], cloud_provider: str) -> Dict[str, Any]:
        """Scan templates for security issues"""
        issues = []
        warnings = []
        
        for filename, content in templates.items():
            # Run security rules
            for rule in self.security_rules:
                matches = re.findall(rule["pattern"], content, re.IGNORECASE)
                if matches:
                    issues.append({
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "severity": rule["severity"],
                        "file": filename,
                        "description": rule["description"],
                        "matches": matches[:3]  # Limit matches
                    })
            
            # Cloud-specific checks
            if cloud_provider == "azure":
                issues.extend(self._scan_azure_specific(content, filename))
            elif cloud_provider == "aws":
                issues.extend(self._scan_aws_specific(content, filename))
            elif cloud_provider == "gcp":
                issues.extend(self._scan_gcp_specific(content, filename))
        
        # Calculate security score
        total_score = 100
        for issue in issues:
            if issue["severity"] == "CRITICAL":
                total_score -= 25
            elif issue["severity"] == "HIGH":
                total_score -= 15
            elif issue["severity"] == "MEDIUM":
                total_score -= 5
            elif issue["severity"] == "LOW":
                total_score -= 2
        
        total_score = max(0, total_score)
        
        return {
            "security_score": total_score,
            "grade": self._get_grade(total_score),
            "issues": issues,
            "warnings": warnings,
            "total_issues": len(issues),
            "critical_issues": len([i for i in issues if i["severity"] == "CRITICAL"]),
            "recommendations": self._generate_recommendations(issues),
            "scan_completed": True
        }
    
    def _scan_azure_specific(self, content: str, filename: str) -> List[Dict]:
        """Azure-specific security checks"""
        issues = []
        
        # Check for public network access
        if "publicNetworkAccess: 'Enabled'" in content:
            issues.append({
                "rule_id": "AZURE001",
                "rule_name": "Public network access",
                "severity": "HIGH",
                "file": filename,
                "description": "Public network access should be disabled"
            })
        
        # Check for HTTPS only
        if "httpsOnly: false" in content:
            issues.append({
                "rule_id": "AZURE002",
                "rule_name": "HTTPS not enforced",
                "severity": "HIGH",
                "file": filename,
                "description": "HTTPS should be enforced"
            })
        
        # Check for managed identity
        if "identity:" not in content and "managedIdentity" not in content:
            issues.append({
                "rule_id": "AZURE003",
                "rule_name": "Managed identity missing",
                "severity": "MEDIUM",
                "file": filename,
                "description": "Use managed identities instead of secrets"
            })
        
        return issues
    
    def _scan_aws_specific(self, content: str, filename: str) -> List[Dict]:
        """AWS-specific security checks"""
        issues = []
        
        # Check for public S3 buckets
        if "acl" in content and "public-read" in content:
            issues.append({
                "rule_id": "AWS001",
                "rule_name": "Public S3 bucket",
                "severity": "CRITICAL",
                "file": filename,
                "description": "S3 bucket should not be public"
            })
        
        # Check for IAM best practices
        if "iam" in filename and "policy" in content:
            if "*" in content and "Action" in content:
                issues.append({
                    "rule_id": "AWS002",
                    "rule_name": "Overly permissive IAM",
                    "severity": "HIGH",
                    "file": filename,
                    "description": "Avoid using wildcard in IAM policies"
                })
        
        return issues
    
    def _scan_gcp_specific(self, content: str, filename: str) -> List[Dict]:
        """GCP-specific security checks"""
        issues = []
        
        # Check for public Cloud Run
        if "invoker" in content and "allUsers" in content:
            issues.append({
                "rule_id": "GCP001",
                "rule_name": "Public Cloud Run service",
                "severity": "MEDIUM",
                "file": filename,
                "description": "Consider restricting Cloud Run access"
            })
        
        return issues
    
    def _get_grade(self, score: int) -> str:
        """Get grade based on security score"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate security recommendations"""
        recommendations = set()
        
        for issue in issues:
            if "public" in issue["rule_name"].lower():
                recommendations.add("Restrict public access to resources")
            if "encryption" in issue["rule_name"].lower():
                recommendations.add("Enable encryption at rest and in transit")
            if "secret" in issue["rule_name"].lower():
                recommendations.add("Use secrets manager instead of hardcoded secrets")
            if "firewall" in issue["rule_name"].lower():
                recommendations.add("Implement network security groups with least privilege")
        
        # Add general recommendations
        if len(issues) > 0:
            recommendations.add("Implement infrastructure security best practices")
            recommendations.add("Regularly update and patch infrastructure")
            recommendations.add("Enable monitoring and logging")
        
        return list(recommendations)
    
    def generate_security_report(self, scan_results: Dict) -> str:
        """Generate human-readable security report"""
        report = f"""
SECURITY SCAN REPORT
===================
Score: {scan_results['security_score']}/100
Grade: {scan_results['grade']}
Issues Found: {scan_results['total_issues']}
Critical Issues: {scan_results['critical_issues']}

ISSUES DETAILS:
"""
        for issue in scan_results['issues']:
            report += f"""
[{issue['severity']}] {issue['rule_name']}
  File: {issue['file']}
  Description: {issue['description']}
"""
        
        report += "\nRECOMMENDATIONS:\n"
        for rec in scan_results['recommendations']:
            report += f"  • {rec}\n"
        
        return report
