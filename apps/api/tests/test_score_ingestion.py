import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Game

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_test_games():
    """Delete any games created during tests."""
    yield
    db = SessionLocal()
    db.query(Game).filter(Game.source == "user").delete()
    db.commit()
    db.close()


def test_create_game():
    """POST /games/ with valid team IDs should create a game."""
    # Get two valid team IDs
    teams_resp = client.get("/api/v1/teams/?sport=Football&season_year=2025&limit=2")
    teams = teams_resp.json()
    if len(teams) < 2:
        return  # No seed data

    resp = client.post("/api/v1/games/", json={
        "home_team_id": teams[0]["id"],
        "away_team_id": teams[1]["id"],
        "sport_id": teams[0]["sport_id"],
        "season_year": 2025,
        "game_date": "2025-09-05",
        "week_number": 1,
        "home_score": 28,
        "away_score": 14,
        "status": "final",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["home_score"] == 28
    assert data["away_score"] == 14


def test_create_game_bad_team():
    resp = client.post("/api/v1/games/", json={
        "home_team_id": 999999,
        "away_team_id": 999998,
        "sport_id": 1,
        "season_year": 2025,
        "game_date": "2025-09-05",
    })
    assert resp.status_code == 404


def test_update_game_score():
    # Create a game first
    teams_resp = client.get("/api/v1/teams/?sport=Football&season_year=2025&limit=2")
    teams = teams_resp.json()
    if len(teams) < 2:
        return

    create_resp = client.post("/api/v1/games/", json={
        "home_team_id": teams[0]["id"],
        "away_team_id": teams[1]["id"],
        "sport_id": teams[0]["sport_id"],
        "season_year": 2025,
        "game_date": "2025-09-12",
        "week_number": 2,
        "status": "scheduled",
    })
    game_id = create_resp.json()["id"]

    # Update score
    resp = client.patch(f"/api/v1/games/{game_id}", json={
        "home_score": 35,
        "away_score": 21,
        "status": "final",
    })
    assert resp.status_code == 200
    assert resp.json()["home_score"] == 35
    assert resp.json()["status"] == "final"


def test_recalculate_ratings():
    resp = client.post("/api/v1/ratings/recalculate?sport=Football&season_year=2025&week_number=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["teams_updated"] > 0


def test_parse_lhsaa_html():
    """Test the HTML parser with mock LHSAA-style HTML."""
    from app.services.score_ingestion import parse_lhsaa_scores

    html = """
    <table>
        <tr><td>Ruston</td><td>28</td><td>Neville</td><td>14</td></tr>
        <tr><td>Parkway</td><td>35</td><td>Airline</td><td>21</td></tr>
    </table>
    """
    games = parse_lhsaa_scores(html)
    assert len(games) >= 2
    assert games[0]["home_team"] == "Ruston"
    assert games[0]["home_score"] == 28
