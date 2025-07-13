import subprocess
import tempfile
import json
from pathlib import Path

class BicepValidator:
    def validate(self, config: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create Bicep files
            for file_name, content in config.items():
                file_path = Path(tmp_dir) / file_name
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                
            try:
                # Lint all files
                lint_result = subprocess.run(
                    ["az", "bicep", "lint", "--file", str(Path(tmp_dir)/"main.bicep")],
                    capture_output=True,
                    text=True
                )
                
                # Build to validate
                build_result = subprocess.run(
                    ["az", "bicep", "build", "--file", str(Path(tmp_dir)/"main.bicep")],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                return {
                    "valid": True,
                    "lint_output": lint_result.stdout,
                    "build_output": build_result.stdout
                }
            except subprocess.CalledProcessError as e:
                return {
                    "valid": False,
                    "error": e.stderr,
                    "build_output": e.stdout
                }