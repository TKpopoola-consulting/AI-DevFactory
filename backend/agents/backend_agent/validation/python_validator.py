import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict

class PythonValidator:
    def validate(self, project_structure: List[Dict]) -> Dict:
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create project structure
            for file in project_structure:
                path = Path(tmp_dir) / file['path']
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(file['content'])
            
            # Run validation commands
            try:
                # 1. Python syntax check
                subprocess.run(
                    ['python', '-m', 'py_compile', str(Path(tmp_dir)/'*.py')],
                    check=True,
                    capture_output=True
                )
                
                # 2. Install dependencies
                req_file = Path(tmp_dir)/'requirements.txt'
                if req_file.exists():
                    subprocess.run(
                        ['pip', 'install', '-r', 'requirements.txt'],
                        cwd=tmp_dir,
                        check=True
                    )
                
                # 3. Run tests if exists
                test_dir = Path(tmp_dir)/'tests'
                if test_dir.exists():
                    subprocess.run(
                        ['python', '-m', 'pytest'],
                        cwd=tmp_dir,
                        check=True
                    )
                
                return {"valid": True}
            
            except subprocess.CalledProcessError as e:
                return {
                    "valid": False,
                    "errors": [e.stderr.decode()],
                    "command": e.cmd
                }