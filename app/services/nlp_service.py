"""NLP Service — spaCy + NLTK powered text analysis."""

import logging
from collections import Counter

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

# Ensure NLTK data is available
for resource in ["punkt", "punkt_tab", "stopwords", "wordnet", "vader_lexicon"]:
    try:
        nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}" if resource in ("stopwords", "wordnet") else f"sentiment/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)


class NLPService:
    """Full NLP pipeline using spaCy and NLTK."""

    def __init__(self, spacy_model_name="en_core_web_sm"):
        import spacy
        try:
            self.nlp = spacy.load(spacy_model_name)
        except OSError:
            logger.warning("spaCy model %s not found, downloading...", spacy_model_name)
            from spacy.cli import download
            download(spacy_model_name)
            self.nlp = spacy.load(spacy_model_name)

        self.vader = SentimentIntensityAnalyzer()
        self._stop_words = set(stopwords.words("english"))
        logger.info("NLP Service initialized with model: %s", spacy_model_name)

    def analyze(self, text):
        """Run full NLP pipeline on text."""
        doc = self.nlp(text)
        return {
            "sentiment": self._sentiment(text),
            "entities": self._entities(doc),
            "keywords": self._keywords(text),
            "tokens": self._tokenize(doc),
            "pos_tags": self._pos(doc),
        }

    def _tokenize(self, doc):
        """Return token list with lemma and stop-word flag."""
        return [
            {
                "text": token.text,
                "lemma": token.lemma_,
                "is_stop": token.is_stop,
                "pos": token.pos_,
            }
            for token in doc
            if not token.is_punct and not token.is_space
        ]

    def _entities(self, doc):
        """Extract named entities."""
        return [
            {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
            for ent in doc.ents
        ]

    def _pos(self, doc):
        """Return POS tags and dependency labels."""
        return [
            {"text": token.text, "pos": token.pos_, "dep": token.dep_}
            for token in doc
            if not token.is_punct and not token.is_space
        ]

    def _sentiment(self, text):
        """VADER sentiment analysis."""
        scores = self.vader.polarity_scores(text)
        compound = scores["compound"]
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        return {"compound": compound, "label": label, "scores": scores}

    def _keywords(self, text, top_n=10):
        """NLTK frequency-based keyword extraction."""
        tokens = word_tokenize(text.lower())
        filtered = [t for t in tokens if t.isalpha() and t not in self._stop_words and len(t) > 2]
        freq = Counter(filtered)
        return [word for word, _ in freq.most_common(top_n)]
