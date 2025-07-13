import os
import tempfile
import subprocess
import requests
from pathlib import Path
from tools.security_scanner import SecurityScanner
from tools.test_runner import TestRunner
from tools.performance_tester import PerformanceTester
from tools.report_generator import ReportGenerator

class QAAgent:
    def __init__(self):
        self.tools = {
            "security": SecurityScanner(),
            "testing": TestRunner(),
            "performance": PerformanceTester(),
            "report": ReportGenerator()
        }
    
    def analyze(self, code_url: str, language: str, framework: str, test_coverage: int = 70) -> dict:
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Download and extract code
            self._download_code(code_url, tmp_dir)
            
            # Run analysis tools
            results = {
                "security": self.tools["security"].scan(tmp_dir, language),
                "tests": self.tools["testing"].run_tests(tmp_dir, language, framework),
                "performance": self.tools["performance"].test_performance(tmp_dir, language),
                "coverage": self._measure_coverage(tmp_dir, language, test_coverage)
            }
            
            # Generate report
            report = self.tools["report"].generate_report(results)
            
            return {
                "status": "completed",
                "results": results,
                "report": report
            }
    
    def _download_code(self, url: str, dest_dir: str):
        response = requests.get(url)
        zip_path = Path(dest_dir) / "code.zip"
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Unzip code
        subprocess.run(["unzip", "-q", "code.zip"], cwd=dest_dir, check=True)
        zip_path.unlink()
    
    def _measure_coverage(self, code_dir: str, language: str, target: int) -> dict:
        coverage = {"statement": 0, "branch": 0, "target": target}
        
        if language == "python":
            result = subprocess.run(
                ["pytest", "--cov", ".", "--cov-report", "term"],
                cwd=code_dir,
                capture_output=True,
                text=True
            )
            # Parse coverage from output
            if "TOTAL" in result.stdout:
                coverage_line = [line for line in result.stdout.splitlines() if "TOTAL" in line][0]
                parts = coverage_line.split()
                coverage["statement"] = int(parts[3].replace('%', ''))
                coverage["branch"] = int(parts[6].replace('%', ''))
        
        elif language == "javascript":
            result = subprocess.run(
                ["npx", "jest", "--coverage"],
                cwd=code_dir,
                capture_output=True,
                text=True
            )
            # Parse coverage from output
            if "All files" in result.stdout:
                coverage_line = [line for line in result.stdout.splitlines() if "All files" in line][0]
                parts = coverage_line.split('|')
                coverage["statement"] = float(parts[1].strip())
                coverage["branch"] = float(parts[2].strip())
        
        coverage["passed"] = coverage["statement"] >= target
        return coverage