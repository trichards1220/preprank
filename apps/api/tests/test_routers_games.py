from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_games_returns_200():
    response = client.get("/api/v1/games/?season_year=2025&sport=Football")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_games_filter_by_week():
    response = client.get("/api/v1/games/?season_year=2025&sport=Football&week_number=1")
    assert response.status_code == 200


def test_list_games_filter_by_status():
    response = client.get("/api/v1/games/?season_year=2025&sport=Football&status=final")
    assert response.status_code == 200


def test_get_game_not_found():
    response = client.get("/api/v1/games/999999")
    assert response.status_code == 404
