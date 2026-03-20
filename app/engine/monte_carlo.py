"""Monte Carlo simulation engine for predicting final power ratings and playoff outcomes.

Approach:
1. Take every remaining game in the season across the state.
2. Assign a win probability to each game based on current power ratings.
3. Simulate the rest of the season N times (default 10,000).
4. Each simulation produces complete final records and power ratings.
5. Seed a full playoff bracket per division+select_status using final ratings.
6. Simulate each playoff round using win probabilities from projected ratings.
7. Aggregate across simulations for probability distributions.

Key: playoff brackets are separated by division AND select_status.
Division I Select and Division I Non-Select are distinct brackets.

LHSAA playoff structure (football):
- Top N teams per bracket qualify (typically 16 or 32 depending on division)
- Seeded by power rating: #1 vs #N, #2 vs #(N-1), etc.
- Higher seed hosts every round through semifinals
- Championship at neutral site (Caesars Superdome)
- 5 rounds for 32-team brackets: R1 -> Quarters -> Semis -> Championship
- 4 rounds for 16-team brackets: R1 -> Quarters -> Semis -> Championship
"""

from __future__ import annotations

from dataclasses import dataclass, field

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
class PlayoffConfig:
    """Configuration for playoff bracket simulation."""
    teams_per_bracket: int = 32  # 32 for Div I/II, 16 for Div III/IV
    home_advantage_playoffs: float = 0.3  # slightly less than regular season
    championship_neutral: bool = True  # championship game at neutral site


# Default configs by division
PLAYOFF_CONFIGS = {
    "I": PlayoffConfig(teams_per_bracket=32),
    "II": PlayoffConfig(teams_per_bracket=32),
    "III": PlayoffConfig(teams_per_bracket=32),
    "IV": PlayoffConfig(teams_per_bracket=16),
}


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
    # Playoff round advancement probabilities (percentage 0-100)
    made_playoffs: float = 0.0
    won_round1: float = 0.0
    reached_quarters: float = 0.0
    reached_semis: float = 0.0
    reached_championship: float = 0.0
    won_title: float = 0.0


def estimate_win_probability(
    higher_seed_rating: float,
    lower_seed_rating: float,
    home_advantage: float = 0.5,
) -> float:
    """Estimate win probability for the higher-seeded (or home) team.

    Uses a logistic function. In regular season, home_advantage=0.5.
    In playoffs, the higher seed hosts (smaller advantage since they earned it).
    """
    diff = higher_seed_rating - lower_seed_rating
    return 1.0 / (1.0 + np.exp(-(diff + home_advantage) / 3.0))


def _bracket_key(record: TeamRecord) -> str:
    """Generate a bracket key from division + select_status.
    Division I Select and Division I Non-Select are separate brackets."""
    return f"{record.division}_{record.select_status}"


