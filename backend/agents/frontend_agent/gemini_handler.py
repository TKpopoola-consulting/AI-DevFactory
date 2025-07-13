import os
import json
import time
from typing import Dict, List, Optional
from pathlib import Path
import google.generativeai as genai
from validation.flutter_validator import FlutterValidator
from validation.react_validator import ReactValidator

class FrontendGenerator:
    """Enhanced generator with template management and validation"""
    
    def __init__(self):
        self.configure_gemini()
        self.load_templates()
        self.validators = {
            'flutter': FlutterValidator,
            'react': ReactValidator
        }
    
    def configure_gemini(self):
        """Initialize Gemini with optimal settings"""
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(
            'gemini-pro',
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 2048
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        )
    
    def load_templates(self):
        """Load all framework templates and snippets"""
        self.templates = {}
        template_dir = Path('framework_templates')
        
        for framework_dir in template_dir.iterdir():
            if framework_dir.is_dir():
                framework = framework_dir.name
                self.templates[framework] = {
                    'base': self._load_base_template(framework),
                    'snippets': self._load_snippets(framework)
                }
    
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
        Generate complete frontend project with validation
        Returns: {
            "status": "success|error",
            "project": { ... },
            "warnings": List[str],
            "validation_passed": bool
        }
        """
        start_time = time.time()
        generation_result = {
            "status": "success",
            "framework": framework,
            "generation_time": 0,
            "validation_passed": False,
            "warnings": [],
            "errors": []
        }
        
        try:
            # Generate initial code
            generated = self._generate_initial_code(prompt, framework)
            generation_result["project"] = generated
            generation_result["generation_time"] = time.time() - start_time
            
            # Validate the generated code
            validator = self.validators.get(framework)
            if validator:
                is_valid, validation_errors = validator.validate_project(generated)
                generation_result["validation_passed"] = is_valid
                if validation_errors:
                    generation_result["warnings"] = validation_errors
            
            return generation_result
            
        except Exception as e:
            generation_result.update({
                "status": "error",
                "error": str(e),
                "generation_time": time.time() - start_time
            })
            return generation_result
    
    def _generate_initial_code(self, prompt: str, framework: str) -> Dict:
        """Generate code using Gemini with retry logic"""
        full_prompt = self._build_prompt(prompt, framework)
        
        for attempt in range(3):
            try:
                response = self.model.generate_content(full_prompt)
                return self._parse_response(response.text, framework)
            except Exception as e:
                if attempt == 2:
                    raise
                time.sleep(1 * (attempt + 1))
    
    def _build_prompt(self, user_prompt: str, framework: str) -> str:
        """Construct detailed generation prompt"""
        template = self.templates[framework]
        
        return f"""
        **ROLE**: Expert {framework.capitalize()} Developer
        **TASK**: Generate production-ready application
        
        **USER REQUIREMENTS**:
        {user_prompt}
        
        **TECHNICAL REQUIREMENTS**:
        1. Use {framework} best practices
        2. Include proper state management
        3. Make responsive for all screen sizes
        4. Add basic testing setup
        5. Include necessary dependencies
        
        **BASE TEMPLATE**:
        {json.dumps(template['base'], indent=2)}
        
        **AVAILABLE SNIPPETS**:
        {json.dumps(template['snippets'], indent=2)}
        
        **OUTPUT FORMAT** (JSON):
        {{
            "structure": [
                {{
                    "path": "file/relative/path",
                    "content": "..."
                }}
            ],
            "dependencies": ["package1", ...],
            "main_file": "path/to/main/file",
            "entry_point": "main function/widget"
        }}
        """
    
    def _parse_response(self, response_text: str, framework: str) -> Dict:
        """Parse and clean Gemini response"""
        try:
            # Clean response text
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:-3].strip()
            
            # Parse JSON
            result = json.loads(clean_text)
            
            # Ensure required fields
            if not all(k in result for k in ['structure', 'dependencies']):
                raise ValueError("Invalid response format")
            
            # Merge with base template
            return self._merge_with_template(result, framework)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse response: {str(e)}")
    
    def _merge_with_template(self, generated: Dict, framework: str) -> Dict:
        """Merge generated code with base template"""
        template = self.templates[framework]['base']
        merged = {
            "structure": [],
            "dependencies": list(set(
                generated.get('dependencies', []) + 
                self._extract_deps_from_template(template)
            )),
            "main_file": generated.get('main_file', '')
        }
        
        # Add template files not overridden
        for path, content in template.items():
            if not any(f['path'] == path for f in generated['structure']):
                merged['structure'].append({
                    "path": path,
                    "content": content
                })
        
        # Add generated files
        merged['structure'].extend(generated['structure'])
        
        return merged
    
    def _extract_deps_from_template(self, template: Dict) -> List[str]:
        """Extract dependencies from template files"""
        deps = []
        for content in template.values():
            if 'dependencies:' in content:
                lines = content.split('\n')
                deps_section = False
                for line in lines:
                    if line.strip().startswith('dependencies:'):
                        deps_section = True
                    elif deps_section and line.strip().startswith('-'):
                        dep = line.strip().split(':')[0].replace('-', '').strip()
                        deps.append(dep)
                    elif deps_section and not line.strip().startswith(' '):
                        deps_section = False
        return deps