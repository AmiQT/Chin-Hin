"""
Test configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client for API testing."""
    return TestClient(app)


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "ahmad@chinhin.com",
        "full_name": "Ahmad bin Hassan",
        "department": "Engineering",
        "role": "employee"
    }
