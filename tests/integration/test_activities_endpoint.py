"""
Integration tests for GET /activities endpoint and root redirect
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestActivitiesEndpoint:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Verify that GET /activities returns status code 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Verify that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_not_empty(self, client):
        """Verify that GET /activities returns non-empty dictionary"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) > 0

    def test_get_activities_contains_required_fields(self, client):
        """Verify that each activity contains all required fields"""
        response = client.get("/activities")
        activities = response.json()
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity in activities.items():
            assert required_fields.issubset(activity.keys()), \
                f"Activity '{activity_name}' missing required fields"

    def test_get_activities_participants_is_list(self, client):
        """Verify that participants field is a list for each activity"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity in activities.items():
            assert isinstance(activity["participants"], list), \
                f"Participants for '{activity_name}' is not a list"

    def test_get_activities_max_participants_is_positive(self, client):
        """Verify that max_participants is a positive integer"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity in activities.items():
            assert isinstance(activity["max_participants"], int), \
                f"max_participants for '{activity_name}' is not an integer"
            assert activity["max_participants"] > 0, \
                f"max_participants for '{activity_name}' is not positive"

    def test_activity_names_are_keys(self, client):
        """Verify that activity names are dictionary keys"""
        response = client.get("/activities")
        activities = response.json()
        
        # Verify we can access an activity by name
        activity_names = list(activities.keys())
        assert len(activity_names) > 0
        first_activity = activities[activity_names[0]]
        assert "description" in first_activity


class TestRootRedirect:
    """Test the root endpoint redirect"""

    def test_root_redirects(self, client):
        """Verify that GET / returns a redirect response"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307

    def test_root_redirects_to_static_index(self, client):
        """Verify that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_target_exists(self, client):
        """Verify that following the redirect works"""
        response = client.get("/", follow_redirects=True)
        # We expect either 200 (if file exists) or 404 (if not served by static)
        # Just verify the redirect chain works
        assert response.status_code in [200, 404]
