from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_rankings_returns_200():
    response = client.get("/api/v1/ratings/rankings?sport=Football&season_year=2025&week_number=11")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_rankings_filter_by_division():
    response = client.get("/api/v1/ratings/rankings?sport=Football&season_year=2025&week_number=11&division=I")
    assert response.status_code == 200
    for entry in response.json():
        assert entry["division"] == "I"


def test_list_rankings_ordered_by_rank():
    response = client.get("/api/v1/ratings/rankings?sport=Football&season_year=2025&week_number=11&division=I")
    data = response.json()
    if len(data) >= 2:
        for i in range(len(data) - 1):
            assert data[i]["rank"] <= data[i + 1]["rank"]


def test_get_team_ratings_history():
    resp = client.get("/api/v1/ratings/rankings?sport=Football&season_year=2025&week_number=11&limit=1")
    data = resp.json()
    if len(data) == 0:
        return
    team_id = data[0]["team_id"]
    response = client.get(f"/api/v1/ratings/{team_id}?season_year=2025")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_team_ratings_not_found():
    response = client.get("/api/v1/ratings/999999?season_year=2025")
    assert response.status_code == 200
    assert response.json() == []
