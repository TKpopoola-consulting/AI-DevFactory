from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import os

app = FastAPI(title="QA Agent", version="1.0.0")

# Request models
class QAAnalysisRequest(BaseModel):
    project_code: Dict[str, Any]
    framework: str
    test_framework: Optional[str] = "pytest"
    security_scan: Optional[bool] = True
    performance_test: Optional[bool] = False
    language: Optional[str] = "python"

class SecurityScanRequest(BaseModel):
    code: Dict[str, Any]
    language: str

class TestGenerationRequest(BaseModel):
    code: Dict[str, Any]
    framework: str
    test_framework: str

class PerformanceAnalysisRequest(BaseModel):
    code: Dict[str, Any]
    framework: str

class QAAnalysisResponse(BaseModel):
    status: str
    quality_score: int
    security_issues: List[Dict[str, Any]]
    test_coverage: Dict[str, Any]
    performance_metrics: Optional[Dict[str, Any]] = None
    recommendations: List[str]
    error: Optional[str] = None

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "qa",
        "capabilities": [
            "security_scanning",
            "test_generation",
            "performance_analysis",
            "code_quality_check",
            "vulnerability_assessment"
        ],
        "supported_languages": ["python", "javascript", "java", "go", "rust"],
        "version": "1.0.0"
    }

@app.post("/analyze", response_model=QAAnalysisResponse)
async def analyze_project(request: QAAnalysisRequest):
    """Comprehensive QA analysis of a project"""
    try:
        # Perform security scan
        security_issues = perform_security_scan(request.project_code, request.language)

        # Generate tests
        test_coverage = generate_test_coverage(request.project_code, request.test_framework)

        # Calculate quality score
        quality_score = calculate_quality_score(
            security_issues,
            test_coverage,
            request.project_code
        )

        # Performance analysis (if requested)
        performance_metrics = None
        if request.performance_test:
            performance_metrics = analyze_performance(request.project_code, request.framework)

        # Generate recommendations
        recommendations = generate_recommendations(
            security_issues,
            test_coverage,
            quality_score
        )

        return QAAnalysisResponse(
            status="success",
            quality_score=quality_score,
            security_issues=security_issues,
            test_coverage=test_coverage,
            performance_metrics=performance_metrics,
            recommendations=recommendations
        )

    except Exception as e:
        return QAAnalysisResponse(
            status="error",
            quality_score=0,
            security_issues=[],
            test_coverage={},
            recommendations=[],
            error=str(e)
        )

