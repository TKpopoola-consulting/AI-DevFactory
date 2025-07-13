import unittest
from unittest.mock import patch
from agent_logic import BackendAgent

class TestBackendAgent(unittest.TestCase):
    @patch('google.generativeai.GenerativeModel')
    def test_generate_fastapi(self, mock_genai):
        mock_genai.return_value.generate_content.return_value.text = json.dumps({
            "structure": [{"path": "main.py", "content": "from fastapi import FastAPI"}],
            "dependencies": []
        })
        
        agent = BackendAgent()
        result = agent.generate_backend("API for users", "fastapi")
        self.assertIn("main.py", [f["path"] for f in result["structure"]])