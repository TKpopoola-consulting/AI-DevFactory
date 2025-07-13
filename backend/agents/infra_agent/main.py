from flask import Flask, request, jsonify
from agent_logic import InfraAgent
from utils.error_handler import handle_agent_errors

app = Flask(__name__)
agent = InfraAgent()

@app.route('/generate', methods=['POST'])
@handle_agent_errors
def generate_infra():
    data = request.get_json()
    result = agent.generate_infra(
        cloud_provider=data['cloud_provider'],
        app_type=data['app_type'],
        requirements=data.get('requirements', [])
    )
    return jsonify(result)

@app.route('/validate', methods=['POST'])
@handle_agent_errors
def validate_infra():
    data = request.get_json()
    result = agent.validate_config(
        config=data['config'],
        config_type=data['config_type']
    )
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)