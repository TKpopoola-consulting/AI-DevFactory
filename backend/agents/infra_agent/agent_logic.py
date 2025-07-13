import os
import json
import google.generativeai as genai
from pathlib import Path
from validation.bicep_validator import BicepValidator
from validation.terraform_validator import TerraformValidator
from utils.config_parser import ConfigParser

class InfraAgent:
    def __init__(self):
        self.configure_gemini()
        self.templates = self.load_templates()
        self.validators = {
            'bicep': BicepValidator(),
            'terraform': TerraformValidator()
        }
        self.parser = ConfigParser()

    def configure_gemini(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(
            'gemini-pro',
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "max_output_tokens": 4096
            }
        )

    def load_templates(self) -> dict:
        templates = {}
        template_dir = Path('templates')
        for cloud in template_dir.iterdir():
            if cloud.is_dir():
                templates[cloud.name] = {}
                for category in cloud.iterdir():
                    if category.is_dir():
                        category_name = category.name
                        templates[cloud.name][category_name] = {}
                        for file in category.glob('*'):
                            if file.is_file():
                                with open(file, 'r') as f:
                                    templates[cloud.name][category_name][file.name] = f.read()
        return templates

    def generate_infra(self, cloud_provider: str, app_type: str, requirements: list) -> dict:
        # Build prompt with cloud-specific templates
        prompt = self._build_prompt(cloud_provider, app_type, requirements)
        response = self.model.generate_content(prompt)
        config = self._parse_response(response.text)
        
        # Extract and validate variables
        config_type = 'bicep' if cloud_provider == 'azure' else 'terraform'
        variables = self.parser.parse_variables(config['main']['content'], config_type)
        
        # Validate the generated config
        validation_result = self.validate_config(config['main'], config_type)
        
        return {
            "config": config,
            "variables": variables,
            "validation": validation_result
        }

    def validate_config(self, config: dict, config_type: str) -> dict:
        validator = self.validators.get(config_type)
        if validator:
            return validator.validate(config)
        return {"valid": False, "error": f"No validator for {config_type}"}

    def _build_prompt(self, cloud_provider: str, app_type: str, requirements: list) -> str:
        # Get relevant templates for the cloud provider
        cloud_templates = self.templates.get(cloud_provider, {})
        bicep_templates = cloud_templates.get('bicep', {}) if cloud_provider == 'azure' else {}
        terraform_templates = cloud_templates.get('terraform', {}) if cloud_provider in ['aws', 'gcp'] else {}
        pipeline_templates = cloud_templates.get('pipelines', {})
        
        # Add app type specific requirements
        if app_type == "containerized":
            requirements.append("Container orchestration")
        elif app_type == "serverless":
            requirements.append("Serverless compute")
        elif app_type == "data_pipeline":
            requirements.append("Data processing services")
        
        prompt = f"""
        Generate infrastructure as code for a {app_type} application on {cloud_provider}.
        
        Application Requirements:
        {json.dumps(requirements, indent=2)}
        
        Use the following base templates:
        {json.dumps({**bicep_templates, **terraform_templates}, indent=2)}
        
        Also generate a CI/CD pipeline configuration using:
        {json.dumps(pipeline_templates, indent=2)}
        
        Include all necessary components for a production-ready deployment:
        - Compute resources
        - Database
        - Networking
        - Security
        - Monitoring
        
        Output in JSON format:
        {{
            "main": {{
                "path": "main.{'bicep' if cloud_provider=='azure' else 'tf'}",
                "content": "..."
            }},
            "pipeline": {{
                "path": "{'azure-pipelines.yml' if cloud_provider=='azure' else 'github-actions.yml'}",
                "content": "..."
            }},
            "dockerfile": {{
                "path": "Dockerfile",
                "content": "..."
            }}
        }}
        """
        return prompt

    def _parse_response(self, response_text: str) -> dict:
        try:
            clean_text = response_text.strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0].strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            # Attempt to extract JSON from malformed response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            return json.loads(response_text[start:end])