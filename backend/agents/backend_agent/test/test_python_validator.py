import unittest
from validation.python_validator import PythonValidator
from pathlib import Path

class TestPythonValidator(unittest.TestCase):
    def setUp(self):
        self.validator = PythonValidator()
        self.valid_project = [
            {
                "path": "main.py",
                "content": "print('Hello World')"
            }
        ]

    def test_valid_python(self):
        result = self.validator.validate(self.valid_project)
        self.assertTrue(result["valid"])

    def test_invalid_syntax(self):
        invalid_project = [
            {
                "path": "main.py",
                "content": "print('Hello World"
            }
        ]
        result = self.validator.validate(invalid_project)
        self.assertFalse(result["valid"])