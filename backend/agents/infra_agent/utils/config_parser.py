import json
import yaml
import re
from typing import Dict, Any

class ConfigParser:
    @staticmethod
    def parse_variables(config: str, config_type: str) -> Dict[str, Any]:
        """Extract variables from IaC config"""
        variables = {}
        
        if config_type == "bicep":
            # Extract Bicep params: param myParam string = 'value'
            param_pattern = r'param\s+(\w+)\s+(\w+)(?:\s*=\s*(.*))?'
            matches = re.finditer(param_pattern, config)
            for match in matches:
                name = match.group(1)
                var_type = match.group(2)
                default = match.group(3).strip("'\"") if match.group(3) else None
                variables[name] = {
                    "type": var_type,
                    "default": default
                }
        
        elif config_type == "terraform":
            # Extract Terraform variables: variable "instance_type" { default = "t2.micro" }
            var_pattern = r'variable\s+"(\w+)"\s*{([^}]*)}'
            matches = re.finditer(var_pattern, config, re.DOTALL)
            for match in matches:
                name = match.group(1)
                props = match.group(2)
                
                # Extract default value
                default_match = re.search(r'default\s*=\s*(.*)', props)
                default = default_match.group(1).strip('"') if default_match else None
                
                # Extract type
                type_match = re.search(r'type\s*=\s*(\w+)', props)
                var_type = type_match.group(1) if type_match else "string"
                
                variables[name] = {
                    "type": var_type,
                    "default": default
                }
        
        return variables

    @staticmethod
    def generate_parameters(config: str, config_type: str, values: Dict[str, Any]) -> str:
        """Inject parameter values into config"""
        if config_type == "bicep":
            for name, value in values.items():
                if isinstance(value, str):
                    value = f"'{value}'"
                config = re.sub(
                    rf'(param\s+{name}\s+\w+\s*=\s*)(.*)',
                    rf'\1{value}',
                    config
                )
        
        elif config_type == "terraform":
            for name, value in values.items():
                if isinstance(value, str):
                    value = f'"{value}"'
                config = re.sub(
                    rf'(variable\s+"{name}"\s*{{[^}}]*default\s*=\s*)([^}}]*)',
                    rf'\1{value}',
                    config
                )
        
        return config