import google.generativeai as genai
import os
import json

class BackendGenerator:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_backend_code(self, description, framework='nodejs'):
        prompt = f"""
        As senior backend architect, create production-ready code for:
        {description}
        
        Requirements:
        - Use framework: {framework}
        - Implement RESTful API
        - Include database schema
        - Add authentication skeleton
        - Output in this JSON format:
        {{
          "api_code": "...",
          "database_schema": "{{'tables': [...]}}",
          "dependencies": ["express", "mongoose"]
        }}
        """
        
        response = self.model.generate_content(prompt)
        return self.parse_response(response.text)
    
    def parse_response(self, response_text):
        try:
            return json.loads(response_text.strip().replace("```json", "").replace("```", ""))
        except:
            # Fallback parsing
            return {
                "api_code": response_text,
                "database_schema": {},
                "dependencies": []
            }