"""Flask-RESTX request/response models."""

from flask_restx import fields


def register_models(api):
    """Register all API models on the given Api instance."""

    text_input = api.model("TextInput", {
        "text": fields.String(required=True, description="Student text to analyze", min_length=1, max_length=10000),
    })

    chat_input = api.model("ChatInput", {
        "message": fields.String(required=True, description="Chat message"),
        "session_id": fields.String(description="Optional session ID for multi-turn chat"),
    })

    anxiety_score = api.model("AnxietyScore", {
        "label": fields.String(description="Anxiety level label"),
        "score": fields.Float(description="Confidence score"),
    })

    analysis_result = api.model("AnalysisResult", {
        "label": fields.String(description="Predicted anxiety level"),
        "confidence": fields.Float(description="Confidence of the prediction"),
        "all_scores": fields.List(fields.Nested(anxiety_score)),
        "tips": fields.List(fields.String, description="Personalized tips"),
        "disclaimer": fields.String(description="Non-diagnostic disclaimer"),
    })

    nlp_result = api.model("NLPResult", {
        "sentiment": fields.Raw(description="Sentiment analysis results"),
        "entities": fields.List(fields.Raw, description="Named entities"),
        "keywords": fields.List(fields.String, description="Extracted keywords"),
        "tokens": fields.List(fields.Raw, description="Token details"),
    })

    meta_model = api.model("Meta", {
        "request_id": fields.String,
        "timestamp": fields.String,
        "processing_time_ms": fields.Float,
    })

    success_envelope = api.model("SuccessResponse", {
        "success": fields.Boolean(default=True),
        "data": fields.Raw(description="Response payload"),
        "meta": fields.Nested(meta_model),
    })

    error_detail = api.model("ErrorDetail", {
        "code": fields.Integer,
        "message": fields.String,
        "details": fields.String,
    })

    error_envelope = api.model("ErrorResponse", {
        "success": fields.Boolean(default=False),
        "error": fields.Nested(error_detail),
    })

    return {
        "text_input": text_input,
        "chat_input": chat_input,
        "analysis_result": analysis_result,
        "nlp_result": nlp_result,
        "success_envelope": success_envelope,
        "error_envelope": error_envelope,
    }
