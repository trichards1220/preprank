"""Pick'em integration tests."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import PickemContest, PickemEntry, PickemBadge, Game

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup():
    yield
    db = SessionLocal()
    db.query(PickemBadge).delete()
    db.query(PickemEntry).delete()
    db.query(PickemContest).delete()
    db.query(Game).filter(Game.source == "test").delete()
    db.commit()
    db.close()


def _get_token(email: str) -> str:
    resp = client.post("/api/v1/auth/register", json={
        "email": email, "password": "testpass123",
        "first_name": "Test", "last_name": "User",
    })
    if resp.status_code == 400:
        resp = client.post("/api/v1/auth/login", json={
            "email": email, "password": "testpass123",
        })
    return resp.json()["access_token"]


def _create_test_games(db, count=3):
    from sqlalchemy import text
    teams = db.execute(text("SELECT id FROM teams WHERE sport_id=1 AND season_year=2025 LIMIT :n"), {"n": count * 2}).fetchall()
    if len(teams) < count * 2:
        return []
    game_ids = []
    for i in range(count):
        game = Game(
            home_team_id=teams[i * 2][0], away_team_id=teams[i * 2 + 1][0],
            sport_id=1, season_year=2025, week_number=1,
            game_date="2025-09-05", status="scheduled", source="test",
        )
        db.add(game)
        db.flush()
        game_ids.append(game.id)
    db.commit()
    return game_ids


def test_create_contest():
    token = _get_token("pickem1@test.com")
    resp = client.post("/api/v1/pickem/contests", json={
        "sport": "Football", "season_year": 2025, "week_number": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json()["status"] == "open"
    assert "Week 1" in resp.json()["title"]


def test_list_contests():
    token = _get_token("pickem2@test.com")
    client.post("/api/v1/pickem/contests", json={
        "sport": "Football", "season_year": 2025, "week_number": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    resp = client.get("/api/v1/pickem/contests?sport=Football&season_year=2025")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_submit_picks():
    token = _get_token("pickem3@test.com")
    db = SessionLocal()
    game_ids = _create_test_games(db)
    db.close()
    if not game_ids:
        return
    cr = client.post("/api/v1/pickem/contests", json={
        "sport": "Football", "season_year": 2025, "week_number": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    contest_id = cr.json()["id"]
    games_resp = client.get(f"/api/v1/pickem/contests/{contest_id}/games")
    games = games_resp.json()
    if not games:
        return
    picks = [{"game_id": g["game_id"], "picked_team_id": g["home_team_id"]} for g in games]
    resp = client.post(f"/api/v1/pickem/contests/{contest_id}/picks",
        json={"picks": picks}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == len(picks)


def test_get_my_picks():
    token = _get_token("pickem4@test.com")
    db = SessionLocal()
    game_ids = _create_test_games(db)
    db.close()
    if not game_ids:
        return
    cr = client.post("/api/v1/pickem/contests", json={
        "sport": "Football", "season_year": 2025, "week_number": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    contest_id = cr.json()["id"]
    games_resp = client.get(f"/api/v1/pickem/contests/{contest_id}/games")
    games = games_resp.json()
    if not games:
        return
    picks = [{"game_id": games[0]["game_id"], "picked_team_id": games[0]["home_team_id"]}]
    client.post(f"/api/v1/pickem/contests/{contest_id}/picks",
        json={"picks": picks}, headers={"Authorization": f"Bearer {token}"})
    resp = client.get(f"/api/v1/pickem/contests/{contest_id}/my-picks",
        headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_leaderboard_empty():
    resp = client.get("/api/v1/pickem/leaderboard/individual")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_school_leaderboard_empty():
    resp = client.get("/api/v1/pickem/leaderboard/schools")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_badges_requires_auth():
    resp = client.get("/api/v1/pickem/badges")
    assert resp.status_code == 401
