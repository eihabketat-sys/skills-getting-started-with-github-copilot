import copy

from fastapi.testclient import TestClient

from src.app import activities, app

original_activities = copy.deepcopy(activities)
client = TestClient(app)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activity_list():
    # Arrange
    reset_activities()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "teststudent@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email in activities[activity_name]["participants"]


def test_signup_for_existing_participant_returns_400():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    existing_email = original_activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    reset_activities()
    activity_name = "Nonexistent Club"
    email = "unknown@student.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_removes_participant():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = original_activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert email in response.json()["message"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    missing_email = "missing@student.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
