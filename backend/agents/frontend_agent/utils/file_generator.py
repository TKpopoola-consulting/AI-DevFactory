# utils/file_generator.py
import os
import zipfile
from io import BytesIO
from typing import Dict, List

def create_zip(project: Dict) -> BytesIO:
    """Create in-memory ZIP of generated project"""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in project['structure']:
            zipf.writestr(file['path'], file['content'])
    buffer.seek(0)
    return buffer

def save_to_disk(project: Dict, output_dir: str):
    """Save project to filesystem (for debugging)"""
    os.makedirs(output_dir, exist_ok=True)
    for file in project['structure']:
        path = os.path.join(output_dir, file['path'])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(file['content'])