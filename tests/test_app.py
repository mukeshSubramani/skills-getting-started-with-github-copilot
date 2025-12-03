"""
Tests for the Mergington High School Activities API
"""

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_activities_contain_expected_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

    def test_activities_have_participants_list(self):
        """Test that participants is a list"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""

    def test_signup_returns_200_for_valid_request(self):
        """Test that signup returns 200 for a valid request"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_adds_participant(self):
        """Test that signup adds a participant to the activity"""
        # Get initial participant count
        response = client.get("/activities")
        initial_participants = len(response.json()["Chess Club"]["participants"])

        # Sign up a new participant
        client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")

        # Check participant count increased
        response = client.get("/activities")
        final_participants = len(response.json()["Chess Club"]["participants"])
        assert final_participants == initial_participants + 1

    def test_signup_returns_404_for_invalid_activity(self):
        """Test that signup returns 404 for non-existent activity"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_signup_returns_400_for_duplicate_signup(self):
        """Test that signup returns 400 if student already signed up"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200

        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_returns_success_message(self):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=success@mergington.edu"
        )
        assert "Signed up" in response.json()["message"]
        assert "Chess Club" in response.json()["message"]


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_returns_200_for_valid_request(self):
        """Test that unregister returns 200 for a valid request"""
        email = "unreg_test@mergington.edu"
        
        # First sign up
        client.post(f"/activities/Chess%20Club/signup?email={email}")

        # Then unregister
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200

    def test_unregister_removes_participant(self):
        """Test that unregister removes a participant from the activity"""
        email = "remove_me@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        # Get participant count before unregister
        response = client.get("/activities")
        before_count = len(response.json()["Chess Club"]["participants"])

        # Unregister
        client.delete(f"/activities/Chess%20Club/unregister?email={email}")

        # Check participant count decreased
        response = client.get("/activities")
        after_count = len(response.json()["Chess Club"]["participants"])
        assert after_count == before_count - 1

    def test_unregister_returns_404_for_invalid_activity(self):
        """Test that unregister returns 404 for non-existent activity"""
        response = client.delete(
            "/activities/NonExistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_returns_400_for_not_signed_up(self):
        """Test that unregister returns 400 if student not signed up"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notsignedup@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_returns_success_message(self):
        """Test that unregister returns a success message"""
        email = "msg_test@mergington.edu"
        
        # Sign up first
        client.post(f"/activities/Chess%20Club/signup?email={email}")

        # Then unregister
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert "Unregistered" in response.json()["message"]
        assert "Chess Club" in response.json()["message"]


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
