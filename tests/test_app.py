from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    # FastAPI's RedirectResponse uses 307 Temporary Redirect by default
    assert response.status_code in (200, 302, 307)  # Accept any valid redirect or success code
    if response.status_code != 200:  # Only check location if it's a redirect
        assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Test basic structure
    assert isinstance(data, dict)
    assert len(data) > 0
    
    # Test a specific activity structure
    chess_club = data.get("Chess Club")
    assert chess_club is not None
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]

    # Verify participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Using existing participant
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_nonexistent_activity():
    activity_name = "NonexistentClub"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]

def test_unregister_success():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Using existing participant
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]

    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]

def test_unregister_nonexistent_activity():
    activity_name = "NonexistentClub"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]