# backend/agents/qa_agent/tools/coverage_analyzer.py
"""
Enhanced code coverage analysis with detailed reporting
"""
import subprocess
import tempfile
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CoverageAnalyzer:
    """Advanced code coverage analysis"""
    
    async def analyze_coverage(self, code_dir: str, language: str, target: int = 70) -> Dict[str, Any]:
        """
        Analyze code coverage with detailed breakdown
        
        Returns:
            {
                "overall": 85.5,
                "branch": 72.3,
                "function": 90.1,
                "line": 84.2,
                "files": [...],
                "suggestions": [...],
                "trend": {...},
                "thresholds": {...}
            }
        """
        if language == "python":
            return await self._analyze_python_coverage(code_dir, target)
        elif language == "javascript":
            return await self._analyze_javascript_coverage(code_dir, target)
        else:
            return {"error": f"Unsupported language: {language}"}
    
    async def _analyze_python_coverage(self, code_dir: str, target: int) -> Dict[str, Any]:
        """Analyze Python coverage with pytest-cov"""
        results = {
            "overall": 0,
            "branch": 0,
            "function": 0,
            "line": 0,
            "files": [],
            "suggestions": [],
            "trend": {},
            "thresholds": {
                "target": target,
                "minimum_acceptable": 60,
                "excellent": 90
            }
        }
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                # Run coverage with detailed output
                result = subprocess.run(
                    [
                        "pytest", "--cov=.", "--cov-report=json", 
                        "--cov-report=term-missing", "--cov-branch"
                    ],
                    cwd=code_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                # Load coverage report
                coverage_file = Path(code_dir) / "coverage.json"
                if coverage_file.exists():
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                    
                    # Parse overall stats
                    totals = coverage_data.get("totals", {})
                    results["overall"] = totals.get("percent_covered", 0)
                    results["branch"] = totals.get("branch_covered", 0)
                    results["line"] = totals.get("covered_lines", 0) / max(totals.get("total_lines", 1), 1) * 100
                    
                    # File-by-file breakdown
                    for file_path, file_data in coverage_data.get("files", {}).items():
                        file_coverage = file_data.get("summary", {}).get("percent_covered", 0)
                        missed_lines = self._extract_missed_lines(file_data)
                        
                        results["files"].append({
                            "file": file_path,
                            "coverage": file_coverage,
                            "missed_lines": missed_lines,
                            "total_lines": file_data.get("summary", {}).get("total_lines", 0),
                            "covered_lines": file_data.get("summary", {}).get("covered_lines", 0)
                        })
                    
                    # Generate suggestions for low coverage files
                    for file in results["files"]:
                        if file["coverage"] < target:
                            results["suggestions"].append(
                                f"Improve coverage in {file['file']} - currently {file['coverage']:.1f}% "
                                f"(missed lines: {', '.join(map(str, file['missed_lines'][:5]))})"
                            )
                
                # Parse terminal output for function coverage
                if result.stdout:
                    function_match = re.search(r'functions:\s+(\d+)%', result.stdout)
                    if function_match:
                        results["function"] = float(function_match.group(1))
                
                # Add missing tests suggestions
                if results["overall"] < target:
                    results["suggestions"].insert(0, f"Overall coverage {results['overall']:.1f}% is below target {target}%")
                    results["suggestions"].append("Consider adding tests for error handling and edge cases")
                    results["suggestions"].append("Add tests for uncovered functions and branches")
                
            except subprocess.TimeoutExpired:
                results["error"] = "Coverage analysis timed out"
            except Exception as e:
                results["error"] = str(e)
                logger.error(f"Coverage analysis failed: {e}")
        
        return results
    
    def _extract_missed_lines(self, file_data: Dict) -> List[int]:
        """Extract missed line numbers from coverage data"""
        missed = []
        for line_num, hits in file_data.get("executed_lines", {}).items():
            if hits == 0:
                missed.append(line_num)
        return sorted(missed)[:20]  # Limit to 20 lines
    
    async def _analyze_javascript_coverage(self, code_dir: str, target: int) -> Dict[str, Any]:
        """Analyze JavaScript coverage with Jest"""
        results = {
            "overall": 0,
            "branch": 0,
            "function": 0,
            "line": 0,
            "files": [],
            "suggestions": [],
            "trend": {},
            "thresholds": {
                "target": target,
                "minimum_acceptable": 60,
                "excellent": 90
            }
        }
        
        try:
            # Run Jest with coverage
            result = subprocess.run(
                ["npx", "jest", "--coverage", "--coverageReporters=json"],
                cwd=code_dir,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            # Load coverage report
            coverage_file = Path(code_dir) / "coverage" / "coverage-final.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                total_stats = {"lines": 0, "covered": 0, "branches": 0, "branch_covered": 0}
                
                for file_path, file_data in coverage_data.items():
                    file_coverage = file_data.get("coverage", {}).get("lines", {}).get("pct", 0)
                    file_lines = file_data.get("coverage", {}).get("lines", {}).get("total", 0)
                    file_covered = file_data.get("coverage", {}).get("lines", {}).get("covered", 0)
                    
                    total_stats["lines"] += file_lines
                    total_stats["covered"] += file_covered
                    
                    results["files"].append({
                        "file": file_path.replace(code_dir, ""),
                        "coverage": file_coverage,
                        "total_lines": file_lines,
                        "covered_lines": file_covered
                    })
                
                results["overall"] = (total_stats["covered"] / max(total_stats["lines"], 1)) * 100
                
                # Generate suggestions
                for file in results["files"]:
                    if file["coverage"] < target:
                        results["suggestions"].append(
                            f"Improve coverage in {file['file']} - currently {file['coverage']:.1f}%"
                        )
            
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"JavaScript coverage analysis failed: {e}")
        
        return results
    
    async def get_coverage_trend(self, job_id: str, current_coverage: Dict) -> Dict[str, Any]:
        """Get coverage trend compared to previous runs"""
        # In production, this would fetch from a database
        previous_runs = []  # Would come from database
        
        if previous_runs:
            trend = {
                "direction": "improving" if current_coverage["overall"] > previous_runs[-1]["overall"] else "declining",
                "change": current_coverage["overall"] - previous_runs[-1]["overall"],
                "history": previous_runs[-5:]  # Last 5 runs
            }
        else:
            trend = {
                "direction": "new",
                "change": 0,
                "history": [current_coverage]
            }
        
        return trend
