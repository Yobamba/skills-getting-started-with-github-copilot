"""
Pytest configuration and shared fixtures for tests
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Provide sample test data for activities"""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["alice@test.edu", "bob@test.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["charlie@test.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        }
    }


@pytest.fixture
def reset_activities():
    """Reset activities to known state before and after each test"""
    from src.app import activities
    
    # Store original state
    original_state = {key: {
        "description": act["description"],
        "schedule": act["schedule"],
        "max_participants": act["max_participants"],
        "participants": act["participants"].copy()
    } for key, act in activities.items()}
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original_state)
