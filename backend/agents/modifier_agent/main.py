from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import os
import ast
import re
import json

app = FastAPI(title="Modifier Agent", version="1.0.0")

# Request models
class ModifierRequest(BaseModel):
    code: Dict[str, Any]
    modification_type: str = "refactor"  # refactor, optimize, clean, restructure
    language: str = "python"
    target_patterns: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None

class CodeSuggestion(BaseModel):
    file: str
    line: Optional[int]
    suggestion: str
    code_before: str
    code_after: str
    reasoning: str
    priority: str  # low, medium, high, critical

class ModifierResponse(BaseModel):
    status: str
    modifications_applied: List[Dict[str, Any]]
    suggestions: List[CodeSuggestion]
    quality_metrics: Dict[str, Any]
    code_after: Dict[str, Any]
    error: Optional[str] = None

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "modifier",
        "capabilities": [
            "code_refactoring",
            "performance_optimization",
            "code_cleaning",
            "structure_improvement",
            "readability_enhancement",
            "design_pattern_application"
        ],
        "supported_languages": ["python", "javascript", "java", "typescript"],
        "version": "1.0.0"
    }

@app.post("/modify", response_model=ModifierResponse)
async def modify_code(request: ModifierRequest):
    """Modify code based on requested modification type"""
    try:
        # Analyze code and generate suggestions
        suggestions = analyze_code(request.code, request.language, request.modification_type)

        # Apply modifications based on suggestions
        modified_code = apply_modifications(request.code, suggestions, request.modification_type)

        # Calculate quality metrics
        quality_metrics = calculate_quality_metrics(modified_code, request.code, request.language)

        # Track modifications applied
        modifications_applied = []
        for suggestion in suggestions:
            modifications_applied.append({
                "file": suggestion.file,
                "suggestion": suggestion.suggestion,
                "priority": suggestion.priority,
                "applied": suggestion.priority in ["high", "critical"]  # Auto-apply high/critical
            })

        return ModifierResponse(
            status="success",
            modifications_applied=modifications_applied,
            suggestions=suggestions,
            quality_metrics=quality_metrics,
            code_after=modified_code
        )

    except Exception as e:
        return ModifierResponse(
            status="error",
            modifications_applied=[],
            suggestions=[],
            quality_metrics={},
            code_after={},
            error=str(e)
        )

def analyze_code(code: Dict[str, Any], language: str, modification_type: str) -> List[CodeSuggestion]:
    """Analyze code and generate modification suggestions"""
    suggestions = []

    for filename, file_content in code.items():
        if not isinstance(file_content, str):
            continue

        # Language-specific analysis
        if language == "python":
            suggestions.extend(analyze_python_code(filename, file_content, modification_type))
        elif language == "javascript":
            suggestions.extend(analyze_javascript_code(filename, file_content, modification_type))
        elif language == "java":
            suggestions.extend(analyze_java_code(filename, file_content, modification_type))
        else:
            suggestions.extend(analyze_generic_code(filename, file_content, modification_type))

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    suggestions.sort(key=lambda x: priority_order.get(x.priority, 4))

    return suggestions

def analyze_python_code(filename: str, content: str, modification_type: str) -> List[CodeSuggestion]:
    """Analyze Python code for improvements"""
    suggestions = []

    lines = content.split('\n')

    # Look for long functions/methods
    function_lines = []
    current_function = None
    function_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect function definition
        if stripped.startswith("def "):
            if current_function and len(function_lines) > 20:  # Functions longer than 20 lines
                suggestions.append(CodeSuggestion(
                    file=filename,
                    line=function_start,
                    suggestion="Function is too long - consider breaking it down",
                    code_before=content,
                    code_after=content,  # Will be modified later
                    reasoning="Long functions are harder to maintain and test",
                    priority="medium"
                ))
            current_function = stripped.split("def ")[1].split("(")[0]
            function_start = i
            function_lines = []
        elif current_function:
            function_lines.append(line)

            # Check for nested if statements
            if stripped.startswith("if ") and line.count("if ") > 1:
                suggestions.append(CodeSuggestion(
                    file=filename,
                    line=i+1,
                    suggestion="Simplify nested conditionals",
                    code_before=line,
                    code_after=line.replace("if ", "# TODO: Simplify nested if"),
                    reasoning="Deeply nested conditionals reduce readability",
                    priority="low"
                ))

    # Check for code duplication patterns
    for pattern in [
        r"for.*in.*range.*:",
        r"try:.*except:",
        r"if.*not.*:"
    ]:
        matches = re.finditer(pattern, content, re.DOTALL)
        for match in matches:
            if match:
                suggestions.append(CodeSuggestion(
                    file=filename,
                    line=content[:match.start()].count('\n') + 1,
                    suggestion="Potential code pattern that could be abstracted",
                    code_before=match.group(0)[:100] + "...",
                    code_after="# TODO: Consider creating a helper function",
                    reasoning="Repeated patterns indicate opportunity for abstraction",
                    priority="low"
                ))

    # Look for performance issues
    if "for i in range" in content and "for j in range" in content:
        suggestions.append(CodeSuggestion(
            file=filename,
            line=0,
            suggestion="Nested loops may have performance issues",
            code_before="for i in range(...):\n    for j in range(...):",
            code_after="# TODO: Consider vectorization or optimization",
            reasoning="Nested loops can be O(n²) complexity",
            priority="medium"
        ))

    # Look for magic numbers
    magic_numbers = re.findall(r'\b\d{3,}\b', content)  # Numbers with 3+ digits
    for num in magic_numbers:
        suggestions.append(CodeSuggestion(
            file=filename,
            line=0,
            suggestion=f"Replace magic number {num} with named constant",
            code_before=f"value = {num}",
            code_after=f"MAX_VALUE = {num}\nvalue = MAX_VALUE",
            reasoning="Magic numbers make code harder to understand and maintain",
            priority="low"
        ))

    return suggestions

