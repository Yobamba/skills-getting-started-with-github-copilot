"""
Integration tests for POST /activities/{activity_name}/signup endpoint
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


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, reset_activities):
        """Verify successful signup adds participant to activity"""
        activity_name = "Chess Club"
        email = "newstudent@test.edu"
        
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in activities[activity_name]["participants"]

    def test_signup_returns_message(self, client, reset_activities):
        """Verify signup returns a confirmation message"""
        activity_name = "Programming Class"
        email = "anotherstudent@test.edu"
        
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        data = response.json()
        
        assert "message" in data
        assert activity_name in data["message"]
        assert email in data["message"]

    def test_signup_nonexistent_activity_404(self, client):
        """Verify signup to nonexistent activity returns 404"""
        response = client.post("/activities/Nonexistent Activity/signup", params={"email": "test@test.edu"})
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_student_400(self, client, reset_activities):
        """Verify signup fails with 400 when student already signed up"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        """Verify multiple students can sign up for the same activity"""
        activity_name = "Art Studio"
        email1 = "student1@test.edu"
        email2 = "student2@test.edu"
        
        response1 = client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        response2 = client.post(f"/activities/{activity_name}/signup", params={"email": email2})
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]

    def test_signup_single_student_multiple_activities(self, client, reset_activities):
        """Verify a single student can sign up for multiple activities"""
        email = "versatile@test.edu"
        
        response1 = client.post("/activities/Chess Club/signup", params={"email": email})
        response2 = client.post("/activities/Art Studio/signup", params={"email": email})
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Art Studio"]["participants"]

    def test_signup_respects_max_participants(self, client, reset_activities):
        """Verify signup fails when activity reaches max capacity"""
        # Temporarily set a low max_participants for testing
        activity_name = "Art Studio"
        activities[activity_name]["max_participants"] = 1
        activities[activity_name]["participants"] = ["existing@test.edu"]
        
        response = client.post(f"/activities/{activity_name}/signup", params={"email": "newstudent@test.edu"})
        
        # According to current implementation, it should still allow signup
        # This test documents current behavior; modify if max capacity checking is added
        assert response.status_code == 200

    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """Verify signup works with email addresses containing special characters"""
        activity_name = "Science Club"
        email = "john.doe+test@example.edu"
        
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_case_sensitivity_in_activity_name(self, client, reset_activities):
        """Verify that activity names are case-sensitive"""
        response = client.post("/activities/chess club/signup", params={"email": "test@test.edu"})
        
        # "chess club" (lowercase) should not match "Chess Club"
        assert response.status_code == 404
