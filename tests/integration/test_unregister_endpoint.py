"""
Integration tests for DELETE /activities/{activity_name}/participants endpoint
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to known state before and after each test"""
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


class TestUnregisterEndpoint:
    """Test the DELETE /activities/{activity_name}/participants endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """Verify successful unregister removes participant from activity"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Known participant
        
        # Verify participant is there
        assert email in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email not in activities[activity_name]["participants"]

    def test_unregister_returns_message(self, client, reset_activities):
        """Verify unregister returns a confirmation message"""
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Known participant
        
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        data = response.json()
        
        assert "message" in data
        assert activity_name in data["message"]
        assert email in data["message"]

    def test_unregister_nonexistent_activity_404(self, client):
        """Verify unregister from nonexistent activity returns 404"""
        response = client.delete("/activities/Nonexistent Activity/participants", params={"email": "test@test.edu"})
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_nonexistent_participant_404(self, client, reset_activities):
        """Verify unregister of nonexistent participant returns 404"""
        activity_name = "Chess Club"
        email = "notamember@test.edu"
        
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_unregister_multiple_participants(self, client, reset_activities):
        """Verify removing one participant doesn't affect others in same activity"""
        activity_name = "Chess Club"
        email1 = "michael@mergington.edu"
        email2 = "daniel@mergington.edu"
        
        # Both are initially in Chess Club
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]
        
        # Remove first participant
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email1})
        
        assert response.status_code == 200
        assert email1 not in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]

    def test_unregister_twice_second_fails(self, client, reset_activities):
        """Verify unregistering same student twice fails on second attempt"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        response1 = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        assert response1.status_code == 200
        
        # Second attempt should fail
        response2 = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        assert response2.status_code == 404
        assert "Participant not found" in response2.json()["detail"]

    def test_unregister_from_one_activity_doesnt_affect_another(self, client, reset_activities):
        """Verify unregistering from one activity doesn't affect other activities"""
        # Add same student to two activities
        email = "testuser@test.edu"
        client.post("/activities/Chess Club/signup", params={"email": email})
        client.post("/activities/Art Studio/signup", params={"email": email})
        
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Art Studio"]["participants"]
        
        # Remove from one activity
        response = client.delete("/activities/Chess Club/participants", params={"email": email})
        
        assert response.status_code == 200
        assert email not in activities["Chess Club"]["participants"]
        assert email in activities["Art Studio"]["participants"]

    def test_unregister_with_special_characters_in_email(self, client, reset_activities):
        """Verify unregister works with email addresses containing special characters"""
        activity_name = "Science Club"
        email = "john.doe+test@example.edu"
        
        # First sign up
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert email in activities[activity_name]["participants"]
        
        # Then unregister
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_unregister_case_sensitivity_in_activity_name(self, client, reset_activities):
        """Verify that activity names are case-sensitive in unregister"""
        response = client.delete("/activities/chess club/participants", params={"email": "test@test.edu"})
        
        # "chess club" (lowercase) should not match "Chess Club"
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_case_sensitivity_in_email(self, client, reset_activities):
        """Verify that emails are case-sensitive in unregister"""
        activity_name = "Chess Club"
        original_email = "michael@mergington.edu"
        different_case_email = "Michael@mergington.edu"
        
        # Original email is in the activity
        assert original_email in activities[activity_name]["participants"]
        
        # Trying to unregister with different case should fail
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": different_case_email})
        
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
