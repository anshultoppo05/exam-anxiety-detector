"""Integration tests for API routes."""

import json

import pytest


def test_health_endpoint_returns_200(client):
    resp = client.get("/api/v1/health/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "status" in data["data"]


def test_model_health_endpoint(client):
    resp = client.get("/api/v1/health/model")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "labels" in data["data"]


def test_analyze_requires_api_key(client, no_auth_headers):
    resp = client.post(
        "/api/v1/ai/analyze",
        headers=no_auth_headers,
        data=json.dumps({"text": "I am nervous about exams."}),
    )
    assert resp.status_code == 401


def test_analyze_returns_label(client, api_headers):
    resp = client.post(
        "/api/v1/ai/analyze",
        headers=api_headers,
        data=json.dumps({"text": "I am really anxious and worried about my final exams next week."}),
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["label"] in ["Low Anxiety", "Moderate Anxiety", "High Anxiety"]
    assert "tips" in data["data"]
    assert "disclaimer" in data["data"]


def test_analyze_empty_text_returns_400(client, api_headers):
    resp = client.post(
        "/api/v1/ai/analyze",
        headers=api_headers,
        data=json.dumps({"text": ""}),
    )
    assert resp.status_code == 400


def test_nlp_analyze_endpoint(client, api_headers):
    resp = client.post(
        "/api/v1/nlp/analyze",
        headers=api_headers,
        data=json.dumps({"text": "I study at Harvard and feel nervous about the math exam."}),
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "sentiment" in data["data"]


def test_nlp_sentiment_endpoint(client, api_headers):
    resp = client.post(
        "/api/v1/nlp/sentiment",
        headers=api_headers,
        data=json.dumps({"text": "I feel great about my exams!"}),
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"]["label"] in ["positive", "negative", "neutral"]


def test_swagger_docs_available(client):
    resp = client.get("/docs")
    # Flask-RESTX redirects /docs to /docs/ which returns the Swagger UI
    assert resp.status_code in [200, 301, 302, 308]
