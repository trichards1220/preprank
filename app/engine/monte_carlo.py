"""Monte Carlo simulation engine for predicting final power ratings.

Approach:
1. Take every remaining game in the season across the state.
2. Assign a win probability to each game based on current power ratings.
3. Simulate the rest of the season N times (default 10,000).
4. Each simulation produces complete final records and power ratings.
5. Aggregate across simulations for probability distributions.
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
    home_division: int
    home_classification: str
    away_division: int
    away_classification: str


@dataclass
class TeamProjection:
    team_id: int
    projected_rating_mean: float
    projected_rating_p10: float
    projected_rating_p90: float
    playoff_probability: float


@dataclass
class GameImpact:
    game_id: int
    home_win_probability: float
    # Impact on home team's projected rating if home wins vs loses
    home_win_rating_delta: float
    home_loss_rating_delta: float


def estimate_win_probability(home_rating: float, away_rating: float) -> float:
    """Estimate home team win probability from current power ratings.

    Uses a logistic function with a small home-field advantage factor.
    This is a Tier 1 model — wins/losses and power ratings only.
    """
    diff = home_rating - away_rating
    home_advantage = 0.5  # slight edge for home team
    return 1.0 / (1.0 + np.exp(-(diff + home_advantage) / 3.0))


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
        playoff_cutoff: top N teams per division make playoffs.
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

    # Storage for final ratings across simulations
    all_ratings = {tid: np.zeros(num_simulations) for tid in team_ids}

    for sim in range(num_simulations):
        # Copy records for this simulation
        sim_records = {
            tid: TeamRecord(
                team_id=tid,
                classification=r.classification,
                division=r.division,
                select=r.select,
                wins=r.wins,
                losses=r.losses,
            )
            for tid, r in records.items()
        }

        # Copy completed games
        sim_games: dict[int, list[GameResult]] = {
            tid: list(gs) for tid, gs in completed_games.items()
        }

        # Simulate each remaining game
        random_draws = rng.random(len(remaining_games))
        for i, game in enumerate(remaining_games):
            home_wins = random_draws[i] < win_probs[i]

            # Update records
            if home_wins:
                sim_records[game.home_team_id].wins += 1
                sim_records[game.away_team_id].losses += 1
            else:
                sim_records[game.home_team_id].losses += 1
                sim_records[game.away_team_id].wins += 1

            # Add game results for both teams
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

        # Calculate final power ratings for every team in this simulation
        for tid in team_ids:
            team = sim_records[tid]
            games = sim_games.get(tid, [])
            result = calculate_power_rating(team, games, sim_records)
            all_ratings[tid][sim] = result.power_rating

    # Aggregate results
    projections: dict[int, TeamProjection] = {}
    for tid in team_ids:
        ratings = all_ratings[tid]
        projections[tid] = TeamProjection(
            team_id=tid,
            projected_rating_mean=round(float(np.mean(ratings)), 2),
            projected_rating_p10=round(float(np.percentile(ratings, 10)), 2),
            projected_rating_p90=round(float(np.percentile(ratings, 90)), 2),
            playoff_probability=0.0,  # calculated below per division
        )

    # Calculate playoff probabilities per division
    divisions: dict[int, list[int]] = {}
    for tid, rec in records.items():
        divisions.setdefault(rec.division, []).append(tid)

    for div_teams in divisions.values():
        for tid in div_teams:
            # Count simulations where this team finishes in top N of its division
            in_playoff_count = 0
            for sim in range(num_simulations):
                team_rating = all_ratings[tid][sim]
                higher_count = sum(
                    1 for other_tid in div_teams
                    if other_tid != tid and all_ratings[other_tid][sim] > team_rating
                )
                if higher_count < playoff_cutoff:
                    in_playoff_count += 1
            projections[tid].playoff_probability = round(in_playoff_count / num_simulations, 4)

    game_win_probs = {
        game.game_id: wp for game, wp in zip(remaining_games, win_probs)
    }

    return projections, game_win_probs
