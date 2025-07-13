import subprocess
import json
from pathlib import Path

class SecurityScanner:
    def scan(self, code_dir: str, language: str) -> dict:
        results = {"vulnerabilities": [], "warnings": []}
        
        if language == "python":
            result = subprocess.run(
                ["bandit", "-r", ".", "-f", "json"],
                cwd=code_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout:
                try:
                    report = json.loads(result.stdout)
                    results["vulnerabilities"] = [
                        {
                            "file": issue["filename"],
                            "line": issue["line_number"],
                            "severity": issue["issue_severity"],
                            "confidence": issue["issue_confidence"],
                            "description": issue["issue_text"]
                        }
                        for issue in report["results"]
                    ]
                except json.JSONDecodeError:
                    results["error"] = "Failed to parse security report"
        
        elif language == "javascript":
            result = subprocess.run(
                ["npx", "eslint", ".", "--no-eslintrc", "--config", "eslint-security.json", "-f", "json"],
                cwd=code_dir,
                capture_output=True,
                text=True
            )
            if result.returncode in [0, 1] and result.stdout:
                try:
                    report = json.loads(result.stdout)
                    results["vulnerabilities"] = [
                        {
                            "file": issue["filePath"],
                            "line": issue["line"],
                            "message": issue["messages"][0]["message"],
                            "severity": issue["messages"][0]["severity"]
                        }
                        for issue in report
                    ]
                except (json.JSONDecodeError, KeyError):
                    results["error"] = "Failed to parse security report"
        
        results["score"] = self._calculate_security_score(results)
        return results
    
    def _calculate_security_score(self, results: dict) -> int:
        critical = sum(1 for v in results["vulnerabilities"] if v.get("severity") == "HIGH")
        warnings = len(results.get("warnings", []))
        base_score = 100
        return max(0, base_score - (critical * 20) - (warnings * 5))