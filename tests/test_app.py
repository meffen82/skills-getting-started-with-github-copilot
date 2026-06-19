"""
FastAPI tests for Mergington High School Activities API
Uses Arrange-Act-Assert (AAA) pattern for clarity
"""
import pytest
from httpx import ASGITransport, AsyncClient
from src.app import app

transport = ASGITransport(app=app)
client = AsyncClient(transport=transport, base_url="http://testserver")

pytestmark = pytest.mark.anyio


class TestGetActivities:
    async def test_get_activities_returns_all_activities(self):
        # Arrange
        expected_keys = {"description", "schedule", "max_participants", "participants"}
        # Act
        response = await client.get("/activities")
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        first_activity = list(data.values())[0]
        assert expected_keys.issubset(set(first_activity.keys()))
        assert isinstance(first_activity["participants"], list)

    async def test_get_activities_includes_default_activities(self):
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        # Act
        response = await client.get("/activities")
        data = response.json()
        # Assert
        for activity in expected_activities:
            assert activity in data


class TestSignupForActivity:
    async def test_signup_success_adds_participant(self):
        # Arrange
        test_email = "newsignup@mergington.edu"
        activity_name = "Chess Club"
        # Act
        response = await client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
        # Assert
        assert response.status_code == 200
        activities = (await client.get("/activities")).json()
        assert test_email in activities[activity_name]["participants"]

    async def test_signup_for_nonexistent_activity_returns_404(self):
        # Arrange
        test_email = "student@mergington.edu"
        # Act
        response = await client.post("/activities/Nonexistent Club/signup", params={"email": test_email})
        # Assert
        assert response.status_code == 404

    async def test_signup_duplicate_email_returns_400(self):
        # Arrange
        test_email = "duplicate@mergington.edu"
        activity_name = "Programming Class"
        # Act - first signup
        r1 = await client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
        # Assert first succeeded
        assert r1.status_code == 200
        # Act - second signup
        r2 = await client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
        # Assert second failed
        assert r2.status_code == 400

    async def test_signup_missing_email_parameter_returns_422(self):
        # Act
        response = await client.post("/activities/Chess Club/signup")
        # Assert
        assert response.status_code == 422

    async def test_signup_allows_same_email_for_different_activities(self):
        # Arrange
        test_email = "multiactivity@mergington.edu"
        activities = ["Chess Club", "Programming Class"]
        # Act & Assert
        for activity in activities:
            r = await client.post(f"/activities/{activity}/signup", params={"email": test_email})
            assert r.status_code == 200
        all_activities = (await client.get("/activities")).json()
        for activity in activities:
            assert test_email in all_activities[activity]["participants"]


class TestRemoveParticipant:
    async def test_remove_participant_success(self):
        # Arrange
        test_email = "toremove@mergington.edu"
        activity_name = "Art Club"
        await client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
        # Act
        r = await client.delete(f"/activities/{activity_name}/remove", params={"email": test_email})
        # Assert
        assert r.status_code == 200
        activities = (await client.get("/activities")).json()
        assert test_email not in activities[activity_name]["participants"]

    async def test_remove_from_nonexistent_activity_returns_404(self):
        r = await client.delete("/activities/Nonexistent Club/remove", params={"email": "x@a.edu"})
        assert r.status_code == 404

    async def test_remove_nonexistent_participant_returns_404(self):
        r = await client.delete("/activities/Chess Club/remove", params={"email": "not@here.edu"})
        assert r.status_code == 404

    async def test_remove_missing_email_parameter_returns_422(self):
        r = await client.delete("/activities/Chess Club/remove")
        assert r.status_code == 422

    async def test_remove_then_rejoin_activity(self):
        test_email = "rejoin@mergington.edu"
        activity_name = "Drama Workshop"
        await client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
        r1 = await client.delete(f"/activities/{activity_name}/remove", params={"email": test_email})
        assert r1.status_code == 200
        r2 = await client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
        assert r2.status_code == 200


class TestActivityIntegration:
    async def test_full_lifecycle_signup_and_removal(self):
        test_email = "lifecycle@mergington.edu"
        activity_name = "Science Olympiad"
        initial = (await client.get("/activities")).json()
        initial_count = len(initial[activity_name]["participants"])
        r1 = await client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
        assert r1.status_code == 200
        after = (await client.get("/activities")).json()
        assert len(after[activity_name]["participants"]) == initial_count + 1
        r2 = await client.delete(f"/activities/{activity_name}/remove", params={"email": test_email})
        assert r2.status_code == 200
        final = (await client.get("/activities")).json()
        assert len(final[activity_name]["participants"]) == initial_count

    async def test_activity_availability_updates_correctly(self):
        activity_name = "Swimming Team"
        test_emails = [f"swimmer{i}@mergington.edu" for i in range(3)]
        initial_activities = (await client.get("/activities")).json()
        initial_spots = (
            initial_activities[activity_name]["max_participants"] -
            len(initial_activities[activity_name]["participants"])
        )
        for email in test_emails:
            await client.post(f"/activities/{activity_name}/signup", params={"email": email})
        updated_activities = (await client.get("/activities")).json()
        updated_spots = (
            updated_activities[activity_name]["max_participants"] -
            len(updated_activities[activity_name]["participants"])
        )
        assert updated_spots == initial_spots - len(test_emails)
