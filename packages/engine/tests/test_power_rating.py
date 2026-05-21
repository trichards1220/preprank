"""Tests for the LHSAA power rating calculator."""
import pytest
from engine.types import TeamRecord, GameResult, GameStatus
from engine.power_rating import (
    calculate_game_points,
    calculate_power_rating,
    calculate_strength_factor,
    calculate_all_ratings,
)


def test_win_gives_10_result_points():
    pts = calculate_game_points(
        won=True, my_classification="5A", opponent_classification="5A",
        opponent_wins=5, opponent_total_games=10,
    )
    assert pts == 15.0


def test_loss_gives_0_result_points():
    pts = calculate_game_points(
        won=False, my_classification="5A", opponent_classification="5A",
        opponent_wins=5, opponent_total_games=10,
    )
    assert pts == 5.0


def test_play_up_bonus_one_level():
    pts = calculate_game_points(
        won=True, my_classification="3A", opponent_classification="4A",
        opponent_wins=7, opponent_total_games=10,
    )
    assert pts == 19.0


def test_play_up_bonus_two_levels():
    pts = calculate_game_points(
        won=True, my_classification="3A", opponent_classification="5A",
        opponent_wins=6, opponent_total_games=10,
    )
    assert pts == 20.0


def test_play_down_no_bonus():
    pts = calculate_game_points(
        won=True, my_classification="5A", opponent_classification="3A",
        opponent_wins=8, opponent_total_games=10,
    )
    assert pts == 18.0


def test_opponent_undefeated():
    pts = calculate_game_points(
        won=False, my_classification="4A", opponent_classification="4A",
        opponent_wins=10, opponent_total_games=10,
    )
    assert pts == 10.0


def test_opponent_winless():
    pts = calculate_game_points(
        won=True, my_classification="4A", opponent_classification="4A",
        opponent_wins=0, opponent_total_games=10,
    )
    assert pts == 10.0


def test_opponent_zero_games_defaults_to_zero():
    pts = calculate_game_points(
        won=True, my_classification="4A", opponent_classification="4A",
        opponent_wins=0, opponent_total_games=0,
    )
    assert pts == 10.0


def test_power_rating_simple_season():
    game_points = [15.0, 18.0]
    rating = calculate_power_rating(game_points)
    assert rating == pytest.approx(16.50)


def test_power_rating_rounds_to_hundredths():
    game_points = [15.0, 18.0, 12.0]
    rating = calculate_power_rating(game_points)
    assert rating == pytest.approx(15.0)


def test_power_rating_no_games():
    rating = calculate_power_rating([])
    assert rating == 0.0


def test_strength_factor_basic():
    opponent_ratings = [12.0, 14.0, 10.0]
    sf = calculate_strength_factor(opponent_ratings)
    assert sf == pytest.approx(12.0)


def test_strength_factor_no_opponents():
    sf = calculate_strength_factor([])
    assert sf == 0.0


def test_calculate_all_ratings_simple_league():
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
        3: TeamRecord(team_id=3, school_name="Gamma", division="I", classification="5A"),
    }
    games = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=21, away_score=14, status=GameStatus.FINAL),
        GameResult(game_id=2, home_team_id=2, away_team_id=3, home_score=28, away_score=7, status=GameStatus.FINAL),
        GameResult(game_id=3, home_team_id=3, away_team_id=1, home_score=17, away_score=10, status=GameStatus.FINAL),
    ]
    result = calculate_all_ratings(teams, games)
    assert len(result) == 3
    for t in result.values():
        assert t.wins == 1
        assert t.losses == 1
        assert t.power_rating > 0


def test_cancelled_games_excluded():
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
    }
    games = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=21, away_score=14, status=GameStatus.FINAL),
        GameResult(game_id=2, home_team_id=2, away_team_id=1, status=GameStatus.CANCELLED),
    ]
    result = calculate_all_ratings(teams, games)
    assert result[1].wins == 1
    assert result[1].losses == 0
    assert result[1].games_played == 1


def test_disputed_games_excluded():
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
    }
    games = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=21, away_score=14, status=GameStatus.DISPUTED),
    ]
    result = calculate_all_ratings(teams, games)
    assert result[1].games_played == 0
    assert result[1].power_rating == 0.0


def test_forfeit_counts_as_win_loss():
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
    }
    games = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=1, away_score=0,
                   status=GameStatus.FORFEIT, is_forfeit=True),
    ]
    result = calculate_all_ratings(teams, games)
    assert result[1].wins == 1
    assert result[2].losses == 1


def test_convergence_changes_opponent_wins():
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
        3: TeamRecord(team_id=3, school_name="Gamma", division="I", classification="5A"),
    }
    games = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=21, away_score=14, status=GameStatus.FINAL),
        GameResult(game_id=2, home_team_id=2, away_team_id=3, home_score=28, away_score=7, status=GameStatus.FINAL),
    ]
    result = calculate_all_ratings(teams, games)
    assert result[1].wins == 1
    assert result[1].losses == 0
    assert result[1].power_rating == pytest.approx(15.0, abs=0.5)


def test_play_up_in_full_calculation():
    teams = {
        1: TeamRecord(team_id=1, school_name="Small School", division="IV", classification="2A"),
        2: TeamRecord(team_id=2, school_name="Big School", division="I", classification="5A"),
    }
    games = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=21, away_score=14, status=GameStatus.FINAL),
    ]
    result = calculate_all_ratings(teams, games)
    assert result[1].power_rating == pytest.approx(16.0, abs=0.5)


def test_large_league_no_errors():
    import random
    random.seed(42)
    teams = {}
    classifications = ["5A", "4A", "3A", "2A", "1A"]
    divisions = ["I", "II", "III", "IV", "V"]
    for i in range(1, 299):
        idx = (i - 1) % 5
        teams[i] = TeamRecord(
            team_id=i, school_name=f"School_{i}",
            division=divisions[idx], classification=classifications[idx],
        )
    games = []
    for gid in range(1, 501):
        h, a = random.sample(range(1, 299), 2)
        games.append(GameResult(
            game_id=gid, home_team_id=h, away_team_id=a,
            home_score=random.randint(0, 50), away_score=random.randint(0, 50),
            status=GameStatus.FINAL,
        ))
    result = calculate_all_ratings(teams, games)
    assert len(result) == 298
    for t in result.values():
        assert t.power_rating >= 0
