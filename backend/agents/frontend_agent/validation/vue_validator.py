# backend/agents/frontend_agent/validation/vue_validator.py
"""
Vue.js project validator
"""
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Tuple

class VueValidator:
    """Vue.js project validation"""
    
    @staticmethod
    def validate_project(project: Dict) -> Tuple[bool, List[str]]:
        errors = []
        
        # 1. Validate structure
        structure_errors = VueValidator._validate_structure(project)
        errors.extend(structure_errors)
        
        # 2. Validate package.json
        pkg_errors = VueValidator._validate_package_json(project)
        errors.extend(pkg_errors)
        
        # 3. Validate Vue component syntax
        component_errors = VueValidator._validate_vue_components(project)
        errors.extend(component_errors)
        
        # 4. Validate in temp directory
        if not errors:
            temp_errors = VueValidator._validate_in_tempdir(project)
            errors.extend(temp_errors)
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def _validate_structure(project: Dict) -> List[str]:
        errors = []
        required_files = {
            'package.json',
            'src/App.vue',
            'src/main.js',
            'public/index.html'
        }
        
        project_files = {f['path'] for f in project['structure']}
        missing_files = required_files - project_files
        
        if missing_files:
            errors.append(f"Missing required files: {', '.join(missing_files)}")
        
        return errors
    
    @staticmethod
    def _validate_package_json(project: Dict) -> List[str]:
        errors = []
        pkg_file = next((f for f in project['structure'] if f['path'] == 'package.json'), None)
        
        if not pkg_file:
            return ["Missing package.json"]
        
        try:
            pkg = json.loads(pkg_file['content'])
            required_deps = ['vue', 'vue-router']
            
            for dep in required_deps:
                if dep not in pkg.get('dependencies', {}):
                    errors.append(f"Missing required dependency: {dep}")
                    
        except json.JSONDecodeError:
            errors.append("Invalid package.json format")
        
        return errors
    
    @staticmethod
    def _validate_vue_components(project: Dict) -> List[str]:
        errors = []
        vue_files = [f for f in project['structure'] if f['path'].endswith('.vue')]
        
        for vue_file in vue_files:
            content = vue_file['content']
            
            # Check for template section
            if '<template>' not in content:
                errors.append(f"Missing <template> section in {vue_file['path']}")
            
            # Check for script section
            if '<script>' not in content and '<script setup>' not in content:
                errors.append(f"Missing <script> section in {vue_file['path']}")
            
            # Check for style section
            if '<style' not in content:
                errors.append(f"Missing <style> section in {vue_file['path']}")
        
        return errors
    
    @staticmethod
    def _validate_in_tempdir(project: Dict) -> List[str]:
        errors = []
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            # Create project structure
            for file in project['structure']:
                file_path = tmp_path / file['path']
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(file['content'])
            
            try:
                # Install dependencies
                install_result = subprocess.run(
                    ['npm', 'install'],
                    cwd=tmp_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if install_result.returncode != 0:
                    errors.append(f"npm install failed:\n{install_result.stderr}")
                
                # Run Vue CLI lint if available
                lint_result = subprocess.run(
                    ['npx', 'vue-cli-service', 'lint', '--no-fix'],
                    cwd=tmp_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if lint_result.returncode != 0:
                    errors.append(f"Vue lint issues:\n{lint_result.stdout}")
                
            except subprocess.TimeoutExpired:
                errors.append("Validation timed out")
            except Exception as e:
                errors.append(f"Validation process error: {str(e)}")
        
        return errors


# Updated agent_logic.py to include Vue support
class FrontendAgent:
    def generate_project(self, prompt: str, framework: str = 'flutter') -> Dict:
        """Generate project with framework support"""
        try:
            if framework == 'vue':
                return self._generate_vue_project(prompt)
            elif framework == 'react':
                return self._generate_react_project(prompt)
            elif framework == 'flutter':
                return self._generate_flutter_project(prompt)
            else:
                raise ValueError(f"Unsupported framework: {framework}")
        except Exception as e:
            raise RuntimeError(f"Generation failed: {str(e)}")
    
    def _generate_vue_project(self, prompt: str) -> Dict:
        """Generate Vue.js project"""
        templates = self.templates.get('vue', {})
        
        # Build Vue-specific prompt
        vue_prompt = self._build_vue_prompt(prompt, templates)
        
        # Generate with Gemini
        response = self.model.generate_content(vue_prompt)
        project = self._parse_response(response.text, 'vue')
        
        # Merge with base template
        merged = self._merge_with_template(project, 'vue')
        
        # Validate
        validator = VueValidator()
        is_valid, errors = validator.validate_project(merged)
        
        return {
            **merged,
            'validation': {
                'passed': is_valid,
                'errors': errors
            }
        }
    
    def _build_vue_prompt(self, user_prompt: str, templates: Dict) -> str:
        """Build Vue.js specific prompt"""
        return f"""
        Generate production-ready Vue.js 3 code for:
        {user_prompt}
        
        Requirements:
        1. Use Vue 3 Composition API with <script setup>
        2. Include Vue Router for navigation
        3. Use Pinia for state management if needed
        4. Make components responsive
        5. Include proper error boundaries
        
        Base Template:
        {json.dumps(templates.get('base', {}), indent=2)}
        
        Available Snippets:
        {json.dumps(templates.get('snippets', []), indent=2)}
        
        Output Format (JSON):
        {{
            "structure": [
                {{"path": "src/App.vue", "content": "..."}},
                {{"path": "src/main.js", "content": "..."}},
                {{"path": "src/router/index.js", "content": "..."}}
            ],
            "dependencies": ["vue", "vue-router", "pinia"],
            "entry_point": "src/main.js"
        }}
        """
