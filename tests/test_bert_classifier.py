"""Tests for BERT classifier."""

import pytest


@pytest.fixture
def classifier():
    from app.services.bert_classifier import BertClassifier
    return BertClassifier()


def test_predict_returns_label(classifier):
    result = classifier.predict("I am very anxious about my upcoming exams.")
    assert result["label"] in ["Low Anxiety", "Moderate Anxiety", "High Anxiety"]


def test_confidence_between_0_1(classifier):
    result = classifier.predict("I feel good about studying.")
    assert 0.0 <= result["confidence"] <= 1.0


def test_all_scores_sum_to_approximately_1(classifier):
    result = classifier.predict("I am somewhat nervous but mostly prepared.")
    total = sum(s["score"] for s in result["all_scores"])
    assert abs(total - 1.0) < 0.05  # Allow small floating point variance


def test_high_anxiety_keywords_detect(classifier):
    result = classifier.predict(
        "I am terrified and panicking. I feel hopeless and can't stop crying. "
        "I dread the exam and feel like I'm going to have a breakdown."
    )
    assert result["label"] in ["Moderate Anxiety", "High Anxiety"]


def test_low_anxiety_text(classifier):
    result = classifier.predict(
        "I feel confident and well-prepared for my exams. "
        "I've studied hard and I'm looking forward to doing well."
    )
    assert result["label"] in ["Low Anxiety", "Moderate Anxiety"]
