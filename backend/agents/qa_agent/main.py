from flask import Flask, request, jsonify
from agent_logic import QAAgent
from utils.error_handler import handle_agent_errors

app = Flask(__name__)
agent = QAAgent()

@app.route('/analyze', methods=['POST'])
@handle_agent_errors
def analyze_code():
    data = request.get_json()
    result = agent.analyze(
        code_url=data['code_url'],
        language=data['language'],
        framework=data['framework'],
        test_coverage=data.get('test_coverage', 70)
    )
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)