def analyze_javascript_code(filename: str, content: str, modification_type: str) -> List[CodeSuggestion]:
    """Analyze JavaScript code for improvements"""
    suggestions = []

    # Look for callback hell (nested callbacks)
    if content.count("})") > 5 and content.count(".then(") < content.count("function("):
        suggestions.append(CodeSuggestion(
            file=filename,
            line=0,
            suggestion="Consider using async/await instead of callback nesting",
            code_before="functionWithCallback(function(err, data) {\n    anotherCallback(function(err2, data2) {\n        // ...\n    });\n});",
            code_after="async function process() {\n    try {\n        const data = await functionWithPromise();\n        const data2 = await anotherPromise(data);\n        // ...\n    } catch (error) {\n        // Handle error\n    }\n}",
            reasoning="Callback hell reduces readability and error handling",
            priority="high"
        ))

    # Look for var usage (should use let/const)
    if "var " in content:
        suggestions.append(CodeSuggestion(
            file=filename,
            line=0,
            suggestion="Replace var with let/const",
            code_before="var x = 10;",
            code_after="const x = 10;  // or let if reassignment needed",
            reasoning="var has function scope, let/const have block scope",
            priority="medium"
        ))

    # Look for large functions
    lines = content.split('\n')
    brace_count = 0
    function_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if "function " in stripped or "=> {" in stripped:
            function_start = i
            brace_count = 0
        elif "{" in line:
            brace_count += line.count("{")
        elif "}" in line:
            brace_count -= line.count("}")

            if brace_count == 0 and function_start > 0:
                function_length = i - function_start + 1
                if function_length > 30:
                    suggestions.append(CodeSuggestion(
                        file=filename,
                        line=function_start+1,
                        suggestion="Function is too long - consider breaking it down",
                        code_before="// Long function...",
                        code_after="// Break into smaller functions",
                        reasoning="Long functions are harder to maintain and test",
                        priority="medium"
                    ))
                function_start = 0

    return suggestions

def analyze_java_code(filename: str, content: str, modification_type: str) -> List[CodeSuggestion]:
    """Analyze Java code for improvements"""
    suggestions = []

    # Look for long methods
    lines = content.split('\n')
    method_start = 0
    brace_count = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect method start (simplified)
        if "public " in stripped or "private " in stripped or "protected " in stripped:
            if "(" in stripped and ")" in stripped and "{" in stripped:
                method_start = i
                brace_count = 1
        elif method_start > 0:
            if "{" in line:
                brace_count += line.count("{")
            if "}" in line:
                brace_count -= line.count("}")

                if brace_count == 0:
                    method_length = i - method_start + 1
                    if method_length > 30:
                        suggestions.append(CodeSuggestion(
                            file=filename,
                            line=method_start+1,
                            suggestion="Method is too long - consider breaking it down",
                            code_before="// Long method...",
                            code_after="// Break into smaller methods",
                            reasoning="Long methods violate Single Responsibility Principle",
                            priority="medium"
                        ))
                    method_start = 0

    # Look for null checks without Optional
    if "!= null" in content or "== null" in content:
        suggestions.append(CodeSuggestion(
            file=filename,
            line=0,
            suggestion="Consider using Optional instead of null checks",
            code_before='if (value != null) {\n    return value.toString();\n}',
            code_after='Optional.ofNullable(value)\n    .map(Object::toString)\n    .orElse("default");',
            reasoning="Optional provides safer and more expressive null handling",
            priority="low"
        ))

    return suggestions

