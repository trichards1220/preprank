"""Tests for game impact analysis."""
import pytest
from engine.types import (
    TeamRecord, GameResult, GameStatus,
    ScheduledGame, SimulationConfig, GameImpact,
)
from engine.impact import analyze_game_impact


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
    ]
    remaining = [
        ScheduledGame(game_id=3, home_team_id=1, away_team_id=3),
        ScheduledGame(game_id=4, home_team_id=2, away_team_id=4),
    ]
    config = SimulationConfig(
        sport_name="Football", season_year=2025, week_number=2,
        num_runs=500, playoff_spots=2,
    )
    return teams, played, remaining, config


def test_impact_returns_all_division_teams():
    teams, played, remaining, config = _make_4_team_league()
    target_game = remaining[0]
    impacts = analyze_game_impact(teams, played, remaining, target_game, config, seed=42)
    assert len(impacts) == 4
    assert all(isinstance(imp, GameImpact) for imp in impacts)


def test_impact_game_id_matches():
    teams, played, remaining, config = _make_4_team_league()
    target_game = remaining[0]
    impacts = analyze_game_impact(teams, played, remaining, target_game, config, seed=42)
    for imp in impacts:
        assert imp.game_id == target_game.game_id


def test_impact_shows_different_outcomes():
    teams, played, remaining, config = _make_4_team_league()
    target_game = remaining[0]
    impacts = analyze_game_impact(teams, played, remaining, target_game, config, seed=42)
    team1_impact = next(i for i in impacts if i.affected_team_id == 1)
    assert team1_impact.rating_if_home_wins >= team1_impact.rating_if_away_wins


def test_impact_ripple_effects():
    teams, played, remaining, config = _make_4_team_league()
    target_game = remaining[0]
    impacts = analyze_game_impact(teams, played, remaining, target_game, config, seed=42)
    team2_impact = next(i for i in impacts if i.affected_team_id == 2)
    assert team2_impact.rating_if_home_wins > 0
    assert team2_impact.rating_if_away_wins > 0
