# backend/agents/frontend_agent/main.py
from flask import Flask, request, jsonify
from agent_logic import FrontendAgent
import logging

app = Flask(__name__)
agent = FrontendAgent()
logger = logging.getLogger(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate frontend project"""
    try:
        data = request.get_json()
        
        result = agent.generate_project(
            prompt=data['prompt'],
            framework=data.get('framework', 'react')
        )
        
        return jsonify({
            "status": "success",
            "project": result,
            "export_url": f"/export/{data.get('job_id')}" if data.get('job_id') else None
        })
        
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/validate', methods=['POST'])
def validate():
    """Validate existing project"""
    try:
        data = request.get_json()
        
        validator = agent.validators.get(data.get('framework', 'react'))
        if not validator:
            return jsonify({"error": "Unsupported framework"}), 400
        
        is_valid, errors = validator.validate_project(data['project'])
        
        return jsonify({
            "valid": is_valid,
            "errors": errors,
            "accessibility": agent._check_accessibility(data['project']),
            "responsive": agent._check_responsive(data['project'])
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/export', methods=['POST'])
def export():
    """Export project as ZIP"""
    try:
        data = request.get_json()
        zip_data = agent.export_project(data['project'], 'zip')
        
        return jsonify({
            "status": "success",
            "message": "Project exported successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "frameworks": list(agent.templates.keys()),
        "version": "2.0.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
