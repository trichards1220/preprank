"""Scenario builder tests."""
import pytest
from engine.types import TeamRecord, GameResult, GameStatus, ScheduledGame, SimulationConfig
from engine.scenario import calculate_scenario, calculate_best_case, calculate_worst_case


def _make_league():
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
        3: TeamRecord(team_id=3, school_name="Gamma", division="I", classification="5A"),
        4: TeamRecord(team_id=4, school_name="Delta", division="I", classification="5A"),
    }
    played = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=28, away_score=14, status=GameStatus.FINAL),
        GameResult(game_id=2, home_team_id=3, away_team_id=4, home_score=21, away_score=7, status=GameStatus.FINAL),
    ]
    remaining = [
        ScheduledGame(game_id=3, home_team_id=1, away_team_id=3, week_number=2),
        ScheduledGame(game_id=4, home_team_id=2, away_team_id=4, week_number=2),
        ScheduledGame(game_id=5, home_team_id=1, away_team_id=4, week_number=3),
        ScheduledGame(game_id=6, home_team_id=2, away_team_id=3, week_number=3),
    ]
    config = SimulationConfig(sport_name="Football", season_year=2025, week_number=1, num_runs=200, playoff_spots=2)
    return teams, played, remaining, config


def test_scenario_returns_target_projection():
    teams, played, remaining, config = _make_league()
    result = calculate_scenario(
        teams, played, remaining,
        locked_outcomes=[{"game_id": 3, "winner_team_id": 1}],
        target_team_id=1, config=config, seed=42,
    )
    assert result["target"] is not None
    assert result["target"].team_id == 1
    assert result["locked_count"] == 1
    assert result["remaining_count"] == 3


def test_scenario_all_locked():
    teams, played, remaining, config = _make_league()
    locked = [
        {"game_id": 3, "winner_team_id": 1},
        {"game_id": 4, "winner_team_id": 2},
        {"game_id": 5, "winner_team_id": 1},
        {"game_id": 6, "winner_team_id": 2},
    ]
    result = calculate_scenario(teams, played, remaining, locked, target_team_id=1, config=config)
    assert result["remaining_count"] == 0
    assert result["target"].projected_rating_mean > 0


def test_best_case_better_than_worst():
    teams, played, remaining, config = _make_league()
    best = calculate_best_case(teams, played, remaining, target_team_id=1, config=config)
    worst = calculate_worst_case(teams, played, remaining, target_team_id=1, config=config)
    assert best["target"].projected_rating_mean >= worst["target"].projected_rating_mean


def test_best_case_high_playoff_prob():
    teams, played, remaining, config = _make_league()
    best = calculate_best_case(teams, played, remaining, target_team_id=1, config=config)
    assert best["target"].playoff_probability >= 50.0


def test_worst_case_returns_projection():
    teams, played, remaining, config = _make_league()
    worst = calculate_worst_case(teams, played, remaining, target_team_id=1, config=config)
    assert worst["target"] is not None
    assert worst["target"].team_id == 1


def test_scenario_speed():
    """Scenario with 4 teams should be fast."""
    import time
    teams, played, remaining, config = _make_league()
    start = time.time()
    calculate_scenario(teams, played, remaining,
        locked_outcomes=[{"game_id": 3, "winner_team_id": 1}],
        target_team_id=1, config=config)
    elapsed = time.time() - start
    assert elapsed < 5.0
