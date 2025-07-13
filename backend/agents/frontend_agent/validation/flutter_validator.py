# validation/flutter_validator.py
import subprocess
import tempfile
from pathlib import Path
from typing import Dict

class FlutterValidator:
    @staticmethod
    def validate_project(project: Dict) -> bool:
        """Validate generated Flutter project"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create project structure
            for file in project['structure']:
                path = Path(tmp_dir) / file['path']
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(file['content'])
            
            # Run validation commands
            try:
                # Check Dart formatting
                subprocess.run(
                    ['dart', 'format', '--set-exit-if-changed', tmp_dir],
                    check=True,
                    capture_output=True
                )
                
                # Analyze code
                result = subprocess.run(
                    ['flutter', 'analyze', tmp_dir],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    raise ValidationError(f"Flutter analyze failed:\n{result.stderr}")
                
                # Verify pubspec
                subprocess.run(
                    ['flutter', 'pub', 'get'],
                    cwd=tmp_dir,
                    check=True
                )
                
                return True
            except subprocess.CalledProcessError as e:
                raise ValidationError(f"Validation failed: {str(e)}\n{e.stderr}")

class ValidationError(Exception):
    pass