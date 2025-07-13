import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict
import json

class NodeJSValidator:
    def validate(self, project_structure: List[Dict]) -> Dict:
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create project structure
            for file in project_structure:
                path = Path(tmp_dir) / file['path']
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(file['content'])
            
            # Run validation commands
            try:
                # 1. Check package.json
                pkg_file = Path(tmp_dir)/'package.json'
                if not pkg_file.exists():
                    return {"valid": False, "errors": ["Missing package.json"]}
                
                # 2. Install dependencies
                subprocess.run(
                    ['npm', 'install'],
                    cwd=tmp_dir,
                    check=True
                )
                
                # 3. Run ESLint if configured
                eslintrc = Path(tmp_dir)/'.eslintrc.js'
                if eslintrc.exists():
                    subprocess.run(
                        ['npx', 'eslint', '.'],
                        cwd=tmp_dir,
                        check=True
                    )
                
                # 4. Run tests
                subprocess.run(
                    ['npm', 'test'],
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