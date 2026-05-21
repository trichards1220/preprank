"""Performance tests for the Monte Carlo engine."""
import time
import random
import pytest
from engine.types import (
    TeamRecord, GameResult, GameStatus,
    ScheduledGame, SimulationConfig,
)
from engine.monte_carlo import run_simulation


def _build_298_team_league(num_played=400, num_remaining=400, seed=42):
    rng = random.Random(seed)
    classifications = ["5A", "4A", "3A", "2A"]
    divisions = ["I", "II", "III", "IV"]
    teams = {}
    for i in range(1, 299):
        idx = (i - 1) % 4
        teams[i] = TeamRecord(
            team_id=i, school_name=f"School_{i}",
            division=divisions[idx], classification=classifications[idx],
        )
    played = []
    for gid in range(1, num_played + 1):
        h, a = rng.sample(range(1, 299), 2)
        played.append(GameResult(
            game_id=gid, home_team_id=h, away_team_id=a,
            home_score=rng.randint(0, 50), away_score=rng.randint(0, 50),
            status=GameStatus.FINAL,
        ))
    remaining = []
    for gid in range(num_played + 1, num_played + num_remaining + 1):
        h, a = rng.sample(range(1, 299), 2)
        remaining.append(ScheduledGame(game_id=gid, home_team_id=h, away_team_id=a))
    return teams, played, remaining


def test_298_team_simulation_under_60_seconds():
    """Full 298-team football simulation with 10,000 runs must complete in < 60s."""
    teams, played, remaining = _build_298_team_league(num_played=400, num_remaining=400)
    config = SimulationConfig(
        sport_name="Football", season_year=2025, week_number=5,
        num_runs=10000, playoff_spots=8,
    )
    start = time.time()
    projections = run_simulation(teams, played, remaining, config, seed=42)
    elapsed = time.time() - start
    assert len(projections) == 298
    assert elapsed < 60.0, f"Simulation took {elapsed:.1f}s, must be under 60s"
    print(f"\n  298-team, 10K runs: {elapsed:.1f}s")


def test_small_simulation_fast():
    """20-team, 1000 runs should be very fast."""
    rng = random.Random(42)
    teams = {}
    for i in range(1, 21):
        teams[i] = TeamRecord(team_id=i, school_name=f"School_{i}", division="I", classification="5A")
    played = []
    for gid in range(1, 31):
        h, a = rng.sample(range(1, 21), 2)
        played.append(GameResult(
            game_id=gid, home_team_id=h, away_team_id=a,
            home_score=rng.randint(0, 50), away_score=rng.randint(0, 50),
            status=GameStatus.FINAL,
        ))
    remaining = []
    for gid in range(31, 51):
        h, a = rng.sample(range(1, 21), 2)
        remaining.append(ScheduledGame(game_id=gid, home_team_id=h, away_team_id=a))
    config = SimulationConfig(
        sport_name="Football", season_year=2025, week_number=5,
        num_runs=1000, playoff_spots=4,
    )
    start = time.time()
    projections = run_simulation(teams, played, remaining, config, seed=42)
    elapsed = time.time() - start
    assert elapsed < 10.0
    print(f"\n  20-team, 1K runs: {elapsed:.1f}s")
