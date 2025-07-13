import subprocess
import json
import time
from pathlib import Path

class PerformanceTester:
    def test_performance(self, code_dir: str, language: str) -> dict:
        results = {"latency": 0, "throughput": 0, "error_rate": 0}
        
        # Start the application
        process = self._start_application(code_dir, language)
        time.sleep(5)  # Wait for app to start
        
        try:
            # Run performance test
            if language == "python":
                result = subprocess.run(
                    ["locust", "-f", "perf_test.py", "--headless", "-u", "100", "-r", "10", "-t", "1m", "--json"],
                    cwd=code_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.stdout:
                    report = json.loads(result.stdout)
                    results = self._parse_locust_report(report)
            
            elif language == "javascript":
                result = subprocess.run(
                    ["npx", "artillery", "run", "perf-test.yml", "--output", "perf-report.json"],
                    cwd=code_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                try:
                    with open(Path(code_dir) / "perf-report.json", "r") as f:
                        report = json.load(f)
                        results = self._parse_artillery_report(report)
                except FileNotFoundError:
                    results["error"] = "Performance report not found"
        
        finally:
            # Stop the application
            process.terminate()
        
        return results
    
    def _start_application(self, code_dir: str, language: str):
        if language == "python":
            return subprocess.Popen(
                ["uvicorn", "main:app", "--port", "8000"],
                cwd=code_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        elif language == "javascript":
            return subprocess.Popen(
                ["npm", "start"],
                cwd=code_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    
    def _parse_locust_report(self, report: dict) -> dict:
        return {
            "latency": report["stats"][0]["avg_response_time"],
            "throughput": report["stats"][0]["total_rps"],
            "error_rate": report["stats"][0]["fail_ratio"] * 100
        }
    
    def _parse_artillery_report(self, report: dict) -> dict:
        return {
            "latency": report["aggregate"]["latency"]["median"],
            "throughput": report["aggregate"]["rps"]["mean"],
            "error_rate": report["aggregate"]["codes"]["500"] / report["aggregate"]["requests"] * 100
        }