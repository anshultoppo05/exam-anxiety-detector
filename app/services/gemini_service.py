"""Google Gemini AI service."""

import logging
import os
import uuid

logger = logging.getLogger(__name__)


class GeminiService:
    """Wraps Google Generative AI SDK for text generation, chat, and embeddings."""

    def __init__(self):
        self._model = None
        self._embed_model = None
        self._sessions = {}
        self._available = False
        self._init_client()

    def _init_client(self):
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not set — Gemini features disabled.")
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)

            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            self._model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=(
                    "You are an empathetic student wellness counselor AI. "
                    "You provide supportive, non-diagnostic guidance for exam anxiety. "
                    "Never diagnose or replace professional help. "
                    "Always include a disclaimer that you are not a medical professional."
                ),
            )
            self._genai = genai
            self._available = True
            logger.info("Gemini service initialized with model: %s", model_name)
        except Exception as e:
            logger.error("Failed to initialize Gemini: %s", e)

    @property
    def is_available(self):
        return self._available

    def generate_text(self, prompt, max_tokens=None, temperature=None):
        """Generate text from a prompt."""
        if not self._available:
            return {"error": "Gemini AI is not configured. Please set GOOGLE_API_KEY."}

        config = {}
        if max_tokens:
            config["max_output_tokens"] = max_tokens
        if temperature is not None:
            config["temperature"] = temperature

        try:
            response = self._model.generate_content(prompt, generation_config=config if config else None)
            if response and response.text:
                return {"text": response.text}
            return {"error": "Empty response from Gemini."}
        except Exception as e:
            logger.error("Gemini generate error: %s", e)
            return {"error": str(e)}

    def chat(self, session_id, message):
        """Multi-turn chat conversation."""
        if not self._available:
            return {"error": "Gemini AI is not configured."}

        if not session_id:
            session_id = str(uuid.uuid4())

        if session_id not in self._sessions:
            self._sessions[session_id] = self._model.start_chat(history=[])

        try:
            chat_session = self._sessions[session_id]
            response = chat_session.send_message(message)
            return {"session_id": session_id, "reply": response.text if response.text else ""}
        except Exception as e:
            logger.error("Gemini chat error: %s", e)
            return {"error": str(e)}

    def summarize(self, text, style="concise"):
        """Summarize text in the given style."""
        style_prompts = {
            "concise": "Summarize this student's reflection concisely in 2-3 sentences:",
            "bullet": "Summarize this student's reflection as bullet points:",
            "detailed": "Provide a detailed summary of this student's reflection:",
        }
        prompt = f"{style_prompts.get(style, style_prompts['concise'])}\n\n{text}"
        return self.generate_text(prompt)

    def generate_anxiety_tips(self, level):
        """Generate personalized anxiety management tips for the given level."""
        if not self._available:
            return None  # Caller should use static fallback

        prompt = (
            f"A student has been assessed as having '{level}' exam anxiety. "
            f"Provide exactly 5 practical, empathetic, and actionable tips to help them. "
            f"Format as a numbered list. Include a brief disclaimer that this is not professional medical advice."
        )
        result = self.generate_text(prompt, max_tokens=500, temperature=0.7)
        return result.get("text") if "text" in result else None
