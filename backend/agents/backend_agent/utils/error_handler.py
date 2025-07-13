import logging
from functools import wraps
from flask import jsonify
from enum import Enum

class BackendErrorCode(Enum):
    TEMPLATE_LOAD_FAILED = 2001
    VALIDATION_FAILED = 2002
    FRAMEWORK_NOT_SUPPORTED = 2003
    CONTAINER_VALIDATION_ERROR = 2004

class BackendAgentError(Exception):
    def __init__(self, message: str, code: BackendErrorCode, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

def handle_backend_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BackendAgentError as e:
            logging.error(f"[{e.code.name}] {e.message}", extra=e.details)
            return jsonify({
                "error": e.message,
                "code": e.code.value,
                "details": e.details
            }), 400
        except Exception as e:
            logging.critical(f"Unhandled exception: {str(e)}", exc_info=True)
            return jsonify({
                "error": "Internal server error",
                "code": 500
            }), 500
    return wrapper