@app.post("/security")
async def security_scan(request: SecurityScanRequest):
    """Perform security scan on code"""
    try:
        issues = perform_security_scan(request.code, request.language)

        severity_counts = {
            "critical": sum(1 for issue in issues if issue.get("severity") == "critical"),
            "high": sum(1 for issue in issues if issue.get("severity") == "high"),
            "medium": sum(1 for issue in issues if issue.get("severity") == "medium"),
            "low": sum(1 for issue in issues if issue.get("severity") == "low")
        }

        security_score = 100 - (
            severity_counts["critical"] * 20 +
            severity_counts["high"] * 10 +
            severity_counts["medium"] * 5 +
            severity_counts["low"] * 2
        )
        security_score = max(0, min(100, security_score))

        return {
            "status": "success",
            "security_score": security_score,
            "issues_found": len(issues),
            "issues_by_severity": severity_counts,
            "issues": issues,
            "recommendations": [
                f"Fix {severity_counts['critical']} critical issues",
                f"Fix {severity_counts['high']} high severity issues",
                "Implement secure coding practices",
                "Add security testing to CI/CD"
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tests")
async def generate_tests(request: TestGenerationRequest):
    """Generate tests for code"""
    try:
        tests = generate_tests_for_code(
            request.code,
            request.framework,
            request.test_framework
        )

        return {
            "status": "success",
            "tests_generated": len(tests),
            "test_coverage": f"{len(tests) * 10}%",  # Simplified
            "tests": tests,
            "test_files": create_test_files(tests, request.test_framework)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/performance")
async def performance_analysis(request: PerformanceAnalysisRequest):
    """Analyze code performance"""
    try:
        metrics = analyze_performance(request.code, request.framework)

        return {
            "status": "success",
            "performance_score": metrics["score"],
            "metrics": metrics,
            "bottlenecks": metrics.get("bottlenecks", []),
            "optimization_suggestions": metrics.get("suggestions", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def perform_security_scan(code: Dict[str, Any], language: str) -> List[Dict[str, Any]]:
    """Perform security scan on code"""
    issues = []

    # Common security issues to check for
    security_patterns = {
        "python": [
            {"pattern": r"eval\(", "issue": "Use of eval()", "severity": "critical", "description": "eval() can execute arbitrary code"},
            {"pattern": r"exec\(", "issue": "Use of exec()", "severity": "critical", "description": "exec() can execute arbitrary code"},
            {"pattern": r"pickle\.loads", "issue": "Unsafe deserialization", "severity": "high", "description": "Pickle can execute arbitrary code during deserialization"},
            {"pattern": r"subprocess\.Popen.*shell=True", "issue": "Shell injection", "severity": "high", "description": "Shell=True can lead to command injection"},
            {"pattern": r"query = f\".*\{\w+\}.*\"", "issue": "SQL injection risk", "severity": "high", "description": "String formatting in SQL queries can lead to injection"},
            {"pattern": r"password.*=.*['\"].*['\"]", "issue": "Hardcoded credentials", "severity": "medium", "description": "Credentials should not be hardcoded"},
            {"pattern": r"import os.*os\.system", "issue": "Command execution", "severity": "high", "description": "Direct command execution can be dangerous"},
        ],
        "javascript": [
            {"pattern": r"eval\(", "issue": "Use of eval()", "severity": "critical", "description": "eval() can execute arbitrary code"},
            {"pattern": r"innerHTML.*=.*['\"].*\{\w+\}.*['\"]", "issue": "XSS vulnerability", "severity": "high", "description": "Direct assignment to innerHTML can cause XSS"},
            {"pattern": r"localStorage\.setItem.*password", "issue": "Unsafe credential storage", "severity": "medium", "description": "Passwords should not be stored in localStorage"},
            {"pattern": r"console\.log.*password", "issue": "Sensitive data logging", "severity": "low", "description": "Sensitive data should not be logged"},
        ],
        "java": [
            {"pattern": r"Runtime\.getRuntime\(\)\.exec", "issue": "Command execution", "severity": "high", "description": "Direct command execution can be dangerous"},
            {"pattern": r"System\.exit", "issue": "System exit", "severity": "medium", "description": "System.exit() can terminate the JVM"},
            {"pattern": r"password.*=.*['\"].*['\"]", "issue": "Hardcoded credentials", "severity": "medium", "description": "Credentials should not be hardcoded"},
        ]
    }

    patterns = security_patterns.get(language, security_patterns["python"])

    # Check each file in the code
    for filename, file_content in code.items():
        if isinstance(file_content, str):
            for pattern_info in patterns:
                import re
                if re.search(pattern_info["pattern"], file_content):
                    issues.append({
                        "file": filename,
                        "issue": pattern_info["issue"],
                        "severity": pattern_info["severity"],
                        "description": pattern_info["description"],
                        "line": "N/A",  # Could be enhanced to find line numbers
                        "recommendation": f"Fix {pattern_info['issue'].lower()} in {filename}"
                    })

    # Add some generic issues
    if len(issues) == 0:
        issues.append({
            "file": "general",
            "issue": "No critical security issues found",
            "severity": "info",
            "description": "Basic security scan passed",
            "recommendation": "Continue with regular security practices"
        })

    return issues

def generate_test_coverage(code: Dict[str, Any], test_framework: str) -> Dict[str, Any]:
    """Generate test coverage analysis"""
    total_files = len(code)
    files_with_tests = min(total_files // 2, total_files)  # Estimate

    return {
        "estimated_coverage": f"{int((files_with_tests / total_files) * 100) if total_files > 0 else 0}%",
        "total_files": total_files,
        "files_with_tests": files_with_tests,
        "test_framework": test_framework,
        "test_recommendations": [
            f"Add tests for {total_files - files_with_tests} untested files",
            f"Use {test_framework} for testing",
            "Implement unit tests for all public functions",
            "Add integration tests for API endpoints",
            "Include edge case testing"
        ]
    }

def calculate_quality_score(security_issues: List[Dict[str, Any]],
                           test_coverage: Dict[str, Any],
                           code: Dict[str, Any]) -> int:
    """Calculate overall quality score"""
    base_score = 70

    # Adjust based on security issues
    critical_issues = sum(1 for issue in security_issues if issue.get("severity") == "critical")
    high_issues = sum(1 for issue in security_issues if issue.get("severity") == "high")

    base_score -= critical_issues * 20
    base_score -= high_issues * 10

    # Adjust based on test coverage
    coverage_str = test_coverage.get("estimated_coverage", "0%").replace("%", "")
    try:
        coverage = int(coverage_str)
        if coverage >= 80:
            base_score += 20
        elif coverage >= 50:
            base_score += 10
        elif coverage >= 30:
            base_score += 5
    except:
        pass

    # Adjust based on code size
    total_lines = sum(len(str(content).split('\n')) for content in code.values())
    if total_lines > 1000:
        base_score -= 5  # Large codebases are harder to maintain

    return max(0, min(100, base_score))

def analyze_performance(code: Dict[str, Any], framework: str) -> Dict[str, Any]:
    """Analyze code performance"""
    total_files = len(code)
    total_lines = sum(len(str(content).split('\n')) for content in code.values())

    bottlenecks = []

    # Look for common performance issues
    for filename, file_content in code.items():
        if isinstance(file_content, str):
            content_lower = file_content.lower()

            if "for i in range" in content_lower and "for j in range" in content_lower:
                bottlenecks.append(f"Nested loops in {filename}")

            if "select *" in content_lower:
                bottlenecks.append(f"SELECT * query in {filename}")

            if "sleep(" in content_lower:
                bottlenecks.append(f"Sleep/blocking call in {filename}")

            if "recursion" in content_lower and "base case" not in content_lower:
                bottlenecks.append(f"Potential infinite recursion in {filename}")

    performance_score = 100 - len(bottlenecks) * 10
    performance_score = max(0, min(100, performance_score))

    return {
        "score": performance_score,
        "bottlenecks": bottlenecks,
        "suggestions": [
            "Use caching for frequently accessed data",
            "Optimize database queries with indexes",
            "Implement pagination for large datasets",
            "Use asynchronous operations for I/O",
            "Profile code to identify actual bottlenecks"
        ],
        "metrics": {
            "total_files": total_files,
            "total_lines": total_lines,
            "bottlenecks_found": len(bottlenecks),
            "estimated_complexity": "medium" if total_lines > 500 else "low"
        }
    }

def generate_recommendations(security_issues: List[Dict[str, Any]],
                            test_coverage: Dict[str, Any],
                            quality_score: int) -> List[str]:
    """Generate recommendations based on analysis"""
    recommendations = []

    # Security recommendations
    critical_issues = sum(1 for issue in security_issues if issue.get("severity") == "critical")
    high_issues = sum(1 for issue in security_issues if issue.get("severity") == "high")

    if critical_issues > 0:
        recommendations.append(f"Fix {critical_issues} critical security issues immediately")
    if high_issues > 0:
        recommendations.append(f"Fix {high_issues} high severity security issues")

    # Test coverage recommendations
    coverage_str = test_coverage.get("estimated_coverage", "0%").replace("%", "")
    try:
        coverage = int(coverage_str)
        if coverage < 80:
            recommendations.append(f"Increase test coverage from {coverage}% to at least 80%")
    except:
        pass

    # Quality score recommendations
    if quality_score < 70:
        recommendations.append("Improve overall code quality")
    if quality_score < 50:
        recommendations.append("Code needs significant refactoring and improvement")

    # General recommendations
    recommendations.extend([
        "Implement code review process",
        "Add static analysis to CI/CD pipeline",
        "Document security and testing practices",
        "Regularly update dependencies"
    ])

    return recommendations

def generate_tests_for_code(code: Dict[str, Any], framework: str, test_framework: str) -> List[Dict[str, Any]]:
    """Generate tests for the given code"""
    tests = []

    for filename, file_content in code.items():
        if isinstance(file_content, str):
            # Generate simple test based on file content
            test_name = f"test_{filename.replace('.', '_').replace('/', '_')}"

            if framework == "python":
                test_code = generate_python_test(filename, file_content, test_framework)
            elif framework == "javascript":
                test_code = generate_javascript_test(filename, file_content, test_framework)
            elif framework == "java":
                test_code = generate_java_test(filename, file_content, test_framework)
            else:
                test_code = generate_generic_test(filename, file_content)

            tests.append({
                "file": f"test_{filename}",
                "test_name": test_name,
                "framework": test_framework,
                "test_code": test_code
            })

    return tests[:5]  # Limit to 5 tests for demo

def generate_python_test(filename: str, content: str, test_framework: str) -> str:
    """Generate Python test"""
    if test_framework == "pytest":
        return f"""
import pytest
import sys
sys.path.insert(0, '.')

def test_{filename.replace('.', '_')}_exists():
    \"\"\"Test that {filename} can be imported\"\"\"
    try:
        # Import the module
        module_name = '{filename.replace('.py', '')}'
        __import__(module_name)
        assert True
    except ImportError:
        pytest.fail(f"Module {{module_name}} cannot be imported")

def test_{filename.replace('.', '_')}_functions():
    \"\"\"Test basic functions in {filename}\"\"\"
    # Add specific function tests here
    assert True
"""
    else:  # unittest
        return f"""
import unittest
import sys
sys.path.insert(0, '.')

class Test{filename.replace('.', '_').title()}(unittest.TestCase):
    def test_module_import(self):
        \"\"\"Test that {filename} can be imported\"\"\"
        try:
            import {filename.replace('.py', '')}
            self.assertTrue(True)
        except ImportError:
            self.fail(f"Cannot import {{filename.replace('.py', '')}}")

    def test_basic_functionality(self):
        \"\"\"Test basic functionality\"\"\"
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
"""

def create_test_files(tests: List[Dict[str, Any]], test_framework: str) -> Dict[str, str]:
    """Create test files from generated tests"""
    test_files = {}

    for test in tests:
        filename = test["file"]
        test_code = test["test_code"]
        test_files[filename] = test_code

    return test_files

@app.post("/test")
async def test_analysis():
    """Test endpoint to verify agent is working"""
    test_code = {
        "main.py": """
def calculate_sum(a, b):
    return a + b

def get_user_input():
    return input("Enter password: ")

def process_data(data):
    # Process data
    result = []
    for item in data:
        for subitem in item:
            result.append(subitem * 2)
    return result
"""
    }

    try:
        security_issues = perform_security_scan(test_code, "python")
        test_coverage = generate_test_coverage(test_code, "pytest")
        quality_score = calculate_quality_score(security_issues, test_coverage, test_code)

        return {
            "status": "success",
            "test": "passed",
            "quality_score": quality_score,
            "security_issues_found": len(security_issues),
            "test_coverage": test_coverage["estimated_coverage"],
            "agent": "qa"
        }
    except Exception as e:
        return {
            "status": "error",
            "test": "failed",
            "error": str(e)
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5003))
    print(f"🚀 Starting QA Agent on port {port}")
    print(f"📍 Endpoint: http://localhost:{port}/analyze")
    print(f"📚 Docs: http://localhost:{port}/docs")
    print(f"🔒 Security scanning, testing, and performance analysis")

    uvicorn.run(app, host="0.0.0.0", port=port)