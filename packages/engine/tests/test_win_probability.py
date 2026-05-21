import pytest
import numpy as np
from engine.win_probability import win_probability, win_probability_batch


def test_equal_teams_home_advantage():
    p = win_probability(home_rating=10.0, away_rating=10.0, home_advantage=0.5, k=0.8)
    assert 0.5 < p < 0.7


def test_equal_teams_no_home_advantage():
    p = win_probability(home_rating=10.0, away_rating=10.0, home_advantage=0.0, k=0.8)
    assert p == pytest.approx(0.5, abs=0.01)


def test_much_better_home_team():
    p = win_probability(home_rating=15.0, away_rating=8.0, home_advantage=0.5, k=0.8)
    assert p > 0.95


def test_much_better_away_team():
    p = win_probability(home_rating=8.0, away_rating=15.0, home_advantage=0.5, k=0.8)
    assert p < 0.05


def test_probability_bounded_0_1():
    p1 = win_probability(home_rating=100.0, away_rating=0.0, home_advantage=0.5, k=0.8)
    p2 = win_probability(home_rating=0.0, away_rating=100.0, home_advantage=0.5, k=0.8)
    assert 0.0 < p1 <= 1.0
    assert 0.0 <= p2 < 1.0


def test_symmetry():
    p1 = win_probability(home_rating=12.0, away_rating=10.0, home_advantage=0.0, k=0.8)
    p2 = win_probability(home_rating=10.0, away_rating=12.0, home_advantage=0.0, k=0.8)
    assert p1 + p2 == pytest.approx(1.0, abs=0.01)


def test_batch_matches_scalar():
    home = np.array([10.0, 12.0, 8.0])
    away = np.array([10.0, 10.0, 15.0])
    batch = win_probability_batch(home, away, home_advantage=0.5, k=0.8)
    for i in range(3):
        scalar = win_probability(home[i], away[i], home_advantage=0.5, k=0.8)
        assert batch[i] == pytest.approx(scalar, abs=1e-10)


def test_batch_returns_numpy_array():
    home = np.array([10.0, 12.0])
    away = np.array([10.0, 10.0])
    result = win_probability_batch(home, away, home_advantage=0.5, k=0.8)
    assert isinstance(result, np.ndarray)
    assert result.shape == (2,)
