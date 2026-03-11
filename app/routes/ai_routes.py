"""AI analysis routes — BERT classification + Gemini chat/summarize."""

import time
import uuid

from flask import current_app, request
from flask_restx import Namespace, Resource

from app.utils.auth import require_api_key
from app.utils.validators import validate_text_input
from app.utils.tips_content import ANXIETY_TIPS, DISCLAIMER

ai_ns = Namespace("ai", description="AI-powered anxiety analysis")


def _make_meta(start):
    return {
        "request_id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "processing_time_ms": round((time.time() - start) * 1000, 2),
    }


@ai_ns.route("/analyze")
class AnalyzeAnxiety(Resource):
    @require_api_key
    def post(self):
        """Classify exam anxiety level from student text."""
        start = time.time()
        data = request.get_json(silent=True) or {}
        raw_text = data.get("text", "")

        try:
            text = validate_text_input(raw_text)
        except ValueError as e:
            return {"success": False, "error": {"code": 400, "message": str(e)}}, 400

        classifier = current_app.config.get("_bert_classifier")
        if not classifier:
            return {"success": False, "error": {"code": 503, "message": "Model not loaded."}}, 503

        prediction = classifier.predict(text)
        label = prediction["label"]

        # Get tips — try Gemini first, then static fallback
        gemini = current_app.config.get("_gemini_service")
        tips_text = None
        if gemini and gemini.is_available:
            tips_text = gemini.generate_anxiety_tips(label)

        if tips_text:
            tips = [t.strip() for t in tips_text.strip().split("\n") if t.strip()]
        else:
            tips_data = ANXIETY_TIPS.get(label, ANXIETY_TIPS["Moderate Anxiety"])
            tips = tips_data["tips"]

        result = {
            "label": label,
            "confidence": prediction["confidence"],
            "all_scores": prediction["all_scores"],
            "tips": tips,
            "color": ANXIETY_TIPS.get(label, {}).get("color", "yellow"),
            "emoji": ANXIETY_TIPS.get(label, {}).get("emoji", "🟡"),
            "disclaimer": DISCLAIMER,
        }

        return {"success": True, "data": result, "meta": _make_meta(start)}, 200


@ai_ns.route("/chat")
class ChatSession(Resource):
    @require_api_key
    def post(self):
        """Multi-turn Gemini chat session."""
        start = time.time()
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()
        session_id = data.get("session_id", "")

        if not message:
            return {"success": False, "error": {"code": 400, "message": "Message is required."}}, 400

        gemini = current_app.config.get("_gemini_service")
        if not gemini or not gemini.is_available:
            return {"success": False, "error": {"code": 503, "message": "Gemini AI is not configured."}}, 503

        result = gemini.chat(session_id, message)
        if "error" in result:
            return {"success": False, "error": {"code": 500, "message": result["error"]}}, 500

        return {"success": True, "data": result, "meta": _make_meta(start)}, 200


@ai_ns.route("/summarize")
class SummarizeText(Resource):
    @require_api_key
    def post(self):
        """Summarize student reflection text."""
        start = time.time()
        data = request.get_json(silent=True) or {}
        raw_text = data.get("text", "")
        style = data.get("style", "concise")

        try:
            text = validate_text_input(raw_text)
        except ValueError as e:
            return {"success": False, "error": {"code": 400, "message": str(e)}}, 400

        gemini = current_app.config.get("_gemini_service")
        if not gemini or not gemini.is_available:
            return {"success": False, "error": {"code": 503, "message": "Gemini AI is not configured."}}, 503

        result = gemini.summarize(text, style)
        if "error" in result:
            return {"success": False, "error": {"code": 500, "message": result["error"]}}, 500

        return {"success": True, "data": {"summary": result["text"]}, "meta": _make_meta(start)}, 200
