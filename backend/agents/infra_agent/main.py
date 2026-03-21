# backend/agents/infra_agent/main.py
"""
Infrastructure Agent API endpoints
"""
from flask import Flask, request, jsonify
from agent_logic import InfraAgent, InfrastructureConfig
import logging
import asyncio

app = Flask(__name__)
agent = InfraAgent()
logger = logging.getLogger(__name__)


@app.route('/generate', methods=['POST'])
def generate_infrastructure():
    """Generate infrastructure templates"""
    try:
        data = request.get_json()
        
        config = InfrastructureConfig(
            job_id=data['job_id'],
            cloud_provider=data.get('cloud_provider', 'azure'),
            services=data.get('services', ['compute']),
            scaling=data.get('scaling', {}),
            environment=data.get('environment', 'dev'),
            region=data.get('region', 'eastus'),
            tags=data.get('tags', {})
        )
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(agent.generate_infrastructure(config))
        loop.close()
        
        return jsonify({
            "status": "success",
            "job_id": data['job_id'],
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/deploy', methods=['POST'])
def deploy_infrastructure():
    """Deploy generated infrastructure"""
    try:
        data = request.get_json()
        
        # Run async deployment
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            agent.deploy_infrastructure(
                data['job_id'],
                data['templates'],
                data['cloud_provider']
            )
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/cost', methods=['POST'])
def estimate_cost():
    """Estimate infrastructure cost"""
    try:
        data = request.get_json()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            agent.get_cost_estimate(
                data.get('templates', {}),
                data['cloud_provider'],
                data.get('services', [])
            )
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/validate', methods=['POST'])
def validate_templates():
    """Validate infrastructure templates"""
    try:
        data = request.get_json()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            agent.validator.validate_templates(
                data['templates'],
                data['cloud_provider']
            )
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/security', methods=['POST'])
def scan_security():
    """Scan templates for security issues"""
    try:
        data = request.get_json()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            agent.security_scanner.scan_templates(
                data['templates'],
                data['cloud_provider']
            )
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "cloud_providers": ["azure", "aws", "gcp"],
        "services": ["compute", "database", "storage", "monitoring", "networking", "secrets"],
        "version": "2.0.0"
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
