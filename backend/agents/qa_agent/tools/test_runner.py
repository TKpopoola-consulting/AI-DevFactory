import subprocess
import json

class TestRunner:
    def run_tests(self, code_dir: str, language: str, framework: str) -> dict:
        results = {"passed": 0, "failed": 0, "errors": 0, "details": []}
        
        if language == "python" and framework == "pytest":
            result = subprocess.run(
                ["pytest", "--json-report"],
                cwd=code_dir,
                capture_output=True,
                text=True
            )
            try:
                with open(Path(code_dir) / ".report.json", "r") as f:
                    report = json.load(f)
                    results["passed"] = report["summary"]["passed"]
                    results["failed"] = report["summary"]["failed"]
                    results["errors"] = report["summary"]["error"]
                    results["details"] = [
                        {
                            "nodeid": test["nodeid"],
                            "outcome": test["outcome"],
                            "duration": test["duration"]
                        }
                        for test in report["tests"]
                    ]
            except (FileNotFoundError, json.JSONDecodeError):
                results["error"] = "Failed to load test report"
        
        elif language == "javascript" and framework == "jest":
            result = subprocess.run(
                ["npx", "jest", "--json", "--outputFile=test-results.json"],
                cwd=code_dir,
                capture_output=True,
                text=True
            )
            try:
                with open(Path(code_dir) / "test-results.json", "r") as f:
                    report = json.load(f)
                    results["passed"] = report["numPassedTests"]
                    results["failed"] = report["numFailedTests"]
                    results["errors"] = report["numRuntimeErrorTestSuites"]
                    results["details"] = [
                        {
                            "name": test["name"],
                            "status": test["status"],
                            "duration": test["duration"]
                        }
                        for test in report["testResults"][0]["assertionResults"]
                    ]
            except (FileNotFoundError, json.JSONDecodeError):
                results["error"] = "Failed to load test report"
        
        results["success"] = results["failed"] == 0 and results["errors"] == 0
        return results