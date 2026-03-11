"""Flask application factory."""

import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restx import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import get_config

logger = logging.getLogger(__name__)


def create_app(config_override=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load config
    cfg = config_override or get_config()
    app.config.from_object(cfg)

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Rate limiter
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200/day", "60/hour"],
        storage_uri="memory://",
    )
    app.config["_limiter"] = limiter

    # Flask-RESTX API with Swagger docs
    api = Api(
        app,
        version="1.0",
        title="Exam Anxiety Detector API",
        description="AI-powered exam anxiety analysis for students",
        doc="/docs",
        prefix="/api/v1",
    )

    # Register namespaces
    from app.routes.health_routes import health_ns
    from app.routes.ai_routes import ai_ns
    from app.routes.nlp_routes import nlp_ns

    api.add_namespace(health_ns, path="/health")
    api.add_namespace(ai_ns, path="/ai")
    api.add_namespace(nlp_ns, path="/nlp")

    # Initialize services (load once at startup)
    with app.app_context():
        _init_services(app)

    # Global error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(success=False, error={"code": 400, "message": "Bad Request", "details": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify(success=False, error={"code": 401, "message": "Unauthorized"}), 401

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify(success=False, error={"code": 429, "message": "Rate limit exceeded. Please try again later."}), 429

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(success=False, error={"code": 500, "message": "Internal server error."}), 500

    logger.info("Flask app created successfully.")
    return app


def _init_services(app):
    """Initialize ML and NLP services once at startup."""
    # NLP Service
    try:
        from app.services.nlp_service import NLPService
        app.config["_nlp_service"] = NLPService(app.config.get("SPACY_MODEL", "en_core_web_sm"))
        logger.info("NLP service loaded.")
    except Exception as e:
        logger.error("Failed to load NLP service: %s", e)
        app.config["_nlp_service"] = None

    # BERT Classifier
    try:
        from app.services.bert_classifier import BertClassifier
        app.config["_bert_classifier"] = BertClassifier()
        logger.info("BERT classifier loaded.")
    except Exception as e:
        logger.error("Failed to load BERT classifier: %s", e)
        app.config["_bert_classifier"] = None

    # Gemini Service
    try:
        from app.services.gemini_service import GeminiService
        app.config["_gemini_service"] = GeminiService()
        logger.info("Gemini service loaded.")
    except Exception as e:
        logger.error("Failed to load Gemini service: %s", e)
        app.config["_gemini_service"] = None
