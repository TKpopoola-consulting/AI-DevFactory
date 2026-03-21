# backend/agents/qa_agent/agent_logic.py (Updated)
"""
Complete QA Agent with all testing capabilities
"""
import os
import tempfile
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any

from tools.security_scanner import SecurityScanner
from tools.test_runner import TestRunner
from tools.performance_tester import PerformanceTester
from tools.report_generator import ReportGenerator
from tools.test_generator import TestGenerator
from tools.coverage_analyzer import CoverageAnalyzer
from tools.continuous_tester import ContinuousTester
from tools.data_generator import TestDataGenerator
from tools.benchmark_tracker import BenchmarkTracker


class QAAgent:
    """Complete QA agent with comprehensive testing capabilities"""
    
    def __init__(self):
        self.tools = {
            "security": SecurityScanner(),
            "testing": TestRunner(),
            "performance": PerformanceTester(),
            "report": ReportGenerator(),
            "test_generator": TestGenerator(),
            "coverage": CoverageAnalyzer(),
            "continuous": ContinuousTester(),
            "data_generator": TestDataGenerator(),
            "benchmark": BenchmarkTracker()
        }
        
    async def analyze(self, code_url: str, language: str, framework: str, test_coverage: int = 70) -> Dict:
        """Complete analysis of code"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Download and extract code
            await self._download_code(code_url, tmp_dir)
            
            # Generate tests if missing
            tests = await self._generate_missing_tests(tmp_dir, language)
            
            # Run analysis tools
            results = {
                "security": await self.tools["security"].scan(tmp_dir, language),
                "tests": await self.tools["testing"].run_tests(tmp_dir, language, framework),
                "performance": await self.tools["performance"].test_performance(tmp_dir, language),
                "coverage": await self.tools["coverage"].analyze_coverage(tmp_dir, language, test_coverage),
                "generated_tests": tests,
                "test_data": await self._generate_test_data(tmp_dir)
            }
            
            # Compare with baseline
            benchmark = await self.tools["benchmark"].compare_to_baseline(results["performance"])
            
            # Generate report
            report = await self.tools["report"].generate_report(results)
            
            return {
                "status": "completed",
                "results": results,
                "benchmark": benchmark,
                "report": report,
                "suggestions": await self._generate_suggestions(results)
            }
    
    async def _generate_missing_tests(self, code_dir: str, language: str) -> Dict:
        """Generate missing test templates"""
        # Parse code structure
        structure = await self._parse_code_structure(code_dir, language)
        
        # Generate tests
        tests = await self.tools["test_generator"].generate_test_templates(structure, language)
        
        # Save generated tests
        for test_file, content in tests.items():
            test_path = Path(code_dir) / test_file
            test_path.parent.mkdir(parents=True, exist_ok=True)
            test_path.write_text(content)
        
        return tests
    
    async def _parse_code_structure(self, code_dir: str, language: str) -> Dict:
        """Parse code structure for test generation"""
        structure = {"files": {}, "endpoints": []}
        
        if language == "python":
            structure = await self._parse_python_structure(code_dir)
        elif language == "javascript":
            structure = await self._parse_javascript_structure(code_dir)
        
        return structure
    
    async def _parse_python_structure(self, code_dir: str) -> Dict:
        """Parse Python code structure"""
        structure = {"files": {}, "endpoints": []}
        
        for py_file in Path(code_dir).rglob("*.py"):
            if "test" not in py_file.name:
                with open(py_file, 'r') as f:
                    structure["files"][str(py_file)] = f.read()
        
        # Look for FastAPI/Django endpoints
        # This is simplified - in production, use AST parsing
        for file_path, content in structure["files"].items():
            if "app.get" in content or "app.post" in content:
                # Extract endpoints (simplified)
                import re
                endpoints = re.findall(r'@app\.(get|post|put|delete)\(["\']([^"\']+)["\']', content)
                for method, path in endpoints:
                    structure["endpoints"].append({
                        "method": method,
                        "path": path,
                        "name": path.replace("/", "_")
                    })
        
        return structure
    
    async def _parse_javascript_structure(self, code_dir: str) -> Dict:
        """Parse JavaScript code structure"""
        structure = {"files": {}, "endpoints": []}
        
        for js_file in Path(code_dir).rglob("*.js"):
            if "test" not in js_file.name and "node_modules" not in str(js_file):
                with open(js_file, 'r') as f:
                    structure["files"][str(js_file)] = f.read()
        
        return structure
    
    async def _generate_test_data(self, code_dir: str) -> Dict:
        """Generate test data from schemas"""
        # Look for schema files
        schema = await self._extract_schema(code_dir)
        
        if schema:
            return await self.tools["data_generator"].generate_test_data(schema)
        
        return {}
    
    async def _extract_schema(self, code_dir: str) -> Dict:
        """Extract data schema from code"""
        schema = {}
        
        # Look for Pydantic models in Python
        for py_file in Path(code_dir).rglob("*.py"):
            with open(py_file, 'r') as f:
                content = f.read()
                if "class.*BaseModel" in content:
                    # Parse Pydantic model (simplified)
                    import re
                    models = re.findall(r'class (\w+)\(.*BaseModel\):', content)
                    for model in models:
                        fields = re.findall(r'(\w+):\s*(\w+)', content)
                        schema[model] = {field: type_ for field, type_ in fields}
        
        return schema
    
    async def _download_code(self, url: str, dest_dir: str):
        """Download code from URL"""
        response = requests.get(url)
        zip_path = Path(dest_dir) / "code.zip"
        
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Unzip code
        subprocess.run(["unzip", "-q", "code.zip"], cwd=dest_dir, check=True)
        zip_path.unlink()
    
    async def _generate_suggestions(self, results: Dict) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Coverage suggestions
        if results["coverage"].get("overall", 0) < 70:
            suggestions.append(f"Improve test coverage (current: {results['coverage']['overall']:.1f}%)")
            for file in results["coverage"].get("files", [])[:3]:
                if file["coverage"] < 50:
                    suggestions.append(f"  - Add tests for {file['file']} (coverage: {file['coverage']:.1f}%)")
        
        # Performance suggestions
        if results["performance"].get("error_rate", 0) > 1:
            suggestions.append(f"High error rate detected: {results['performance']['error_rate']:.1f}%")
        
        # Security suggestions
        if results["security"].get("score", 100) < 80:
            suggestions.append(f"Security score low: {results['security']['score']}/100")
            for issue in results["security"].get("vulnerabilities", [])[:3]:
                suggestions.append(f"  - Fix: {issue.get('description', 'Security issue')}")
        
        return suggestions
    
    async def start_watch_mode(self, job_id: str, code_dir: str, language: str) -> Dict:
        """Start continuous testing"""
        return await self.tools["continuous"].watch_and_test(job_id, code_dir, language)
    
    async def stop_watch_mode(self, job_id: str) -> Dict:
        """Stop continuous testing"""
        return await self.tools["continuous"].stop_watching(job_id)
