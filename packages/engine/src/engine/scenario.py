"""What-If Scenario Builder engine.

Users lock specific game outcomes, then we simulate the remaining games
with Monte Carlo (1,000 runs for interactivity speed).
"""
from __future__ import annotations

from engine.types import (
    TeamRecord, GameResult, GameStatus,
    ScheduledGame, SimulationConfig, TeamProjection,
)
from engine.monte_carlo import run_simulation
from engine.power_rating import calculate_all_ratings


def calculate_scenario(
    teams: dict[int, TeamRecord],
    played_games: list[GameResult],
    remaining_games: list[ScheduledGame],
    locked_outcomes: list[dict],  # [{game_id, winner_team_id}, ...]
    target_team_id: int,
    config: SimulationConfig | None = None,
    seed: int | None = None,
) -> dict:
    """Calculate projections with specific game outcomes locked.

    Args:
        locked_outcomes: list of {game_id: int, winner_team_id: int} — these games
            are resolved as final before simulation
        target_team_id: the team the user cares about

    Returns:
        dict with target team's projection + all team projections
    """
    if config is None:
        config = SimulationConfig(
            sport_name="Football", season_year=2025, week_number=1,
            num_runs=1000, playoff_spots=8,
        )

    # Separate locked games from remaining
    locked_ids = {lo["game_id"] for lo in locked_outcomes}
    locked_map = {lo["game_id"]: lo["winner_team_id"] for lo in locked_outcomes}

    # Convert locked outcomes to GameResults
    locked_results = []
    still_remaining = []
    for game in remaining_games:
        if game.game_id in locked_ids:
            winner = locked_map[game.game_id]
            home_won = (winner == game.home_team_id)
            locked_results.append(GameResult(
                game_id=game.game_id,
                home_team_id=game.home_team_id,
                away_team_id=game.away_team_id,
                home_score=1 if home_won else 0,
                away_score=0 if home_won else 1,
                status=GameStatus.FINAL,
            ))
        else:
            still_remaining.append(game)

    # Combine played games with locked outcomes
    all_played = list(played_games) + locked_results

    # Run Monte Carlo on the remaining unlocked games
    projections = run_simulation(teams, all_played, still_remaining, config, seed=seed)

    target = projections.get(target_team_id)
    if not target:
        return {"target": None, "all_projections": projections}

    return {
        "target": target,
        "all_projections": projections,
        "locked_count": len(locked_results),
        "remaining_count": len(still_remaining),
    }


def calculate_best_case(
    teams: dict[int, TeamRecord],
    played_games: list[GameResult],
    remaining_games: list[ScheduledGame],
    target_team_id: int,
    config: SimulationConfig | None = None,
) -> dict:
    """Auto-generate best case: lock all remaining games to favor the target team.

    For games involving the target team: target team wins.
    For other games: the weaker team wins (lowers opponents' strength).
    """
    current = calculate_all_ratings(teams, played_games)
    locked = []
    for game in remaining_games:
        if game.home_team_id == target_team_id:
            locked.append({"game_id": game.game_id, "winner_team_id": target_team_id})
        elif game.away_team_id == target_team_id:
            locked.append({"game_id": game.game_id, "winner_team_id": target_team_id})
        else:
            # For games not involving target: pick the lower-rated team to win
            # This weakens the target's division rivals
            home_rating = current.get(game.home_team_id, TeamRecord(team_id=0, school_name="", division="", classification="")).power_rating
            away_rating = current.get(game.away_team_id, TeamRecord(team_id=0, school_name="", division="", classification="")).power_rating
            weaker = game.home_team_id if home_rating <= away_rating else game.away_team_id
            locked.append({"game_id": game.game_id, "winner_team_id": weaker})

    return calculate_scenario(teams, played_games, remaining_games, locked, target_team_id, config)


def calculate_worst_case(
    teams: dict[int, TeamRecord],
    played_games: list[GameResult],
    remaining_games: list[ScheduledGame],
    target_team_id: int,
    config: SimulationConfig | None = None,
) -> dict:
    """Auto-generate worst case: lock all remaining games against the target team.

    For games involving the target team: target team loses.
    For other games: the stronger team wins (strengthens opponents).
    """
    current = calculate_all_ratings(teams, played_games)
    locked = []
    for game in remaining_games:
        if game.home_team_id == target_team_id:
            locked.append({"game_id": game.game_id, "winner_team_id": game.away_team_id})
        elif game.away_team_id == target_team_id:
            locked.append({"game_id": game.game_id, "winner_team_id": game.home_team_id})
        else:
            home_rating = current.get(game.home_team_id, TeamRecord(team_id=0, school_name="", division="", classification="")).power_rating
            away_rating = current.get(game.away_team_id, TeamRecord(team_id=0, school_name="", division="", classification="")).power_rating
            stronger = game.home_team_id if home_rating >= away_rating else game.away_team_id
            locked.append({"game_id": game.game_id, "winner_team_id": stronger})

    return calculate_scenario(teams, played_games, remaining_games, locked, target_team_id, config)
