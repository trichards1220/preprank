"""Integration tests for simulation endpoints. Requires live PostgreSQL."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_simulation_run_returns_200():
    resp = client.post("/api/v1/simulations/run", json={
        "sport": "Football",
        "season_year": 2025,
        "week_number": 11,
        "num_runs": 100,
        "playoff_spots": 8,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("pending", "running", "completed")
    assert data["run_count"] == 100
    assert "id" in data


def test_simulation_run_bad_sport():
    resp = client.post("/api/v1/simulations/run", json={
        "sport": "Quidditch",
        "season_year": 2025,
        "week_number": 11,
    })
    assert resp.status_code == 404


def test_get_simulation_status():
    resp = client.post("/api/v1/simulations/run", json={
        "sport": "Football", "season_year": 2025, "week_number": 11, "num_runs": 10,
    })
    sim_id = resp.json()["id"]
    resp2 = client.get(f"/api/v1/simulations/{sim_id}")
    assert resp2.status_code == 200
    assert resp2.json()["id"] == sim_id


def test_get_simulation_not_found():
    resp = client.get("/api/v1/simulations/999999")
    assert resp.status_code == 404


def test_get_team_projections_not_found():
    resp = client.get("/api/v1/simulations/team/999999/projections")
    assert resp.status_code == 404
