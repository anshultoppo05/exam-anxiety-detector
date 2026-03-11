"""API key authentication decorator."""

from functools import wraps
from flask import request, current_app, jsonify


def require_api_key(f):
    """Decorator that validates X-API-Key header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        expected_key = current_app.config.get("APP_API_KEY")
        if not api_key or api_key != expected_key:
            return {"success": False, "error": {"code": 401, "message": "Unauthorized — invalid or missing API key."}}, 401
        return f(*args, **kwargs)
    return decorated
