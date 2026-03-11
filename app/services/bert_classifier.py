"""BERT-based anxiety classifier service."""

import logging
import os

logger = logging.getLogger(__name__)

# Label mapping
LABEL_MAP = {0: "Low Anxiety", 1: "Moderate Anxiety", 2: "High Anxiety"}


class BertClassifier:
    """Wraps a Hugging Face text classification pipeline for anxiety detection."""

    def __init__(self, model_path=None):
        self._pipeline = None
        self._model_path = model_path
        self._ready = False
        self._load_model()

    def _load_model(self):
        """Load model — uses saved fine-tuned model if available, otherwise falls back to
        a zero-shot / sentiment approach using a distilbert model so the app works out of the box."""
        try:
            from transformers import pipeline as hf_pipeline

            saved = self._model_path or os.path.join(os.path.dirname(__file__), "..", "..", "ml", "saved_model")

            # Check if we have a fine-tuned model saved
            if os.path.isdir(saved) and os.path.exists(os.path.join(saved, "config.json")):
                logger.info("Loading fine-tuned model from %s", saved)
                self._pipeline = hf_pipeline(
                    "text-classification",
                    model=saved,
                    return_all_scores=True,
                    truncation=True,
                    max_length=512,
                )
                self._ready = True
            else:
                # Fallback: use distilbert-base-uncased-finetuned-sst-2-english
                # We'll map its sentiment output to our 3-class anxiety scheme
                logger.info("No fine-tuned model found. Using fallback sentiment model.")
                self._pipeline = hf_pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    return_all_scores=True,
                    truncation=True,
                    max_length=512,
                )
                self._ready = True

        except Exception as e:
            logger.error("Failed to load BERT model: %s", e)
            self._ready = False

    @property
    def is_ready(self):
        return self._ready

    def predict(self, text):
        """Predict anxiety level from text.
        Returns dict with label, confidence, and all_scores.
        """
        if not self._ready:
            return self._fallback_predict(text)

        try:
            results = self._pipeline(text)
            scores_list = results[0] if isinstance(results[0], list) else results

            # Check if using the fine-tuned 3-class model
            if len(scores_list) == 3:
                all_scores = [
                    {"label": LABEL_MAP.get(i, f"LABEL_{i}"), "score": round(s["score"], 4)}
                    for i, s in enumerate(scores_list)
                ]
                best = max(all_scores, key=lambda x: x["score"])
                return {
                    "label": best["label"],
                    "confidence": best["score"],
                    "all_scores": all_scores,
                }
            else:
                # Map 2-class sentiment to 3-class anxiety
                return self._map_sentiment_to_anxiety(scores_list, text)

        except Exception as e:
            logger.error("Prediction error: %s", e)
            return self._fallback_predict(text)

    def _map_sentiment_to_anxiety(self, scores, text):
        """Map binary sentiment scores to anxiety levels using heuristics."""
        score_dict = {s["label"]: s["score"] for s in scores}
        negative_score = score_dict.get("NEGATIVE", 0.0)
        positive_score = score_dict.get("POSITIVE", 0.0)

        # Use anxiety-related keyword boosting
        anxiety_keywords = [
            "anxious", "worried", "nervous", "scared", "afraid", "panic",
            "stress", "fear", "dread", "overwhelm", "can't sleep", "failing",
            "fail", "terrified", "hopeless", "helpless", "cry", "crying",
        ]
        text_lower = text.lower()
        keyword_count = sum(1 for kw in anxiety_keywords if kw in text_lower)
        anxiety_boost = min(keyword_count * 0.08, 0.3)

        adjusted_negative = min(negative_score + anxiety_boost, 1.0)

        if adjusted_negative >= 0.7:
            label = "High Anxiety"
            high = round(adjusted_negative, 4)
            moderate = round((1 - high) * 0.6, 4)
            low = round(1 - high - moderate, 4)
        elif adjusted_negative >= 0.4:
            label = "Moderate Anxiety"
            moderate = round(adjusted_negative, 4)
            high = round((1 - moderate) * 0.35, 4)
            low = round(1 - moderate - high, 4)
        else:
            label = "Low Anxiety"
            low = round(positive_score, 4)
            moderate = round((1 - low) * 0.4, 4)
            high = round(1 - low - moderate, 4)

        all_scores = [
            {"label": "Low Anxiety", "score": max(low, 0.0)},
            {"label": "Moderate Anxiety", "score": max(moderate, 0.0)},
            {"label": "High Anxiety", "score": max(high, 0.0)},
        ]
        best = next(s for s in all_scores if s["label"] == label)
        return {
            "label": label,
            "confidence": best["score"],
            "all_scores": all_scores,
        }

    def _fallback_predict(self, text):
        """Simple keyword-based fallback when no model is available."""
        text_lower = text.lower()
        high_kw = ["terrified", "panic", "hopeless", "can't breathe", "breakdown", "crying"]
        mod_kw = ["worried", "nervous", "anxious", "stressed", "uneasy", "tense"]

        high_count = sum(1 for kw in high_kw if kw in text_lower)
        mod_count = sum(1 for kw in mod_kw if kw in text_lower)

        if high_count >= 2:
            label, conf = "High Anxiety", 0.75
        elif high_count >= 1 or mod_count >= 2:
            label, conf = "Moderate Anxiety", 0.65
        elif mod_count >= 1:
            label, conf = "Moderate Anxiety", 0.55
        else:
            label, conf = "Low Anxiety", 0.70

        scores = {"Low Anxiety": 0.15, "Moderate Anxiety": 0.15, "High Anxiety": 0.15}
        scores[label] = conf
        remaining = 1.0 - conf
        other_labels = [l for l in scores if l != label]
        for ol in other_labels:
            scores[ol] = round(remaining / len(other_labels), 4)

        return {
            "label": label,
            "confidence": conf,
            "all_scores": [{"label": l, "score": s} for l, s in scores.items()],
        }
