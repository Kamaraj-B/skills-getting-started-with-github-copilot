import copy
from fastapi.testclient import TestClient
import src.app as app_module

# Keep a deep copy of the original in-memory state so tests are isolated
_ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


def setup_function():
    # Arrange: reset server state before each test
    app_module.activities = copy.deepcopy(_ORIGINAL_ACTIVITIES)


client = TestClient(app_module.app)


def test_get_activities_returns_expected_structure():
    # Arrange: (done in setup_function)

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_updates_state_and_prevents_duplicate():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act - signup
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert - signup succeeded and server state changed
    assert resp.status_code == 200
    participants = client.get("/activities").json()[activity]["participants"]
    assert email in participants

    # Act - duplicate signup should fail (global duplicate check)
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert - duplicate prevented
    assert resp2.status_code == 400


def test_remove_participant_success_and_404_for_missing():
    # Arrange
    activity = "Programming Class"
    email = "sophia@mergington.edu"

    # Act - remove existing participant
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert - removed
    assert resp.status_code == 200
    participants = client.get("/activities").json()[activity]["participants"]
    assert email not in participants

    # Act - remove again (now missing)
    resp2 = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert - 404 for missing
    assert resp2.status_code == 404


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    email = "a@b.com"
    unknown = "Nonexistent Club"

    # Act
    resp = client.post(f"/activities/{unknown}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 404
