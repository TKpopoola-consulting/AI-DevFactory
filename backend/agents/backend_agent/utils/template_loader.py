import json
from pathlib import Path
from typing import Dict, Any

class TemplateLoader:
    @staticmethod
    def load_with_placeholders(template_path: str, replacements: Dict[str, str]) -> Dict[str, Any]:
        """Load template with dynamic placeholder replacement"""
        path = Path(template_path)
        if not path.exists():
            raise BackendAgentError(
                f"Template not found: {template_path}",
                BackendErrorCode.TEMPLATE_LOAD_FAILED
            )
        
        with open(path, 'r') as f:
            content = f.read()
        
        for placeholder, value in replacements.items():
            content = content.replace(f"{{{{{placeholder}}}}}", value)
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content