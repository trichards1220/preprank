"""Tests for the Monte Carlo simulation engine with playoff bracket simulation."""

from app.engine.monte_carlo import (
    TeamProjection,
    PlayoffConfig,
    _simulate_playoff_bracket,
    _count_rounds,
    _round_to_milestone,
    simulate_season,
    _bracket_key,
)
from app.engine.power_rating import TeamRecord, GameResult

import numpy as np


def test_count_rounds():
    assert _count_rounds(2) == 1
    assert _count_rounds(4) == 2
    assert _count_rounds(8) == 3
    assert _count_rounds(16) == 4
    assert _count_rounds(32) == 5


def test_bracket_key():
    rec = TeamRecord(team_id=1, classification="5A", division="I", select_status="Select")
    assert _bracket_key(rec) == "I_Select"

    rec2 = TeamRecord(team_id=2, classification="3A", division="III", select_status="Non-Select")
    assert _bracket_key(rec2) == "III_Non-Select"


def test_simulate_playoff_bracket_deterministic():
    """With a fixed seed and a massive rating gap, the #1 seed should always win."""
    rng = np.random.default_rng(42)
    config = PlayoffConfig(teams_per_bracket=8)

    # #1 seed has a massive rating advantage
    seeded = [
        (1, 20.0),  # dominant team
        (2, 10.0),
        (3, 9.0),
        (4, 8.0),
        (5, 7.0),
        (6, 6.0),
        (7, 5.0),
        (8, 4.0),
    ]

    # Run many brackets to check probabilities
    wins_by_team = {i: 0 for i in range(1, 9)}
    n_trials = 1000
    for _ in range(n_trials):
        results = _simulate_playoff_bracket(seeded, rng, config)
        total_rounds = _count_rounds(8)
        for tid, rr in results.items():
            if rr > total_rounds:  # won title
                wins_by_team[tid] += 1

    # Team 1 should win the vast majority
    assert wins_by_team[1] > n_trials * 0.5


def test_simulate_playoff_bracket_all_teams_placed():
    """Every team that enters the bracket should have a round_reached value."""
    rng = np.random.default_rng(123)
    config = PlayoffConfig(teams_per_bracket=16)

    seeded = [(i, 15.0 - i * 0.5) for i in range(1, 17)]
    results = _simulate_playoff_bracket(seeded, rng, config)

    assert len(results) == 16
    for tid in range(1, 17):
        assert tid in results
        assert results[tid] >= 1  # everyone plays at least round 1


def test_round_to_milestone_32_team():
    """Test milestone mapping for a 32-team bracket (5 rounds)."""
    total_rounds = 5

    # Lost in round 1
    m = _round_to_milestone(1, total_rounds)
    assert m["made_playoffs"] is True
    assert m["won_round1"] is False
    assert m["reached_quarters"] is False

    # Won round 1, lost in round 2
    m = _round_to_milestone(2, total_rounds)
    assert m["won_round1"] is True
    assert m["reached_quarters"] is False

    # Reached quarters (round 3), lost
    m = _round_to_milestone(3, total_rounds)
    assert m["reached_quarters"] is True
    assert m["reached_semis"] is False

    # Reached semis (round 4), lost
    m = _round_to_milestone(4, total_rounds)
    assert m["reached_semis"] is True
    assert m["reached_championship"] is False

    # Lost championship (round 5)
    m = _round_to_milestone(5, total_rounds)
    assert m["reached_championship"] is True
    assert m["won_title"] is False

    # Won title (round 6 = total_rounds + 1)
    m = _round_to_milestone(6, total_rounds)
    assert m["won_title"] is True
    assert m["reached_championship"] is True
    assert m["reached_semis"] is True


def test_round_to_milestone_16_team():
    """Test milestone mapping for a 16-team bracket (4 rounds)."""
    total_rounds = 4

    m = _round_to_milestone(1, total_rounds)
    assert m["made_playoffs"] is True
    assert m["won_round1"] is False

    m = _round_to_milestone(5, total_rounds)
    assert m["won_title"] is True


def test_full_simulation_with_playoffs():
    """Integration test: simulate a mini season with 8 teams and verify playoff fields."""
    records = {}
    completed_games: dict[int, list[GameResult]] = {}

    # Create 8 teams with varying records. Each team played every other team once.
    # Team 1 beat everyone, team 8 lost to everyone, etc.
    for i in range(1, 9):
        records[i] = TeamRecord(
            team_id=i,
            classification="5A",
            division="I",
            select_status="Non-Select",
            wins=8 - i,
            losses=i - 1,
        )
        completed_games[i] = []

    # Give each team game results so they produce distinct power ratings.
    # Team 1 beat teams 2-8, team 2 beat 3-8 but lost to 1, etc.
    for i in range(1, 9):
        for j in range(1, 9):
            if i == j:
                continue
            won = i < j  # lower team_id = better team
            completed_games[i].append(GameResult(
                team_id=i,
                opponent_id=j,
                won=won,
                opponent_division="I",
                opponent_classification="5A",
            ))

    current_ratings = {i: 15.0 - i * 0.5 for i in range(1, 9)}

    projections, _ = simulate_season(
        completed_games=completed_games,
        remaining_games=[],
        records=records,
        current_ratings=current_ratings,
        num_simulations=500,
        playoff_cutoff=8,
        rng_seed=42,
        playoff_configs={"I": PlayoffConfig(teams_per_bracket=8)},
    )

    assert len(projections) == 8

    # All 8 teams should make playoffs (bracket size = 8)
    for tid in range(1, 9):
        proj = projections[tid]
        assert proj.made_playoffs == 100.0

    # Team 1 (best record/rating) should have highest title probability
    assert projections[1].won_title > projections[8].won_title

    # All milestone fields should be monotonically decreasing
    # (more teams make playoffs than win titles)
    proj1 = projections[1]
    assert proj1.made_playoffs >= proj1.won_round1
    assert proj1.won_round1 >= proj1.reached_quarters
    assert proj1.reached_quarters >= proj1.reached_semis
    assert proj1.reached_semis >= proj1.reached_championship
    assert proj1.reached_championship >= proj1.won_title

    # Bottom seed should have lower advancement rates
    proj8 = projections[8]
    assert proj8.made_playoffs >= proj8.won_round1
    assert proj8.won_title < proj1.won_title


def test_playoff_probabilities_sum():
    """In any given simulation, exactly one team wins the title per bracket."""
    records = {}
    completed_games: dict[int, list[GameResult]] = {}
    for i in range(1, 9):
        records[i] = TeamRecord(
            team_id=i,
            classification="5A",
            division="I",
            select_status="Non-Select",
            wins=5,
            losses=5,
        )
        completed_games[i] = []

    current_ratings = {i: 10.0 for i in range(1, 9)}

    projections, _ = simulate_season(
        completed_games=completed_games,
        remaining_games=[],
        records=records,
        current_ratings=current_ratings,
        num_simulations=1000,
        playoff_cutoff=8,
        rng_seed=99,
        playoff_configs={"I": PlayoffConfig(teams_per_bracket=8)},
    )

    # Total won_title probability across all teams should sum to ~100%
    total_title_prob = sum(p.won_title for p in projections.values())
    assert 99.0 <= total_title_prob <= 101.0  # allow small rounding
