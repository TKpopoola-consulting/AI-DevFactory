import subprocess
import tempfile
import json
from pathlib import Path

class TerraformValidator:
    def validate(self, config: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create Terraform files
            for file_name, content in config.items():
                file_path = Path(tmp_dir) / file_name
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                
            try:
                # Initialize Terraform
                init_result = subprocess.run(
                    ["terraform", "init"],
                    cwd=tmp_dir,
                    capture_output=True,
                    text=True
                )
                
                if init_result.returncode != 0:
                    return {
                        "valid": False,
                        "error": init_result.stderr,
                        "init_output": init_result.stdout
                    }
                
                # Validate configuration
                validate_result = subprocess.run(
                    ["terraform", "validate", "-json"],
                    cwd=tmp_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Format check
                format_result = subprocess.run(
                    ["terraform", "fmt", "-check", "-diff"],
                    cwd=tmp_dir,
                    capture_output=True,
                    text=True
                )
                
                validation_output = json.loads(validate_result.stdout) if validate_result.stdout else {}
                
                return {
                    "valid": validation_output.get("valid", False),
                    "validation_output": validation_output,
                    "format_valid": format_result.returncode == 0,
                    "format_output": format_result.stdout
                }
            except subprocess.CalledProcessError as e:
                return {
                    "valid": False,
                    "error": e.stderr,
                    "output": e.stdout
                }