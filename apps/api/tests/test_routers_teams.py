from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_teams_returns_200():
    response = client.get("/api/v1/teams/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_teams_filter_by_sport():
    response = client.get("/api/v1/teams/?sport=Football")
    assert response.status_code == 200


def test_list_teams_filter_by_season_year():
    response = client.get("/api/v1/teams/?season_year=2025")
    assert response.status_code == 200
    for team in response.json():
        assert team["season_year"] == 2025


def test_list_teams_filter_by_division():
    response = client.get("/api/v1/teams/?division=I")
    assert response.status_code == 200
    for team in response.json():
        assert team["division"] == "I"


def test_get_team_not_found():
    response = client.get("/api/v1/teams/999999")
    assert response.status_code == 404
