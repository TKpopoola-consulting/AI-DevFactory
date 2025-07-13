import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class FrontendAgent:
    def __init__(self):
        self.configure_gemini()
        self.templates = self.load_templates()

    def configure_gemini(self):
        """Initialize Gemini with safety settings"""
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(
            'gemini-pro',
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 2048
            }
        )

    def load_templates(self) -> Dict:
        """Load all framework templates and snippets"""
        templates = {}
        template_dir = Path('framework_templates')
        
        for framework_dir in template_dir.iterdir():
            if framework_dir.is_dir():
                framework = framework_dir.name
                templates[framework] = {
                    'base': self._load_base_template(framework),
                    'snippets': self._load_snippets(framework)
                }
        return templates

    def _load_base_template(self, framework: str) -> Dict:
        """Load base template files"""
        base_dir = Path(f'framework_templates/{framework}/base')
        template = {}
        
        for file in base_dir.glob('*'):
            if file.is_file():
                with open(file, 'r') as f:
                    template[file.name] = f.read()
        return template

    def _load_snippets(self, framework: str) -> List[Dict]:
        """Load all code snippets for framework"""
        snippets = []
        snippet_dir = Path(f'framework_templates/{framework}/snippets')
        
        for snippet_file in snippet_dir.glob('*.json'):
            with open(snippet_file, 'r') as f:
                snippets.append(json.load(f))
        return snippets

    def generate_project(self, prompt: str, framework: str = 'flutter') -> Dict:
        """
        Generate complete frontend project
        Returns: {
            "structure": [
                {"path": "lib/main.dart", "content": "..."},
                {"path": "pubspec.yaml", "content": "..."}
            ],
            "dependencies": ["provider", "http"],
            "main_file": "lib/main.dart"
        }
        """
        try:
            full_prompt = self._build_prompt(prompt, framework)
            response = self.model.generate_content(full_prompt)
            return self._parse_response(response.text, framework)
        except Exception as e:
            raise RuntimeError(f"Generation failed: {str(e)}")

    def _build_prompt(self, user_prompt: str, framework: str) -> str:
        """Construct detailed prompt for Gemini"""
        template = self.templates[framework]
        return f"""
        Generate production-ready {framework} code for:
        {user_prompt}
        
        Technical Requirements:
        1. Use {framework} best practices
        2. Include proper state management
        3. Make responsive for all screen sizes
        4. Add basic testing setup
        5. Include necessary dependencies
        
        Base Template:
        {json.dumps(template['base'], indent=2)}
        
        Available Snippets:
        {json.dumps(template['snippets'], indent=2)}
        
        Output Format (JSON):
        {{
            "structure": [
                {{
                    "path": "file/relative/path",
                    "content": "..."
                }}
            ],
            "dependencies": ["package1", ...],
            "main_file": "path/to/main/file"
        }}
        """

    def _parse_response(self, response_text: str, framework: str) -> Dict:
        """Parse and clean Gemini response"""
        try:
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:-3].strip()
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse response: {str(e)}")

if __name__ == '__main__':
    agent = FrontendAgent()
    result = agent.generate_project(
        "A weather app with 5-day forecast",
        "flutter"
    )
    print(json.dumps(result, indent=2))