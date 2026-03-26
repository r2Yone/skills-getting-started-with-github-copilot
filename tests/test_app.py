"""
Tests for the Mergington High School API

Comprehensive test suite covering all endpoints and edge cases for the
extracurricular activities management system.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Art Painting": {
            "description": "Explore painting techniques and create original artwork",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Band": {
            "description": "Join the school band and perform at events",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific discoveries",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ethan@mergington.edu", "grace@mergington.edu"]
        }
    }

    activities.clear()
    activities.update(initial_activities)
    yield
    activities.clear()
    activities.update(initial_activities)


class TestRootEndpoint:
    def test_root_redirects_to_static(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Music Band" in data

    def test_activities_have_required_fields(self, client):
        response = client.get("/activities")
        data = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]

        for name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data

    def test_activities_participants_is_list(self, client):
        response = client.get("/activities")
        data = response.json()

        for activity_data in data.values():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    def test_signup_successful(self, client):
        email = "test@mergington.edu"
        response = client.post("/activities/Chess Club/signup", params={"email": email})
        assert response.status_code == 200
        assert email in activities["Chess Club"]["participants"]

    def test_duplicate_signup_fails(self, client):
        email = "michael@mergington.edu"
        response = client.post("/activities/Chess Club/signup", params={"email": email})
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity(self, client):
        response = client.post("/activities/NotAnActivity/signup", params={"email": "a@b.com"})
        assert response.status_code == 404


class TestUnregisterFromActivity:
    def test_unregister_successful(self, client):
        email = "michael@mergington.edu"
        response = client.delete("/activities/Chess Club/signup", params={"email": email})
        assert response.status_code == 200
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        response = client.delete("/activities/NotAnActivity/signup", params={"email": "a@b.com"})
        assert response.status_code == 404

    def test_unregister_nonexistent_participant(self, client):
        response = client.delete("/activities/Chess Club/signup", params={"email": "unknown@mergington.edu"})
        assert response.status_code == 404

    def test_unregister_and_rejoin(self, client):
        email = "rejoin@mergington.edu"
        activity = "Art Painting"

        response1 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response1.status_code == 200

        response2 = client.delete(f"/activities/{activity}/signup", params={"email": email})
        assert response2.status_code == 200

        response3 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response3.status_code == 200

        assert email in activities[activity]["participants"]
