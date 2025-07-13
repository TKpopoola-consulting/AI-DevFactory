import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List
import google.generativeai as genai
from validation.python_validator import PythonValidator
from validation.nodejs_validator import NodeJSValidator

class BackendAgent:
    def __init__(self):
        self.configure_gemini()
        self.templates = self.load_templates()
        self.validators = {
            'python': PythonValidator(),
            'nodejs': NodeJSValidator()
        }

    def configure_gemini(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(
            'gemini-pro',
            generation_config={
                "temperature": 0.5,
                "top_p": 0.95,
                "max_output_tokens": 4096
            }
        )

    def load_templates(self) -> Dict:
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

    def generate_backend(self, description: str, framework: str, requirements: List[str]) -> Dict:
        prompt = self._build_prompt(description, framework, requirements)
        response = self.model.generate_content(prompt)
        project = self._parse_response(response.text)
        
        # Merge with base template
        merged_project = self._merge_with_template(project, framework)
        
        # Validate the generated code
        validation_result = self.validate_project(merged_project['structure'], framework)
        
        return {
            **merged_project,
            'validation': validation_result
        }

    def validate_project(self, project_structure: List[Dict], framework: str) -> Dict:
        validator = self.validators['python'] if framework in ['fastapi', 'django'] else self.validators['nodejs']
        return validator.validate(project_structure)

    def _build_prompt(self, description: str, framework: str, requirements: List[str]) -> str:
        template = self.templates[framework]
        return f"""
        Generate production-ready {framework} backend code for:
        {description}
        
        Additional Requirements:
        {', '.join(requirements) if requirements else 'None'}
        
        Technical Specifications:
        1. Implement clean architecture
        2. Include proper error handling
        3. Add API documentation
        4. Use modern security practices
        5. Include database integration
        
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
            "entrypoint": "main file path",
            "api_routes": ["/route1", ...]
        }}
        """

    def _parse_response(self, response_text: str) -> Dict:
        clean_text = response_text.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(clean_text)

    def _merge_with_template(self, project: Dict, framework: str) -> Dict:
        """Merge generated code with base template"""
        template = self.templates[framework]['base']
        merged = {
            "structure": [],
            "dependencies": list(set(
                project.get('dependencies', []) +
                self._extract_deps_from_template(template)
            ),
            "entrypoint": project.get('entrypoint', '')
        }
        
        # Add template files not overridden
        for path, content in template.items():
            if not any(f['path'] == path for f in project['structure']):
                merged['structure'].append({
                    "path": path,
                    "content": content
                })
        
        # Add generated files
        merged['structure'].extend(project['structure'])
        
        return merged

    def _extract_deps_from_template(self, template: Dict) -> List[str]:
        """Extract dependencies from template files"""
        deps = []
        for content in template.values():
            if 'requirements.txt' in content:
                deps.extend([
                    line.strip() 
                    for line in content.split('\n') 
                    if line.strip() and not line.startswith('#')
                ])
            elif 'package.json' in content:
                try:
                    pkg = json.loads(content)
                    deps.extend([
                        f"{name}@{ver}" 
                        for name, ver in pkg.get('dependencies', {}).items()
                    ])
                except json.JSONDecodeError:
                    pass
        return deps