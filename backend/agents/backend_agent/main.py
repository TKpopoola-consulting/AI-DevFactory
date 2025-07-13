from flask import Flask, request, jsonify
from agent_logic import BackendAgent
from utils.error_handler import handle_agent_errors

app = Flask(__name__)
agent = BackendAgent()

@app.route('/generate', methods=['POST'])
@handle_agent_errors
def generate():
    data = request.get_json()
    result = agent.generate_backend(
        description=data['description'],
        framework=data.get('framework', 'fastapi'),
        requirements=data.get('requirements', [])
    )
    return jsonify(result)

@app.route('/validate', methods=['POST'])
@handle_agent_errors
def validate():
    data = request.get_json()
    result = agent.validate_project(
        project_structure=data['structure'],
        framework=data['framework']
    )
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)