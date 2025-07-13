import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple
import json

class ReactValidator:
    """React project validator using npm and ESLint"""
    
    @staticmethod
    def validate_project(project: Dict) -> Tuple[bool, List[str]]:
        errors = []
        
        # 1. Validate structure
        structure_errors = ReactValidator._validate_structure(project)
        errors.extend(structure_errors)
        
        # 2. Validate package.json
        pkg_errors = ReactValidator._validate_package_json(project)
        errors.extend(pkg_errors)
        
        # 3. Validate in temp dir
        if not errors:
            temp_errors = ReactValidator._validate_in_tempdir(project)
            errors.extend(temp_errors)
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def _validate_structure(project: Dict) -> List[str]:
        errors = []
        required_files = {
            'package.json',
            'src/App.js',
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
            if 'dependencies' not in pkg:
                errors.append("Missing dependencies in package.json")
            if 'react' not in pkg.get('dependencies', {}):
                errors.append("React not listed in dependencies")
        except json.JSONDecodeError:
            errors.append("Invalid package.json format")
        
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
                
                # Run ESLint
                lint_result = subprocess.run(
                    ['npx', 'eslint', 'src/'],
                    cwd=tmp_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if lint_result.returncode != 0:
                    errors.append(f"ESLint issues:\n{lint_result.stdout}")
                
            except subprocess.TimeoutExpired:
                errors.append("Validation timed out")
            except Exception as e:
                errors.append(f"Validation process error: {str(e)}")
        
        return errors