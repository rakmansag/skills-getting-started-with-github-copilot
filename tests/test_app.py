import pytest
from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity: at least one known activity exists
    assert "Chess Club" in data


def test_signup_and_remove_participant_flow():
    activity = "Chess Club"
    email = "test.student@example.com"

    # Ensure clean state: if the email already exists (from previous run), remove it
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    if email in data.get(activity, {}).get("participants", []):
        r = client.delete(f"/activities/{activity}/participants", params={"email": email})
        # allow 200 or 404 depending on state race
        assert r.status_code in (200, 404)

    # Sign up the test email
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Verify the participant was added
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email in data[activity]["participants"]

    # Remove the participant
    r = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r.status_code == 200
    assert "Removed" in r.json().get("message", "")

    # Verify removal
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email not in data[activity]["participants"]