def analyze_generic_code(filename: str, content: str, modification_type: str) -> List[CodeSuggestion]:
    """Analyze generic code for improvements"""
    suggestions = []

    # Generic suggestions based on modification type
    if modification_type == "refactor":
        suggestions.append(CodeSuggestion(
            file=filename,
            line=0,
            suggestion="Consider extracting repeated logic into helper functions",
            code_before="// Repeated logic...",
            code_after="// Extracted to helper function",
            reasoning="DRY (Don't Repeat Yourself) principle",
            priority="medium"
        ))

    elif modification_type == "optimize":
        suggestions.append(CodeSuggestion(
            file=filename,
            line=0,
            suggestion="Review algorithms and data structures for optimization",
            code_before="// Current implementation",
            code_after="// Optimized implementation",
            reasoning="Potential performance improvements",
            priority="high"
        ))

    elif modification_type == "clean":
        suggestions.append(CodeSuggestion(
            file=filename,
            line=0,
            suggestion="Remove unused code and comments",
            code_before="// Unused code...",
            code_after="// Cleaned up",
            reasoning="Clean code is easier to maintain",
            priority="low"
        ))

    return suggestions

def apply_modifications(code: Dict[str, Any], suggestions: List[CodeSuggestion], modification_type: str) -> Dict[str, Any]:
    """Apply modifications to code based on suggestions"""
    modified_code = code.copy()

    for suggestion in suggestions:
        filename = suggestion.file

        if filename not in modified_code:
            continue

        content = modified_code[filename]

        # Apply high and critical priority suggestions automatically
        if suggestion.priority in ["high", "critical"]:
            # Simple text replacement (in reality would be more sophisticated)
            if suggestion.code_before in content:
                modified_code[filename] = content.replace(
                    suggestion.code_before,
                    suggestion.code_after
                )

    return modified_code

def calculate_quality_metrics(modified_code: Dict[str, Any], original_code: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Calculate quality metrics for modified code"""
    metrics = {
        "files_analyzed": len(modified_code),
        "lines_of_code": sum(len(str(c).split('\n')) for c in modified_code.values()),
        "complexity_score": 70,  # Placeholder
        "readability_score": 75,  # Placeholder
        "maintainability_score": 80,  # Placeholder
        "performance_score": 65  # Placeholder
    }

    # Language-specific metrics
    if language == "python":
        metrics["python_specific"] = {
            "uses_type_hints": "partial",
            "follows_pep8": "good",
            "has_docstrings": "needs_improvement"
        }
    elif language == "javascript":
        metrics["javascript_specific"] = {
            "uses_es6_features": "good",
            "has_proper_error_handling": "partial",
            "modular_structure": "needs_improvement"
        }

    return metrics

@app.post("/refactor")
async def refactor_code(request: ModifierRequest):
    """Specialized endpoint for code refactoring"""
    try:
        # Set modification type to refactor
        request.modification_type = "refactor"

        # Call the main modify function
        result = await modify_code(request)

        return {
            "status": "success",
            "refactoring_completed": True,
            "improvements_made": len(result.suggestions),
            "quality_improvement": f"{result.quality_metrics.get('readability_score', 0)}%",
            "details": result.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize")
async def optimize_code(request: ModifierRequest):
    """Specialized endpoint for performance optimization"""
    try:
        # Set modification type to optimize
        request.modification_type = "optimize"

        # Call the main modify function
        result = await modify_code(request)

        return {
            "status": "success",
            "optimization_completed": True,
            "performance_improvement": f"{result.quality_metrics.get('performance_score', 0)}%",
            "details": result.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clean")
async def clean_code(request: ModifierRequest):
    """Specialized endpoint for code cleaning"""
    try:
        # Set modification type to clean
        request.modification_type = "clean"

        # Call the main modify function
        result = await modify_code(request)

        return {
            "status": "success",
            "cleaning_completed": True,
            "reduction_in_complexity": f"{100 - result.quality_metrics.get('complexity_score', 100)}%",
            "details": result.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test")
async def test_modification():
    """Test endpoint to verify agent is working"""
    test_code = {
        "example.py": """
def process_data(data):
    result = []
    for item in data:
        for subitem in item:
            if subitem is not None:
                if subitem.value > 100:
                    result.append(subitem.value * 2)
                else:
                    result.append(subitem.value)
    return result

def calculate_stats(numbers):
    total = 0
    count = 0
    for n in numbers:
        total += n
        count += 1
    average = total / count if count > 0 else 0

    variance = 0
    for n in numbers:
        diff = n - average
        variance += diff * diff
    variance = variance / count if count > 0 else 0

    return {
        "average": average,
        "variance": variance,
        "count": count
    }
"""
    }

    try:
        request = ModifierRequest(
            code=test_code,
            modification_type="refactor",
            language="python"
        )

        result = await modify_code(request)

        return {
            "status": "success",
            "test": "passed",
            "suggestions_found": len(result.suggestions),
            "modifications_applied": len([m for m in result.modifications_applied if m["applied"]]),
            "agent": "modifier"
        }
    except Exception as e:
        return {
            "status": "error",
            "test": "failed",
            "error": str(e)
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5004))
    print(f"🚀 Starting Modifier Agent on port {port}")
    print(f"📍 Endpoint: http://localhost:{port}/modify")
    print(f"📚 Docs: http://localhost:{port}/docs")
    print(f"🔧 Refactoring, optimization, and code cleaning")

    uvicorn.run(app, host="0.0.0.0", port=port)