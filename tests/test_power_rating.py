"""Tests for the LHSAA power rating calculation engine.

Validates the formula against hand-calculated examples.
"""

from app.engine.power_rating import (
    TeamRecord,
    GameResult,
    calculate_power_rating,
    calculate_play_up_points,
    calculate_opponent_wins_points,
)


def test_play_up_points_same_level():
    assert calculate_play_up_points(1, "5A", 1, "5A") == 0.0


def test_play_up_points_higher_opponent():
    # Opponent is 1 class higher
    assert calculate_play_up_points(1, "4A", 1, "5A") == 2.0
    # Opponent is 2 classes higher
    assert calculate_play_up_points(1, "3A", 1, "5A") == 4.0


def test_play_up_points_lower_opponent():
    # Playing down should yield 0
    assert calculate_play_up_points(1, "5A", 1, "3A") == 0.0


def test_opponent_wins_points():
    assert calculate_opponent_wins_points(8, 10) == 8.0
    assert calculate_opponent_wins_points(5, 10) == 5.0
    assert calculate_opponent_wins_points(0, 10) == 0.0
    assert calculate_opponent_wins_points(0, 0) == 0.0


def test_basic_power_rating():
    """Test a simple 3-game season with known results."""
    team_a = TeamRecord(team_id=1, classification="5A", division=1, wins=2, losses=1)
    team_b = TeamRecord(team_id=2, classification="5A", division=1, wins=3, losses=0)
    team_c = TeamRecord(team_id=3, classification="4A", division=1, wins=1, losses=2)
    team_d = TeamRecord(team_id=4, classification="5A", division=1, wins=0, losses=3)

    records = {1: team_a, 2: team_b, 3: team_c, 4: team_d}

    games_a = [
        GameResult(team_id=1, opponent_id=2, won=False, opponent_division=1, opponent_classification="5A"),
        GameResult(team_id=1, opponent_id=3, won=True, opponent_division=1, opponent_classification="4A"),
        GameResult(team_id=1, opponent_id=4, won=True, opponent_division=1, opponent_classification="5A"),
    ]

    result = calculate_power_rating(team_a, games_a, records)

    # Game 1 vs B (loss): 0 + 0 + (3/3)*10 = 10.0
    # Game 2 vs C (win, 4A): 10 + 0 + (1/3)*10 = 13.33
    # Game 3 vs D (win): 10 + 0 + (0/3)*10 = 10.0
    # Total: 33.33 / 3 = 11.11
    assert result.power_rating == 11.11
    assert len(result.game_details) == 3


def test_no_games():
    team = TeamRecord(team_id=1, classification="5A", division=1)
    result = calculate_power_rating(team, [], {})
    assert result.power_rating == 0.0
    assert result.strength_factor == 0.0
