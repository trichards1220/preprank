"""Monte Carlo simulation engine for predicting final power ratings.

Approach:
1. Take every remaining game in the season across the state.
2. Assign a win probability to each game based on current power ratings.
3. Simulate the rest of the season N times (default 10,000).
4. Each simulation produces complete final records and power ratings.
5. Aggregate across simulations for probability distributions.

Key: playoff brackets are separated by division AND select_status.
Division I Select and Division I Non-Select are distinct brackets.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.engine.power_rating import (
    TeamRecord,
    GameResult,
    calculate_power_rating,
)


@dataclass
class ScheduledGame:
    game_id: int
    home_team_id: int
    away_team_id: int
    home_division: str  # "I", "II", "III", "IV"
    home_classification: str
    away_division: str
    away_classification: str


@dataclass
class TeamProjection:
    team_id: int
    projected_rating_mean: float
    projected_rating_median: float
    projected_rating_p10: float
    projected_rating_p90: float
    projected_rank_mean: float
    playoff_probability: float
    championship_probability: float
    projected_wins_mean: float
    projected_losses_mean: float


def estimate_win_probability(home_rating: float, away_rating: float) -> float:
    """Estimate home team win probability from current power ratings.

    Uses a logistic function with a small home-field advantage factor.
    This is a Tier 1 model — wins/losses and power ratings only.
    """
    diff = home_rating - away_rating
    home_advantage = 0.5
    return 1.0 / (1.0 + np.exp(-(diff + home_advantage) / 3.0))


def _bracket_key(record: TeamRecord) -> str:
    """Generate a bracket key from division + select_status.
    Division I Select and Division I Non-Select are separate brackets."""
    return f"{record.division}_{record.select_status}"


def simulate_season(
    completed_games: dict[int, list[GameResult]],
    remaining_games: list[ScheduledGame],
    records: dict[int, TeamRecord],
    current_ratings: dict[int, float],
    num_simulations: int = 10_000,
    playoff_cutoff: int = 8,
    rng_seed: int | None = None,
) -> tuple[dict[int, TeamProjection], dict[int, float]]:
    """Run Monte Carlo simulations for the rest of the season.

    Args:
        completed_games: team_id -> list of completed GameResults.
        remaining_games: games yet to be played.
        records: current TeamRecord for every team.
        current_ratings: current power rating per team.
        num_simulations: number of Monte Carlo iterations.
        playoff_cutoff: top N teams per bracket make playoffs.
        rng_seed: optional seed for reproducibility.

    Returns:
        Tuple of (team projections dict, game-level home win probabilities dict).
    """
    rng = np.random.default_rng(rng_seed)
    team_ids = list(records.keys())

    # Pre-compute win probabilities for each remaining game
    win_probs = []
    for game in remaining_games:
        hr = current_ratings.get(game.home_team_id, 0.0)
        ar = current_ratings.get(game.away_team_id, 0.0)
        win_probs.append(estimate_win_probability(hr, ar))

    # Storage for results across simulations
    all_ratings = {tid: np.zeros(num_simulations) for tid in team_ids}
    all_wins = {tid: np.zeros(num_simulations) for tid in team_ids}
    all_losses = {tid: np.zeros(num_simulations) for tid in team_ids}

    for sim in range(num_simulations):
        # Copy records for this simulation
        sim_records = {
            tid: TeamRecord(
                team_id=tid,
                classification=r.classification,
                division=r.division,
                select_status=r.select_status,
                wins=r.wins,
                losses=r.losses,
            )
            for tid, r in records.items()
        }

        sim_games: dict[int, list[GameResult]] = {
            tid: list(gs) for tid, gs in completed_games.items()
        }

        # Simulate each remaining game
        random_draws = rng.random(len(remaining_games))
        for i, game in enumerate(remaining_games):
            home_wins = random_draws[i] < win_probs[i]

            if home_wins:
                sim_records[game.home_team_id].wins += 1
                sim_records[game.away_team_id].losses += 1
            else:
                sim_records[game.home_team_id].losses += 1
                sim_records[game.away_team_id].wins += 1

            sim_games.setdefault(game.home_team_id, []).append(GameResult(
                team_id=game.home_team_id,
                opponent_id=game.away_team_id,
                won=home_wins,
                opponent_division=game.away_division,
                opponent_classification=game.away_classification,
            ))
            sim_games.setdefault(game.away_team_id, []).append(GameResult(
                team_id=game.away_team_id,
                opponent_id=game.home_team_id,
                won=not home_wins,
                opponent_division=game.home_division,
                opponent_classification=game.home_classification,
            ))

        # Calculate final power ratings for every team
        for tid in team_ids:
            team = sim_records[tid]
            games = sim_games.get(tid, [])
            result = calculate_power_rating(team, games, sim_records)
            all_ratings[tid][sim] = result.power_rating
            all_wins[tid][sim] = sim_records[tid].wins
            all_losses[tid][sim] = sim_records[tid].losses

    # Aggregate results
    projections: dict[int, TeamProjection] = {}
    for tid in team_ids:
        ratings = all_ratings[tid]
        projections[tid] = TeamProjection(
            team_id=tid,
            projected_rating_mean=round(float(np.mean(ratings)), 2),
            projected_rating_median=round(float(np.median(ratings)), 2),
            projected_rating_p10=round(float(np.percentile(ratings, 10)), 2),
            projected_rating_p90=round(float(np.percentile(ratings, 90)), 2),
            projected_rank_mean=0.0,
            playoff_probability=0.0,
            championship_probability=0.0,
            projected_wins_mean=round(float(np.mean(all_wins[tid])), 1),
            projected_losses_mean=round(float(np.mean(all_losses[tid])), 1),
        )

    # Calculate playoff/championship probabilities per bracket (division + select_status)
    brackets: dict[str, list[int]] = {}
    for tid, rec in records.items():
        key = _bracket_key(rec)
        brackets.setdefault(key, []).append(tid)

    for bracket_teams in brackets.values():
        for tid in bracket_teams:
            in_playoff = 0
            first_place = 0
            rank_sum = 0.0
            for sim in range(num_simulations):
                team_rating = all_ratings[tid][sim]
                higher = sum(
                    1 for other in bracket_teams
                    if other != tid and all_ratings[other][sim] > team_rating
                )
                rank = higher + 1
                rank_sum += rank
                if rank <= playoff_cutoff:
                    in_playoff += 1
                if rank == 1:
                    first_place += 1

            projections[tid].projected_rank_mean = round(rank_sum / num_simulations, 1)
            projections[tid].playoff_probability = round(in_playoff / num_simulations * 100, 2)
            projections[tid].championship_probability = round(first_place / num_simulations * 100, 2)

    game_win_probs = {
        game.game_id: wp for game, wp in zip(remaining_games, win_probs)
    }

    return projections, game_win_probs
