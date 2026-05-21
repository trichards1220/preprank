import pytest
from engine.hype_score import calculate_hype_score, HypeInput, get_hype_label


def test_hype_label_on_fire():
    assert get_hype_label(95) == "ON FIRE"


def test_hype_label_surging():
    assert get_hype_label(75) == "SURGING"


def test_hype_label_steady():
    assert get_hype_label(55) == "STEADY"


def test_hype_label_cooling():
    assert get_hype_label(35) == "COOLING"


def test_hype_label_ice_cold():
    assert get_hype_label(15) == "ICE COLD"


def test_rising_team_high_hype():
    inp = HypeInput(
        weekly_ratings=[10.0, 11.0, 12.5, 14.0],
        wins=8, losses=1,
        current_win_streak=5,
        upset_wins=2,
        follower_count=50,
    )
    result = calculate_hype_score(inp)
    assert result.hype_score >= 70  # Should be SURGING or ON FIRE
    assert result.rating_velocity > 0
    assert result.hype_label in ("ON FIRE", "SURGING")


def test_falling_team_low_hype():
    inp = HypeInput(
        weekly_ratings=[14.0, 13.0, 11.5, 10.0],
        wins=2, losses=7,
        current_win_streak=0,
        upset_wins=0,
        follower_count=2,
    )
    result = calculate_hype_score(inp)
    assert result.hype_score < 40
    assert result.rating_velocity < 0
    assert result.hype_label in ("COOLING", "ICE COLD")


def test_steady_team():
    inp = HypeInput(
        weekly_ratings=[12.0, 12.1, 11.9, 12.0],
        wins=5, losses=5,
        current_win_streak=1,
        upset_wins=0,
        follower_count=10,
    )
    result = calculate_hype_score(inp)
    assert 30 <= result.hype_score <= 70


def test_no_games_minimal_hype():
    inp = HypeInput(
        weekly_ratings=[],
        wins=0, losses=0,
        current_win_streak=0,
        upset_wins=0,
        follower_count=0,
    )
    result = calculate_hype_score(inp)
    assert result.hype_score >= 0
    assert result.hype_score <= 30


def test_components_present():
    inp = HypeInput(
        weekly_ratings=[10.0, 12.0],
        wins=2, losses=0,
        current_win_streak=2,
        upset_wins=1,
        follower_count=5,
    )
    result = calculate_hype_score(inp)
    assert "velocity_score" in result.components
    assert "streak_score" in result.components
    assert "upset_score" in result.components
    assert "buzz_score" in result.components


def test_score_bounded():
    inp = HypeInput(
        weekly_ratings=[0.0, 20.0],  # extreme velocity
        wins=10, losses=0,
        current_win_streak=10,
        upset_wins=10,
        follower_count=10000,
    )
    result = calculate_hype_score(inp)
    assert 0 <= result.hype_score <= 100
