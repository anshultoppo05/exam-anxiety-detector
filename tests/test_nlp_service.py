"""Tests for NLP service."""

import pytest


@pytest.fixture
def nlp_service():
    from app.services.nlp_service import NLPService
    return NLPService()


def test_sentiment_positive(nlp_service):
    result = nlp_service._sentiment("I feel great and confident about my exams!")
    assert result["label"] == "positive"


def test_sentiment_negative(nlp_service):
    result = nlp_service._sentiment("I am terrified and hopeless about failing the exam.")
    assert result["label"] == "negative"


def test_sentiment_returns_compound(nlp_service):
    result = nlp_service._sentiment("I feel okay about the exam.")
    assert "compound" in result
    assert -1.0 <= result["compound"] <= 1.0


def test_keywords_extracted(nlp_service):
    text = "The exam stress is overwhelming. I feel anxious about the math exam and the science exam."
    keywords = nlp_service._keywords(text)
    assert isinstance(keywords, list)
    assert "exam" in keywords


def test_entities_extraction(nlp_service):
    text = "I study at MIT in Cambridge and my professor Dr. Smith is giving the final exam."
    doc = nlp_service.nlp(text)
    entities = nlp_service._entities(doc)
    assert isinstance(entities, list)
    labels = [e["label"] for e in entities]
    assert any(l in labels for l in ["ORG", "GPE", "PERSON"])


def test_full_analysis(nlp_service):
    result = nlp_service.analyze("I am worried about my upcoming final exams at university.")
    assert "sentiment" in result
    assert "entities" in result
    assert "keywords" in result
    assert "tokens" in result


def test_empty_text_handling(nlp_service):
    """NLP service processes short text without errors."""
    result = nlp_service.analyze("test")
    assert "sentiment" in result
