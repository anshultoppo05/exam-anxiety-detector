"""NLP analysis routes."""

import time
import uuid

from flask import current_app, request
from flask_restx import Namespace, Resource

from app.utils.auth import require_api_key
from app.utils.validators import validate_text_input

nlp_ns = Namespace("nlp", description="NLP text analysis endpoints")


def _make_meta(start):
    return {
        "request_id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "processing_time_ms": round((time.time() - start) * 1000, 2),
    }


@nlp_ns.route("/analyze")
class FullNLPAnalysis(Resource):
    @require_api_key
    def post(self):
        """Full NLP pipeline: entities, sentiment, POS, keywords."""
        start = time.time()
        data = request.get_json(silent=True) or {}
        try:
            text = validate_text_input(data.get("text", ""))
        except ValueError as e:
            return {"success": False, "error": {"code": 400, "message": str(e)}}, 400

        nlp_svc = current_app.config.get("_nlp_service")
        result = nlp_svc.analyze(text)
        return {"success": True, "data": result, "meta": _make_meta(start)}, 200


@nlp_ns.route("/sentiment")
class SentimentOnly(Resource):
    @require_api_key
    def post(self):
        """Sentiment analysis only (VADER)."""
        start = time.time()
        data = request.get_json(silent=True) or {}
        try:
            text = validate_text_input(data.get("text", ""))
        except ValueError as e:
            return {"success": False, "error": {"code": 400, "message": str(e)}}, 400

        nlp_svc = current_app.config.get("_nlp_service")
        result = nlp_svc._sentiment(text)
        return {"success": True, "data": result, "meta": _make_meta(start)}, 200


@nlp_ns.route("/entities")
class EntityExtraction(Resource):
    @require_api_key
    def post(self):
        """Named entity recognition (spaCy)."""
        start = time.time()
        data = request.get_json(silent=True) or {}
        try:
            text = validate_text_input(data.get("text", ""))
        except ValueError as e:
            return {"success": False, "error": {"code": 400, "message": str(e)}}, 400

        nlp_svc = current_app.config.get("_nlp_service")
        doc = nlp_svc.nlp(text)
        result = nlp_svc._entities(doc)
        return {"success": True, "data": {"entities": result}, "meta": _make_meta(start)}, 200


@nlp_ns.route("/keywords")
class KeywordExtraction(Resource):
    @require_api_key
    def post(self):
        """Keyword extraction (NLTK)."""
        start = time.time()
        data = request.get_json(silent=True) or {}
        try:
            text = validate_text_input(data.get("text", ""))
        except ValueError as e:
            return {"success": False, "error": {"code": 400, "message": str(e)}}, 400

        nlp_svc = current_app.config.get("_nlp_service")
        result = nlp_svc._keywords(text)
        return {"success": True, "data": {"keywords": result}, "meta": _make_meta(start)}, 200
