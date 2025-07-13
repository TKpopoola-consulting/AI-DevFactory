import logging
from flask import jsonify
from functools import wraps

logger = logging.getLogger("qa_agent")

def handle_agent_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except subprocess.CalledProcessError as e:
            logger.error(f"Process error: {e.stderr}")
            return jsonify({
                "error": "QA process failed",
                "details": e.stderr.decode()
            }), 500
        except requests.RequestException as e:
            logger.error(f"Network error: {str(e)}")
            return jsonify({
                "error": "Network operation failed",
                "details": str(e)
            }), 503
        except TimeoutError as e:
            logger.error(f"Timeout error: {str(e)}")
            return jsonify({
                "error": "Operation timed out",
                "details": str(e)
            }), 504
        except Exception as e:
            logger.critical(f"Unhandled exception: {str(e)}")
            return jsonify({
                "error": "Internal server error",
                "details": str(e)
            }), 500
    return wrapper