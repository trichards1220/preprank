"""Tests for Monte Carlo simulation with a 4-team mini-league."""
import pytest
import numpy as np
from engine.types import (
    TeamRecord, GameResult, GameStatus,
    ScheduledGame, SimulationConfig, TeamProjection,
)
from engine.monte_carlo import run_simulation


def _make_4_team_league():
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
        3: TeamRecord(team_id=3, school_name="Gamma", division="I", classification="5A"),
        4: TeamRecord(team_id=4, school_name="Delta", division="I", classification="5A"),
    }
    played = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=28, away_score=14, status=GameStatus.FINAL),
        GameResult(game_id=2, home_team_id=3, away_team_id=4, home_score=21, away_score=7, status=GameStatus.FINAL),
        GameResult(game_id=3, home_team_id=1, away_team_id=3, home_score=17, away_score=10, status=GameStatus.FINAL),
    ]
    remaining = [
        ScheduledGame(game_id=4, home_team_id=2, away_team_id=3),
        ScheduledGame(game_id=5, home_team_id=4, away_team_id=1),
        ScheduledGame(game_id=6, home_team_id=2, away_team_id=4),
    ]
    config = SimulationConfig(
        sport_name="Football", season_year=2025, week_number=3,
        num_runs=1000, playoff_spots=2,
    )
    return teams, played, remaining, config


def test_simulation_returns_projections_for_all_teams():
    teams, played, remaining, config = _make_4_team_league()
    projections = run_simulation(teams, played, remaining, config)
    assert len(projections) == 4
    assert all(isinstance(p, TeamProjection) for p in projections.values())


def test_probabilities_between_0_and_100():
    teams, played, remaining, config = _make_4_team_league()
    projections = run_simulation(teams, played, remaining, config)
    for p in projections.values():
        assert 0.0 <= p.playoff_probability <= 100.0
        assert 0.0 <= p.championship_probability <= 100.0


def test_playoff_probabilities_reasonable():
    teams, played, remaining, config = _make_4_team_league()
    projections = run_simulation(teams, played, remaining, config, seed=42)
    assert projections[1].playoff_probability > projections[4].playoff_probability


def test_projected_wins_plus_losses_positive():
    teams, played, remaining, config = _make_4_team_league()
    projections = run_simulation(teams, played, remaining, config)
    for tid, p in projections.items():
        total = p.projected_wins_mean + p.projected_losses_mean
        assert total > 0


def test_rating_percentiles_ordered():
    teams, played, remaining, config = _make_4_team_league()
    projections = run_simulation(teams, played, remaining, config)
    for p in projections.values():
        assert p.projected_rating_p10 <= p.projected_rating_median <= p.projected_rating_p90


def test_deterministic_with_seed():
    teams, played, remaining, config = _make_4_team_league()
    p1 = run_simulation(teams, played, remaining, config, seed=42)
    p2 = run_simulation(teams, played, remaining, config, seed=42)
    for tid in teams:
        assert p1[tid].projected_rating_mean == pytest.approx(p2[tid].projected_rating_mean, abs=0.01)


def test_no_remaining_games():
    teams, played, _, config = _make_4_team_league()
    projections = run_simulation(teams, played, [], config)
    for p in projections.values():
        assert abs(p.projected_rating_p90 - p.projected_rating_p10) < 1.0
