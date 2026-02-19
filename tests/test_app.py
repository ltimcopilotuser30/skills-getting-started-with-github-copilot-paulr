import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    from src.app import activities
    
    original_activities = {
        "Chess Club ♟️": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class 💻": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class 🏋️": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Club ⚽": {
            "description": "Team drills, scrimmages, and friendly matches",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Club 🏀": {
            "description": "Skill development, teamwork, and after-school games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"]
        },
        "Painting Workshop 🎨": {
            "description": "Explore watercolor, acrylic, and mixed media techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "charlotte@mergington.edu"]
        },
        "Drama Club 🎭": {
            "description": "Acting exercises, improv, and school play preparation",
            "schedule": "Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
        },
        "Robotics Club 🤖": {
            "description": "Design, build, and program robots for competitions",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["ethan@mergington.edu", "james@mergington.edu"]
        },
        "Math Olympiad Prep 🧮": {
            "description": "Practice advanced problem-solving for math contests",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["lucas@mergington.edu", "alexander@mergington.edu"]
        }
    }
    
    # Clear and repopulate
    activities.clear()
    activities.update(original_activities)
    yield
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, reset_activities):
        """Should return all activities with participants."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club ♟️" in data
        assert "Programming Class 💻" in data
        
    def test_activities_contain_required_fields(self, reset_activities):
        """Each activity should have required fields."""
        response = client.get("/activities")
        data = response.json()
        first_activity = data["Chess Club ♟️"]
        
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        
    def test_activities_participant_count(self, reset_activities):
        """Participant list should match expected count."""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club ♟️"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club ♟️"]["participants"]


class TestSignup:
    """Test POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant(self, reset_activities):
        """Should successfully sign up a new participant."""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club ♟️"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify side effect
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        
    def test_signup_nonexistent_activity(self):
        """Should return 404 for non-existent activity."""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
        
    def test_signup_duplicate_participant(self, reset_activities):
        """Should prevent duplicate signups with 400 error."""
        response = client.post(
            "/activities/Chess Club ♟️/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
        
    def test_signup_multiple_activities(self, reset_activities):
        """Same student should be able to sign up for multiple activities."""
        # Arrange
        email = "versatile@mergington.edu"
        activities = ["Chess Club ♟️", "Programming Class 💻"]
        
        # Act
        response1 = client.post(f"/activities/{activities[0]}/signup?email={email}")
        response2 = client.post(f"/activities/{activities[1]}/signup?email={email}")
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify side effect
        data = client.get("/activities").json()
        assert email in data[activities[0]]["participants"]
        assert email in data[activities[1]]["participants"]


class TestRemoveParticipant:
    """Test DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_remove_existing_participant(self, reset_activities):
        """Should successfully remove a participant."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club ♟️"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify side effect
        data = client.get("/activities").json()
        assert email not in data[activity]["participants"]
        
    def test_remove_from_nonexistent_activity(self):
        """Should return 404 for non-existent activity."""
        response = client.delete(
            "/activities/Nonexistent Club/participants?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        
    def test_remove_nonexistent_participant(self, reset_activities):
        """Should return 404 when removing non-existent participant."""
        response = client.delete(
            "/activities/Chess Club ♟️/participants?email=notamember@mergington.edu"
        )
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"]
        
    def test_signup_after_removal(self, reset_activities):
        """Should be able to re-signup after being removed."""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club ♟️"
        
        # Act: Remove participant
        remove_response = client.delete(
            f"/activities/{activity}/participants?email={email}"
        )
        
        # Assert: Removal successful
        assert remove_response.status_code == 200
        data = client.get("/activities").json()
        assert email not in data[activity]["participants"]
        
        # Act: Re-signup
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert: Re-signup successful
        assert signup_response.status_code == 200
        data = client.get("/activities").json()
        assert email in data[activity]["participants"]


class TestRootEndpoint:
    """Test GET / endpoint."""
    
    def test_root_redirects_to_static(self):
        """Root should redirect to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307


class TestEmailEncoding:
    """Test that email parameters are properly encoded."""
    
    def test_signup_with_special_characters(self, reset_activities):
        """Should handle email-like parameters with special characters."""
        email = "test+special@mergington.edu"
        response = client.post(
            f"/activities/Chess Club ♟️/signup?email={email.replace('+', '%2B')}"
        )
        assert response.status_code == 200
        
        # Verify in participants
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club ♟️"]["participants"]
