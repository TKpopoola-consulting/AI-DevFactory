import os
import json
import logging
from flask import Flask, request, jsonify
from gemini_handler import generate_frontend_code
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_code():
    try:
        # Get job data from orchestration
        job_data = request.json
        
        # Extract parameters
        job_id = job_data['job_id']
        description = job_data['description']
        framework = job_data.get('framework', 'flutter')
        output_config = job_data['output_config']
        
        # Generate code
        result = generate_frontend_code(
            description=description,
            framework=framework,
            platforms=output_config['platforms']
        )
        
        # Validate generated code
        if framework == 'flutter':
            from dart_flutter_utils import validate_flutter_code
            validation_result = validate_flutter_code(result['code'])
            if not validation_result['valid']:
                raise ValueError(f"Flutter validation failed: {validation_result['errors']}")
        
        return jsonify({
            "job_id": job_id,
            "status": "success",
            "artifacts": {
                "code": result['code'],
                "dependencies": result['dependencies']
            }
        })
    
    except Exception as e:
        logging.error(f"Frontend generation failed: {str(e)}")
        return jsonify({
            "job_id": job_id,
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)