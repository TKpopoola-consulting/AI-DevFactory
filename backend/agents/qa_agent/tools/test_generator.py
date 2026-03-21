# backend/agents/qa_agent/tools/test_generator.py
"""
Dynamic test generation based on code structure
"""
import ast
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TestGenerator:
    """Generate test templates from code structure"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load test templates"""
        return {
            "python_unit": """
import pytest
from {module} import {class_name}

class Test{class_name}:
    ""Tests for {class_name}""
    
    def setup_method(self):
        """Setup before each test"""
        pass
    
    def test_{method_name}_success(self):
        """Test {method_name} with valid input"""
        # TODO: Implement test
        pass
    
    def test_{method_name}_error(self):
        """Test {method_name} with invalid input"""
        # TODO: Implement test
        pass
    
    def test_{method_name}_edge_case(self):
        """Test {method_name} with edge cases"""
        # TODO: Implement test
        pass
""",
            "python_integration": """
import pytest
from fastapi.testclient import TestClient
from {module} import app

client = TestClient(app)

class TestAPI:
    ""Integration tests for API endpoints""
    
    def test_{endpoint_name}_success(self):
        """Test {endpoint_name} endpoint"""
        response = client.get("{endpoint_path}")
        assert response.status_code == 200
        assert "data" in response.json()
    
    def test_{endpoint_name}_validation(self):
        """Test {endpoint_name} input validation"""
        response = client.post("{endpoint_path}", json={})
        assert response.status_code == 422
""",
            "python_e2e": """
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

class TestE2E:
    ""End-to-end tests""
    
    @pytest.fixture
    def driver(self):
        driver = webdriver.Chrome()
        yield driver
        driver.quit()
    
    def test_user_flow(self, driver):
        """Test complete user journey"""
        driver.get("{base_url}")
        # TODO: Implement full user flow
        pass
""",
            "javascript_unit": """
import { describe, it, expect, beforeEach } from 'vitest';
import { {class_name} } from './{module}';

describe('{class_name}', () => {
  let instance;

  beforeEach(() => {
    instance = new {class_name}();
  });

  it('should {method_name} successfully', () => {
    const result = instance.{method_name}();
    expect(result).toBeDefined();
  });

  it('should handle errors', () => {
    expect(() => instance.{method_name}()).toThrow();
  });
});
""",
            "javascript_integration": """
import { describe, it, expect } from 'vitest';
import request from 'supertest';
import app from './app';

describe('API Integration Tests', () => {
  it('GET {endpoint_path} should return data', async () => {
    const response = await request(app)
      .get('{endpoint_path}')
      .expect(200);
    
    expect(response.body).toHaveProperty('data');
  });
});
"""
        }
    
    async def generate_test_templates(self, code_structure: Dict[str, Any], language: str) -> Dict[str, str]:
        """
        Generate test templates based on code structure
        
        Args:
            code_structure: Parsed code structure with classes, functions, endpoints
            language: Programming language (python or javascript)
            
        Returns:
            Dictionary of generated test files
        """
        tests = {}
        
        if language == "python":
            tests.update(await self._generate_python_tests(code_structure))
        elif language == "javascript":
            tests.update(await self._generate_javascript_tests(code_structure))
        
        return tests
    
    async def _generate_python_tests(self, structure: Dict) -> Dict[str, str]:
        """Generate Python test files"""
        tests = {}
        
        # Unit tests for each class/function
        for file_path, content in structure.get("files", {}).items():
            classes = self._extract_python_classes(content)
            functions = self._extract_python_functions(content)
            
            if classes or functions:
                test_content = []
                
                for class_name in classes:
                    test_content.append(self._generate_python_unit_test(class_name, content))
                
                for func_name in functions:
                    test_content.append(self._generate_python_function_test(func_name, content))
                
                if test_content:
                    test_file = file_path.replace(".py", "_test.py")
                    tests[f"tests/{test_file}"] = "\n\n".join(test_content)
        
        # Integration tests for API endpoints
        if structure.get("endpoints"):
            tests["tests/test_integration.py"] = self._generate_python_integration_tests(structure["endpoints"])
        
        # E2E tests
        tests["tests/test_e2e.py"] = self._generate_python_e2e_tests(structure)
        
        return tests
    
    def _extract_python_classes(self, content: str) -> List[str]:
        """Extract class names from Python code"""
        try:
            tree = ast.parse(content)
            return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        except:
            return []
    
    def _extract_python_functions(self, content: str) -> List[str]:
        """Extract function names from Python code"""
        try:
            tree = ast.parse(content)
            return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        except:
            return []
    
    def _generate_python_unit_test(self, class_name: str, content: str) -> str:
        """Generate unit test for a Python class"""
        # Extract methods
        methods = self._extract_methods(content, class_name)
        
        test_template = self.templates["python_unit"]
        test_content = test_template.format(
            module="app",
            class_name=class_name,
            method_name=methods[0] if methods else "default"
        )
        
        return test_content
    
    def _extract_methods(self, content: str, class_name: str) -> List[str]:
        """Extract method names from a class"""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    return [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        except:
            pass
        return []
    
    def _generate_python_function_test(self, func_name: str, content: str) -> str:
        """Generate test for a Python function"""
        return f"""
import pytest
from app import {func_name}

def test_{func_name}_basic():
    '''Basic test for {func_name}'''
    # TODO: Implement test
    result = {func_name}()
    assert result is not None
"""
    
    def _generate_python_integration_tests(self, endpoints: List[Dict]) -> str:
        """Generate integration tests for API endpoints"""
        tests = []
        
        for endpoint in endpoints:
            test = self.templates["python_integration"].format(
                endpoint_name=endpoint["name"].replace("/", "_"),
                endpoint_path=endpoint["path"]
            )
            tests.append(test)
        
        return "\n\n".join(tests)
    
    def _generate_python_e2e_tests(self, structure: Dict) -> str:
        """Generate E2E tests"""
        base_url = structure.get("base_url", "http://localhost:8000")
        return self.templates["python_e2e"].format(base_url=base_url)
    
    async def _generate_javascript_tests(self, structure: Dict) -> Dict[str, str]:
        """Generate JavaScript test files"""
        tests = {}
        
        # Unit tests
        for file_path in structure.get("files", {}):
            if file_path.endswith((".js", ".jsx")):
                tests[f"tests/{file_path.replace('.js', '.test.js')}"] = self.templates["javascript_unit"]
        
        # Integration tests
        if structure.get("endpoints"):
            tests["tests/integration.test.js"] = self._generate_javascript_integration_tests(
                structure["endpoints"]
            )
        
        return tests
    
    def _generate_javascript_integration_tests(self, endpoints: List[Dict]) -> str:
        """Generate JavaScript integration tests"""
        tests = []
        
        for endpoint in endpoints:
            test = self.templates["javascript_integration"].format(
                endpoint_path=endpoint["path"]
            )
            tests.append(test)
        
        return "\n\n".join(tests)
