"""LHSAA Power Rating Calculator.

Formula per game:
    result_points = 10 if won, 0 if lost
    play_up_points = 2 * max(0, opponent_classification_level - my_classification_level)
    opponent_wins_points = (opponent_wins / opponent_total_games) * 10  (0 if opponent has 0 games)
    game_points = result_points + play_up_points + opponent_wins_points

Season power rating = sum(game_points) / games_played, rounded to 2 decimals.
Strength factor = sum(opponent_power_ratings) / games_played.

Iterative recalculation: opponent_wins change as other results are factored in,
so we iterate until ratings converge (delta < 0.001 across all teams).
"""
from __future__ import annotations

from engine.types import TeamRecord, GameResult, GameStatus, ClassificationLevel


def calculate_game_points(
    won: bool,
    my_classification: str,
    opponent_classification: str,
    opponent_wins: int,
    opponent_total_games: int,
) -> float:
    """Calculate points earned from a single game."""
    result_points = 10.0 if won else 0.0
    play_up_points = 2.0 * ClassificationLevel.play_up_levels(my_classification, opponent_classification)
    if opponent_total_games > 0:
        opponent_wins_points = (opponent_wins / opponent_total_games) * 10.0
    else:
        opponent_wins_points = 0.0
    return result_points + play_up_points + opponent_wins_points


def calculate_power_rating(game_points: list[float]) -> float:
    """Average of all game points, rounded to hundredths. Returns 0.0 if no games."""
    if not game_points:
        return 0.0
    return round(sum(game_points) / len(game_points), 2)


def calculate_strength_factor(opponent_ratings: list[float]) -> float:
    """Average of all opponents' power ratings. Returns 0.0 if no opponents."""
    if not opponent_ratings:
        return 0.0
    return round(sum(opponent_ratings) / len(opponent_ratings), 2)


def _eligible_games(games: list[GameResult]) -> list[GameResult]:
    """Filter to games that count toward ratings (exclude cancelled/disputed)."""
    return [g for g in games if g.status in (GameStatus.FINAL, GameStatus.FORFEIT)]


def _build_team_games(
    games: list[GameResult],
) -> dict[int, list[tuple[bool, int]]]:
    """Map team_id -> list of (won, opponent_team_id) from eligible games."""
    team_games: dict[int, list[tuple[bool, int]]] = {}
    for g in games:
        if g.home_won is None:
            continue
        team_games.setdefault(g.home_team_id, []).append((g.home_won, g.away_team_id))
        team_games.setdefault(g.away_team_id, []).append((not g.home_won, g.home_team_id))
    return team_games


def calculate_all_ratings(
    teams: dict[int, TeamRecord],
    games: list[GameResult],
    max_iterations: int = 50,
    tolerance: float = 0.001,
) -> dict[int, TeamRecord]:
    """Calculate power ratings for all teams with iterative convergence.

    Returns a new dict of TeamRecord with updated wins, losses, power_rating, strength_factor.
    """
    eligible = _eligible_games(games)
    team_games = _build_team_games(eligible)

    # Initialize win/loss records
    updated: dict[int, TeamRecord] = {}
    for tid, t in teams.items():
        wins = sum(1 for won, _ in team_games.get(tid, []) if won)
        losses = sum(1 for won, _ in team_games.get(tid, []) if not won)
        updated[tid] = t.model_copy(update={"wins": wins, "losses": losses, "power_rating": 0.0, "strength_factor": 0.0})

    prev_ratings: dict[int, float] = {tid: 0.0 for tid in teams}

    # Iterative convergence
    for iteration in range(max_iterations):
        max_delta = 0.0
        new_ratings: dict[int, float] = {}

        for tid in teams:
            my_games = team_games.get(tid, [])
            if not my_games:
                new_ratings[tid] = 0.0
                continue

            my_class = updated[tid].classification
            game_pts: list[float] = []
            opponent_ratings: list[float] = []

            for won, opp_id in my_games:
                opp = updated.get(opp_id)
                if opp is None:
                    opp_wins = 0
                    opp_total = 0
                    opp_class = my_class
                    opp_rating = 0.0
                else:
                    opp_wins = opp.wins
                    opp_total = opp.games_played
                    opp_class = opp.classification
                    opp_rating = opp.power_rating

                pts = calculate_game_points(won, my_class, opp_class, opp_wins, opp_total)
                game_pts.append(pts)
                opponent_ratings.append(opp_rating)

            new_ratings[tid] = calculate_power_rating(game_pts)
            updated[tid] = updated[tid].model_copy(update={
                "power_rating": new_ratings[tid],
                "strength_factor": calculate_strength_factor(opponent_ratings),
            })

        # Check convergence
        for tid in teams:
            delta = abs(new_ratings.get(tid, 0.0) - prev_ratings.get(tid, 0.0))
            max_delta = max(max_delta, delta)

        prev_ratings = dict(new_ratings)
        if iteration > 0 and max_delta < tolerance:
            break

    return updated
