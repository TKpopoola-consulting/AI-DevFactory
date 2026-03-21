# backend/agents/frontend_agent/agent_logic.py
"""
Complete Frontend Agent with Vue.js support, component hierarchy, styling,
responsive design, accessibility, performance optimization, and best practices
"""
import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from functools import lru_cache, wraps
import google.generativeai as genai
from dotenv import load_dotenv

# Import validators
from validation.react_validator import ReactValidator
from validation.flutter_validator import FlutterValidator
from validation.vue_validator import VueValidator

# Import utilities
from utils.component_generator import ComponentHierarchyGenerator, StylingGenerator
from utils.asset_optimizer import AssetOptimizer
from utils.file_generator import create_zip, save_to_disk

load_dotenv()


class FrontendAgent:
    """Complete frontend agent with multi-framework support"""
    
    def __init__(self):
        self.configure_gemini()
        self.templates = self.load_templates()
        self.validators = {
            'react': ReactValidator(),
            'flutter': FlutterValidator(),
            'vue': VueValidator()
        }
        self.optimizer = AssetOptimizer()
        self.cache = {}
        
    def configure_gemini(self):
        """Initialize Gemini with optimal settings"""
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(
            'gemini-pro',
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 4096
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
        
        if base_dir.exists():
            for file in base_dir.glob('*'):
                if file.is_file():
                    with open(file, 'r') as f:
                        template[file.name] = f.read()
        return template
    
    def _load_snippets(self, framework: str) -> List[Dict]:
        """Load all code snippets for framework"""
        snippets = []
        snippet_dir = Path(f'framework_templates/{framework}/snippets')
        
        if snippet_dir.exists():
            for snippet_file in snippet_dir.glob('*.json'):
                with open(snippet_file, 'r') as f:
                    snippets.append(json.load(f))
        return snippets
    
    def generate_project(self, prompt: str, framework: str = 'flutter') -> Dict:
        """Generate project with framework support"""
        try:
            # Check cache first
            cache_key = hashlib.md5(f"{prompt}_{framework}".encode()).hexdigest()
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Generate based on framework
            if framework == 'vue':
                result = self._generate_vue_project(prompt)
            elif framework == 'react':
                result = self._generate_react_project(prompt)
            elif framework == 'flutter':
                result = self._generate_flutter_project(prompt)
            else:
                raise ValueError(f"Unsupported framework: {framework}")
            
            # Add performance optimizations
            result = self.optimizer.optimize_project(result, framework)
            
            # Cache result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Generation failed: {str(e)}")
    
    def _generate_vue_project(self, prompt: str) -> Dict:
        """Generate Vue.js project with component hierarchy"""
        templates = self.templates.get('vue', {})
        
        # Generate component hierarchy
        hierarchy_gen = ComponentHierarchyGenerator('vue')
        hierarchy = hierarchy_gen.generate_hierarchy(prompt)
        
        # Generate styling
        styling_gen = StylingGenerator('vue', 'tailwind')
        styles = styling_gen.generate_styling(prompt)
        
        # Build Vue-specific prompt with hierarchy
        vue_prompt = self._build_vue_prompt(prompt, templates, hierarchy, styles)
        
        # Generate with Gemini with retry
        response = self._call_gemini_with_retry(vue_prompt)
        project = self._parse_response(response.text, 'vue')
        
        # Add hierarchy and styles to project
        project['component_hierarchy'] = hierarchy
        project['styling'] = styles
        
        # Merge with base template
        merged = self._merge_with_template(project, 'vue')
        
        # Validate
        validator = self.validators['vue']
        is_valid, errors = validator.validate_project(merged)
        
        return {
            **merged,
            'validation': {
                'passed': is_valid,
                'errors': errors,
                'accessibility': self._check_accessibility(merged),
                'responsive': self._check_responsive(merged),
                'best_practices': self._check_best_practices(merged, 'vue')
            },
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _generate_react_project(self, prompt: str) -> Dict:
        """Generate React project with component hierarchy"""
        templates = self.templates.get('react', {})
        
        # Generate component hierarchy
        hierarchy_gen = ComponentHierarchyGenerator('react')
        hierarchy = hierarchy_gen.generate_hierarchy(prompt)
        
        # Generate styling
        styling_gen = StylingGenerator('react', 'tailwind')
        styles = styling_gen.generate_styling(prompt)
        
        # Build React-specific prompt
        react_prompt = self._build_react_prompt(prompt, templates, hierarchy, styles)
        
        # Generate with Gemini
        response = self._call_gemini_with_retry(react_prompt)
        project = self._parse_response(response.text, 'react')
        
        project['component_hierarchy'] = hierarchy
        project['styling'] = styles
        
        merged = self._merge_with_template(project, 'react')
        
        validator = self.validators['react']
        is_valid, errors = validator.validate_project(merged)
        
        return {
            **merged,
            'validation': {
                'passed': is_valid,
                'errors': errors,
                'accessibility': self._check_accessibility(merged),
                'responsive': self._check_responsive(merged),
                'best_practices': self._check_best_practices(merged, 'react')
            },
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _generate_flutter_project(self, prompt: str) -> Dict:
        """Generate Flutter project"""
        templates = self.templates.get('flutter', {})
        
        flutter_prompt = self._build_flutter_prompt(prompt, templates)
        
        response = self._call_gemini_with_retry(flutter_prompt)
        project = self._parse_response(response.text, 'flutter')
        
        merged = self._merge_with_template(project, 'flutter')
        
        validator = self.validators['flutter']
        is_valid, errors = validator.validate_project(merged)
        
        return {
            **merged,
            'validation': {
                'passed': is_valid,
                'errors': errors,
                'best_practices': self._check_best_practices(merged, 'flutter')
            },
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _call_gemini_with_retry(self, prompt: str, retries: int = 3) -> Any:
        """Call Gemini API with retry logic"""
        for attempt in range(retries):
            try:
                return self.model.generate_content(prompt)
            except Exception as e:
                if attempt == retries - 1:
                    raise
                wait_time = 2 ** attempt
                time.sleep(wait_time)
    
    def _build_vue_prompt(self, user_prompt: str, templates: Dict, hierarchy: Dict, styles: Dict) -> str:
        """Build Vue.js specific prompt with hierarchy"""
        return f"""
        Generate production-ready Vue.js 3 code for:
        {user_prompt}
        
        Component Hierarchy:
        {json.dumps(hierarchy, indent=2, default=str)}
        
        Styling Requirements:
        {json.dumps(styles, indent=2)}
        
        Requirements:
        1. Use Vue 3 Composition API with <script setup>
        2. Include Vue Router for navigation
        3. Use Pinia for state management if needed
        4. Make components responsive with Tailwind CSS
        5. Include proper error boundaries
        6. Add accessibility attributes (aria-labels, roles)
        7. Use lazy loading for routes
        8. Include web-vitals for performance monitoring
        
        Base Template:
        {json.dumps(templates.get('base', {}), indent=2)}
        
        Available Snippets:
        {json.dumps(templates.get('snippets', []), indent=2)}
        
        Output Format (JSON):
        {{
            "structure": [
                {{"path": "src/App.vue", "content": "..."}},
                {{"path": "src/main.js", "content": "..."}},
                {{"path": "src/router/index.js", "content": "..."}},
                {{"path": "src/components/HelloWorld.vue", "content": "..."}}
            ],
            "dependencies": ["vue", "vue-router", "pinia", "tailwindcss"],
            "entry_point": "src/main.js",
            "description": "Brief description of the generated app"
        }}
        """
    
    def _build_react_prompt(self, user_prompt: str, templates: Dict, hierarchy: Dict, styles: Dict) -> str:
        """Build React specific prompt"""
        return f"""
        Generate production-ready React 18 code for:
        {user_prompt}
        
        Component Hierarchy:
        {json.dumps(hierarchy, indent=2, default=str)}
        
        Styling Requirements:
        {json.dumps(styles, indent=2)}
        
        Requirements:
        1. Use functional components with hooks
        2. Implement React Router for navigation
        3. Use context or Redux for state management
        4. Make responsive with Tailwind CSS
        5. Add React.lazy for code splitting
        6. Include accessibility attributes
        7. Add web-vitals tracking
        8. Use proper error boundaries
        
        Base Template:
        {json.dumps(templates.get('base', {}), indent=2)}
        
        Available Snippets:
        {json.dumps(templates.get('snippets', []), indent=2)}
        
        Output Format (JSON):
        {{
            "structure": [
                {{"path": "src/App.js", "content": "..."}},
                {{"path": "src/index.js", "content": "..."}},
                {{"path": "src/components/Header.js", "content": "..."}}
            ],
            "dependencies": ["react", "react-dom", "react-router-dom"],
            "entry_point": "src/index.js",
            "description": "Brief description"
        }}
        """
    
    def _build_flutter_prompt(self, user_prompt: str, templates: Dict) -> str:
        """Build Flutter specific prompt"""
        return f"""
        Generate production-ready Flutter code for:
        {user_prompt}
        
        Requirements:
        1. Use Material Design
        2. Implement proper state management (Provider or Riverpod)
        3. Make responsive for all screen sizes
        4. Add proper error handling
        5. Use const constructors where possible
        6. Implement proper navigation
        7. Add dispose methods for cleanup
        8. Follow Dart style guide
        
        Base Template:
        {json.dumps(templates.get('base', {}), indent=2)}
        
        Available Snippets:
        {json.dumps(templates.get('snippets', []), indent=2)}
        
        Output Format (JSON):
        {{
            "structure": [
                {{"path": "lib/main.dart", "content": "..."}},
                {{"path": "pubspec.yaml", "content": "..."}}
            ],
            "dependencies": ["flutter", "provider"],
            "entry_point": "lib/main.dart",
            "description": "Brief description"
        }}
        """
    
    def _parse_response(self, response_text: str, framework: str) -> Dict:
        """Parse and clean Gemini response"""
        try:
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse response: {str(e)}")
    
    def _merge_with_template(self, project: Dict, framework: str) -> Dict:
        """Merge generated code with base template"""
        template = self.templates.get(framework, {}).get('base', {})
        merged = {
            "structure": [],
            "dependencies": list(set(
                project.get('dependencies', []) +
                self._extract_deps_from_template(template)
            )),
            "entry_point": project.get('entry_point', ''),
            "description": project.get('description', '')
        }
        
        # Add template files not overridden
        for path, content in template.items():
            if not any(f['path'] == path for f in project.get('structure', [])):
                merged['structure'].append({
                    "path": path,
                    "content": content
                })
        
        # Add generated files
        merged['structure'].extend(project.get('structure', []))
        
        return merged
    
    def _extract_deps_from_template(self, template: Dict) -> List[str]:
        """Extract dependencies from template files"""
        deps = []
        for content in template.values():
            if 'dependencies:' in content:
                lines = content.split('\n')
                in_deps = False
                for line in lines:
                    if line.strip().startswith('dependencies:'):
                        in_deps = True
                    elif in_deps and line.strip().startswith('-'):
                        dep = line.strip().split(':')[0].replace('-', '').strip()
                        deps.append(dep)
                    elif in_deps and not line.strip().startswith(' '):
                        in_deps = False
            elif 'package.json' in content:
                try:
                    pkg = json.loads(content)
                    deps.extend(list(pkg.get('dependencies', {}).keys()))
                except:
                    pass
        return deps
    
    def _check_accessibility(self, project: Dict) -> Dict:
        """Check accessibility best practices"""
        issues = []
        for file in project.get('structure', []):
            content = file['content']
            if '<img' in content and 'alt=' not in content:
                issues.append(f"Missing alt text in {file['path']}")
            if '<button' in content and 'aria-label' not in content:
                issues.append(f"Missing aria-label on button in {file['path']}")
        return {"passed": len(issues) == 0, "issues": issues}
    
    def _check_responsive(self, project: Dict) -> Dict:
        """Check responsive design patterns"""
        issues = []
        for file in project.get('structure', []):
            content = file['content']
            if '@media' not in content and 'flex' not in content.lower():
                issues.append(f"Missing responsive patterns in {file['path']}")
        return {"passed": len(issues) == 0, "issues": issues}
    
    def _check_best_practices(self, project: Dict, framework: str) -> Dict:
        """Check framework-specific best practices"""
        issues = []
        if framework == 'flutter':
            for file in project.get('structure', []):
                if 'setState' in file['content'] and 'dispose' not in file['content']:
                    issues.append(f"Missing dispose() in {file['path']}")
        return {"passed": len(issues) == 0, "issues": issues}
    
    def export_project(self, project: Dict, format: str = 'zip') -> Any:
        """Export project in specified format"""
        if format == 'zip':
            return create_zip(project)
        elif format == 'disk':
            save_to_disk(project, f"output/{project.get('description', 'project')}")
        else:
            raise ValueError(f"Unsupported format: {format}")


if __name__ == '__main__':
    agent = FrontendAgent()
    result = agent.generate_project(
        "A weather app with 5-day forecast and location search",
        "vue"
    )
    print(json.dumps(result, indent=2))
