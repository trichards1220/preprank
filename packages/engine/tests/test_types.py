from engine.types import (
    TeamRecord, GameResult, GameStatus,
    SimulationConfig, ClassificationLevel,
)


def test_team_record_defaults():
    t = TeamRecord(team_id=1, school_name="Ruston", division="I", classification="5A")
    assert t.wins == 0
    assert t.losses == 0
    assert t.power_rating == 0.0
    assert t.games_played == 0


def test_team_record_games_played():
    t = TeamRecord(team_id=1, school_name="Ruston", division="I", classification="5A", wins=8, losses=2)
    assert t.games_played == 10


def test_game_result_construction():
    g = GameResult(
        game_id=1, home_team_id=1, away_team_id=2,
        home_score=28, away_score=14, status=GameStatus.FINAL,
    )
    assert g.home_won is True
    assert g.margin == 14


def test_game_result_away_win():
    g = GameResult(
        game_id=2, home_team_id=1, away_team_id=2,
        home_score=10, away_score=21, status=GameStatus.FINAL,
    )
    assert g.home_won is False
    assert g.margin == -11


def test_classification_level_ordering():
    assert ClassificationLevel.from_str("5A") > ClassificationLevel.from_str("3A")
    assert ClassificationLevel.from_str("1A") < ClassificationLevel.from_str("2A")
    assert ClassificationLevel.play_up_levels("3A", "5A") == 2
    assert ClassificationLevel.play_up_levels("5A", "3A") == 0


def test_simulation_config_defaults():
    cfg = SimulationConfig(sport_name="Football", season_year=2025, week_number=5)
    assert cfg.num_runs == 10000
    assert cfg.home_advantage == 0.5
    assert cfg.k_factor == 0.8
    assert cfg.playoff_spots == 8
