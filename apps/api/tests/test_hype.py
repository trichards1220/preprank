from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_trending_empty():
    resp = client.get("/api/v1/hype/trending?season_year=2025")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_risers_empty():
    resp = client.get("/api/v1/hype/risers?season_year=2025")
    assert resp.status_code == 200


def test_fallers_empty():
    resp = client.get("/api/v1/hype/fallers?season_year=2025")
    assert resp.status_code == 200


def test_team_hype_not_found():
    resp = client.get("/api/v1/hype/team/999999")
    assert resp.status_code == 404
