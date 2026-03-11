"""Health check routes."""

import time
from flask import current_app
from flask_restx import Namespace, Resource

health_ns = Namespace("health", description="Health check endpoints")

_start_time = time.time()


@health_ns.route("/")
class HealthCheck(Resource):
    def get(self):
        """System health status."""
        classifier = current_app.config.get("_bert_classifier")
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "uptime_seconds": round(time.time() - _start_time, 1),
                "bert_model_ready": classifier.is_ready if classifier else False,
                "gemini_available": current_app.config.get("_gemini_service", None) is not None
                    and current_app.config["_gemini_service"].is_available,
            },
        }, 200


@health_ns.route("/model")
class ModelHealth(Resource):
    def get(self):
        """BERT model info and readiness."""
        classifier = current_app.config.get("_bert_classifier")
        return {
            "success": True,
            "data": {
                "model": current_app.config.get("BERT_MODEL", "unknown"),
                "ready": classifier.is_ready if classifier else False,
                "labels": ["Low Anxiety", "Moderate Anxiety", "High Anxiety"],
            },
        }, 200
