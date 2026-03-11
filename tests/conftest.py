"""Pytest fixtures."""

import pytest
from app import create_app
from config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing."""
    application = create_app(config_override=TestingConfig)
    yield application


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def api_headers():
    """Headers with valid API key."""
    return {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key",
    }


@pytest.fixture
def no_auth_headers():
    """Headers without API key."""
    return {"Content-Type": "application/json"}
