import json
import google.generativeai as genai
import os

class ReportGenerator:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_report(self, results: dict) -> dict:
        prompt = f"""
        As a senior software quality analyst, generate a comprehensive quality assessment report based on the following test results:
        
        Security Scan:
        {json.dumps(results['security'], indent=2)}
        
        Test Results:
        {json.dumps(results['tests'], indent=2)}
        
        Performance Metrics:
        {json.dumps(results['performance'], indent=2)}
        
        Code Coverage:
        {json.dumps(results['coverage'], indent=2)}
        
        Structure your report with:
        1. Executive Summary
        2. Security Assessment
        3. Functional Testing Results
        4. Performance Evaluation
        5. Code Quality Metrics
        6. Recommendations
        
        Output in JSON format:
        {{
            "summary": "...",
            "security_rating": "A-F",
            "test_score": "0-100",
            "performance_grade": "A-F",
            "overall_quality": "Pass/Fail",
            "recommendations": ["...", "..."]
        }}
        """
        
        response = self.model.generate_content(prompt)
        return self._parse_response(response.text)
    
    def _parse_response(self, response_text: str) -> dict:
        try:
            clean_text = response_text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            # Fallback to manual extraction
            return {
                "summary": "Failed to parse report",
                "security_rating": "N/A",
                "test_score": 0,
                "performance_grade": "N/A",
                "overall_quality": "Fail",
                "recommendations": ["Review QA results manually"]
            }