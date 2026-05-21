"""'What's At Stake' game impact analysis.

For a target game, run two simulation scenarios:
1. Lock home team winning, simulate rest normally
2. Lock away team winning, simulate rest normally

Compare projections across both scenarios for every affected team.
"""
from __future__ import annotations

from engine.types import (
    TeamRecord, GameResult, GameStatus,
    ScheduledGame, SimulationConfig, GameImpact,
)
from engine.monte_carlo import run_simulation


def analyze_game_impact(
    teams: dict[int, TeamRecord],
    played_games: list[GameResult],
    remaining_games: list[ScheduledGame],
    target_game: ScheduledGame,
    config: SimulationConfig,
    seed: int | None = None,
) -> list[GameImpact]:
    """Analyze how a specific game's outcome affects all teams in the same divisions."""
    other_remaining = [g for g in remaining_games if g.game_id != target_game.game_id]

    # Scenario 1: Home team wins
    home_win_result = GameResult(
        game_id=target_game.game_id,
        home_team_id=target_game.home_team_id,
        away_team_id=target_game.away_team_id,
        home_score=1, away_score=0, status=GameStatus.FINAL,
    )
    played_home_wins = played_games + [home_win_result]
    proj_home = run_simulation(teams, played_home_wins, other_remaining, config, seed=seed)

    # Scenario 2: Away team wins
    away_win_result = GameResult(
        game_id=target_game.game_id,
        home_team_id=target_game.home_team_id,
        away_team_id=target_game.away_team_id,
        home_score=0, away_score=1, status=GameStatus.FINAL,
    )
    played_away_wins = played_games + [away_win_result]
    proj_away = run_simulation(teams, played_away_wins, other_remaining, config, seed=seed)

    # Find affected teams (same division as either participant)
    home_div = teams[target_game.home_team_id].division
    away_div = teams[target_game.away_team_id].division
    affected_divs = {home_div, away_div}
    affected_ids = [tid for tid, t in teams.items() if t.division in affected_divs]

    impacts: list[GameImpact] = []
    for tid in affected_ids:
        ph = proj_home[tid]
        pa = proj_away[tid]
        impacts.append(GameImpact(
            game_id=target_game.game_id,
            affected_team_id=tid,
            rating_if_home_wins=ph.projected_rating_mean,
            rating_if_away_wins=pa.projected_rating_mean,
            rank_if_home_wins=round(ph.projected_rank_mean),
            rank_if_away_wins=round(pa.projected_rank_mean),
            playoff_prob_if_home_wins=ph.playoff_probability,
            playoff_prob_if_away_wins=pa.playoff_probability,
        ))

    return impacts