def _simulate_playoff_bracket(
    seeded_teams: list[tuple[int, float]],
    rng: np.random.Generator,
    config: PlayoffConfig,
) -> dict[int, int]:
    """Simulate a single-elimination playoff bracket.

    Args:
        seeded_teams: List of (team_id, power_rating) sorted by seed (best first).
        rng: Random number generator.
        config: Playoff configuration.

    Returns:
        Dict of team_id -> deepest round reached (0=didn't qualify, 1=lost R1,
        2=lost quarters, 3=lost semis, 4=lost championship, 5=won title).
        For 16-team brackets: 1=lost R1, 2=lost quarters, 3=lost semis,
        4=lost championship, 5=won title.
    """
    n = min(len(seeded_teams), config.teams_per_bracket)
    if n < 2:
        # Not enough teams for a bracket
        result = {}
        for tid, _ in seeded_teams:
            result[tid] = 0
        return result

    # Build matchups: #1 vs #N, #2 vs #(N-1), etc.
    bracket_teams = seeded_teams[:n]
    team_ratings = {tid: rating for tid, rating in bracket_teams}

    # Track how far each team advances
    round_reached: dict[int, int] = {tid: 1 for tid, _ in bracket_teams}

    # Build first round matchups (1 vs N, 2 vs N-1, etc.)
    current_round: list[tuple[int, int]] = []
    for i in range(n // 2):
        higher_seed = bracket_teams[i][0]
        lower_seed = bracket_teams[n - 1 - i][0]
        current_round.append((higher_seed, lower_seed))

    round_num = 1
    total_rounds = _count_rounds(n)

    while len(current_round) > 0:
        winners = []
        draws = rng.random(len(current_round))

        for idx, (team_a, team_b) in enumerate(current_round):
            rating_a = team_ratings[team_a]
            rating_b = team_ratings[team_b]

            # Higher seed hosts, except championship is neutral
            is_championship = (len(current_round) == 1 and
                               round_num == total_rounds)
            if is_championship and config.championship_neutral:
                adv = 0.0
            else:
                adv = config.home_advantage_playoffs

            win_prob = estimate_win_probability(rating_a, rating_b, adv)
            winner = team_a if draws[idx] < win_prob else team_b
            loser = team_b if winner == team_a else team_a

            # Winner advances, loser stays at current round
            round_reached[loser] = round_num
            winners.append(winner)

        round_num += 1

        if len(winners) == 1:
            # Champion
            round_reached[winners[0]] = total_rounds + 1  # won the title
            break

        # Build next round matchups (maintain bracket order)
        current_round = []
        for i in range(0, len(winners), 2):
            if i + 1 < len(winners):
                current_round.append((winners[i], winners[i + 1]))
            else:
                # Odd number of winners (shouldn't happen in power-of-2 bracket)
                round_reached[winners[i]] = round_num
                break

    return round_reached


def _count_rounds(n_teams: int) -> int:
    """Count the number of rounds in a single-elimination bracket."""
    rounds = 0
    while n_teams > 1:
        n_teams = n_teams // 2
        rounds += 1
    return rounds


def _round_to_milestone(round_reached: int, total_rounds: int) -> dict[str, bool]:
    """Convert round_reached number to milestone flags.

    For a 32-team bracket (5 rounds):
        round 1 = lost R1, round 2 = lost quarters, round 3 = lost semis,
        round 4 = lost championship, round 5 = WON (reached round 6 = total+1)

    For a 16-team bracket (4 rounds):
        round 1 = lost R1, round 2 = lost quarters, round 3 = lost semis,
        round 4 = lost championship, round 5 = WON (reached round 5 = total+1)

    We normalize to consistent milestone names regardless of bracket size.
    """
    won_title = round_reached > total_rounds
    reached_championship = round_reached >= total_rounds or won_title
    reached_semis = round_reached >= total_rounds - 1 or reached_championship
    reached_quarters = round_reached >= total_rounds - 2 or reached_semis

    # For 32-team brackets, R1 is an extra round before quarters
    # For 16-team brackets, R1 directly feeds quarters
    if total_rounds >= 5:
        # 32-team: R1(1) -> R2(2) -> Quarters(3) -> Semis(4) -> Champ(5)
        won_round1 = round_reached >= 2 or reached_quarters
    else:
        # 16-team: R1(1) -> Quarters(2) -> Semis(3) -> Champ(4)
        won_round1 = round_reached >= 2 or reached_quarters

    return {
        "made_playoffs": True,
        "won_round1": won_round1,
        "reached_quarters": reached_quarters,
        "reached_semis": reached_semis,
        "reached_championship": reached_championship,
        "won_title": won_title,
    }


def simulate_season(
    completed_games: dict[int, list[GameResult]],
    remaining_games: list[ScheduledGame],
    records: dict[int, TeamRecord],
    current_ratings: dict[int, float],
    num_simulations: int = 10_000,
    playoff_cutoff: int = 32,
    rng_seed: int | None = None,
    playoff_configs: dict[str, PlayoffConfig] | None = None,
) -> tuple[dict[int, TeamProjection], dict[int, float]]:
    """Run Monte Carlo simulations for the rest of the season including playoffs.

    Args:
        completed_games: team_id -> list of completed GameResults.
        remaining_games: games yet to be played.
        records: current TeamRecord for every team.
        current_ratings: current power rating per team.
        num_simulations: number of Monte Carlo iterations.
        playoff_cutoff: max teams per bracket that qualify for playoffs.
        rng_seed: optional seed for reproducibility.
        playoff_configs: optional per-division playoff configuration overrides.

    Returns:
        Tuple of (team projections dict, game-level home win probabilities dict).
    """
    rng = np.random.default_rng(rng_seed)
    team_ids = list(records.keys())
    configs = playoff_configs or PLAYOFF_CONFIGS

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

    # Playoff advancement tracking
    playoff_counts = {tid: np.zeros(6, dtype=int) for tid in team_ids}
    # Index: 0=made_playoffs, 1=won_round1, 2=reached_quarters,
    #        3=reached_semis, 4=reached_championship, 5=won_title

    # Group teams by bracket
    brackets: dict[str, list[int]] = {}
    for tid, rec in records.items():
        key = _bracket_key(rec)
        brackets.setdefault(key, []).append(tid)

    for sim in range(num_simulations):
        # --- Phase 1: Simulate remaining regular season games ---
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

        # --- Phase 2: Calculate final power ratings ---
        sim_final_ratings: dict[int, float] = {}
        for tid in team_ids:
            team = sim_records[tid]
            games = sim_games.get(tid, [])
            result = calculate_power_rating(team, games, sim_records)
            sim_final_ratings[tid] = result.power_rating
            all_ratings[tid][sim] = result.power_rating
            all_wins[tid][sim] = sim_records[tid].wins
            all_losses[tid][sim] = sim_records[tid].losses

        # --- Phase 3: Seed and simulate playoff brackets ---
        for bracket_key, bracket_tids in brackets.items():
            division = bracket_key.split("_")[0]
            config = configs.get(division, PlayoffConfig())
            n_qualify = min(len(bracket_tids), config.teams_per_bracket)

            # Rank teams in this bracket by final power rating
            ranked = sorted(
                [(tid, sim_final_ratings[tid]) for tid in bracket_tids],
                key=lambda x: x[1],
                reverse=True,
            )

            # Teams that made the playoffs
            qualifiers = ranked[:n_qualify]
            qualifier_ids = {tid for tid, _ in qualifiers}

            # Simulate the bracket
            round_results = _simulate_playoff_bracket(qualifiers, rng, config)
            total_rounds = _count_rounds(n_qualify)

            for tid in bracket_tids:
                if tid in qualifier_ids:
                    rr = round_results.get(tid, 0)
                    milestones = _round_to_milestone(rr, total_rounds)
                    if milestones["made_playoffs"]:
                        playoff_counts[tid][0] += 1
                    if milestones["won_round1"]:
                        playoff_counts[tid][1] += 1
                    if milestones["reached_quarters"]:
                        playoff_counts[tid][2] += 1
                    if milestones["reached_semis"]:
                        playoff_counts[tid][3] += 1
                    if milestones["reached_championship"]:
                        playoff_counts[tid][4] += 1
                    if milestones["won_title"]:
                        playoff_counts[tid][5] += 1

    # --- Aggregate results ---
    projections: dict[int, TeamProjection] = {}
    for tid in team_ids:
        ratings = all_ratings[tid]
        pc = playoff_counts[tid]
        projections[tid] = TeamProjection(
            team_id=tid,
            projected_rating_mean=round(float(np.mean(ratings)), 2),
            projected_rating_median=round(float(np.median(ratings)), 2),
            projected_rating_p10=round(float(np.percentile(ratings, 10)), 2),
            projected_rating_p90=round(float(np.percentile(ratings, 90)), 2),
            projected_rank_mean=0.0,
            playoff_probability=round(float(pc[0]) / num_simulations * 100, 2),
            championship_probability=round(float(pc[5]) / num_simulations * 100, 2),
            projected_wins_mean=round(float(np.mean(all_wins[tid])), 1),
            projected_losses_mean=round(float(np.mean(all_losses[tid])), 1),
            made_playoffs=round(float(pc[0]) / num_simulations * 100, 2),
            won_round1=round(float(pc[1]) / num_simulations * 100, 2),
            reached_quarters=round(float(pc[2]) / num_simulations * 100, 2),
            reached_semis=round(float(pc[3]) / num_simulations * 100, 2),
            reached_championship=round(float(pc[4]) / num_simulations * 100, 2),
            won_title=round(float(pc[5]) / num_simulations * 100, 2),
        )

    # Calculate projected rank mean per bracket
    for bracket_tids in brackets.values():
        for tid in bracket_tids:
            rank_sum = 0.0
            for sim in range(num_simulations):
                team_rating = all_ratings[tid][sim]
                higher = sum(
                    1 for other in bracket_tids
                    if other != tid and all_ratings[other][sim] > team_rating
                )
                rank_sum += higher + 1
            projections[tid].projected_rank_mean = round(rank_sum / num_simulations, 1)

    game_win_probs = {
        game.game_id: wp for game, wp in zip(remaining_games, win_probs)
    }

    return projections, game_win_probs
