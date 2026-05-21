"""Logistic win probability model.

P(home_win) = 1 / (1 + exp(-k * (home_rating - away_rating + home_advantage)))
"""
from __future__ import annotations

import numpy as np


def win_probability(
    home_rating: float,
    away_rating: float,
    home_advantage: float = 0.5,
    k: float = 0.8,
) -> float:
    """Scalar win probability for home team."""
    exponent = -k * (home_rating - away_rating + home_advantage)
    return float(1.0 / (1.0 + np.exp(exponent)))


def win_probability_batch(
    home_ratings: np.ndarray,
    away_ratings: np.ndarray,
    home_advantage: float = 0.5,
    k: float = 0.8,
) -> np.ndarray:
    """Vectorized win probability for arrays of matchups."""
    exponent = -k * (home_ratings - away_ratings + home_advantage)
    return 1.0 / (1.0 + np.exp(exponent))
