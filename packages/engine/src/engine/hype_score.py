"""Hype Score — momentum metric for teams.

Components:
- Rating velocity: weighted average of week-over-week rating changes (recent weeks weighted higher)
- Win streak bonus: consecutive wins add multiplier
- Upset factor: beating higher-rated teams boosts hype
- Buzz factor: how many users follow this team (social proof)

Output: 0-100 score with labels:
  90-100: ON FIRE
  70-89: SURGING
  50-69: STEADY
  30-49: COOLING
  0-29: ICE COLD
"""
from __future__ import annotations

from dataclasses import dataclass


HYPE_LABELS = [
    (90, "ON FIRE"),
    (70, "SURGING"),
    (50, "STEADY"),
    (30, "COOLING"),
    (0, "ICE COLD"),
]


def get_hype_label(score: float) -> str:
    for threshold, label in HYPE_LABELS:
        if score >= threshold:
            return label
    return "ICE COLD"


@dataclass
class HypeInput:
    """Input data for hype score calculation."""
    weekly_ratings: list[float]  # ratings by week, chronological (oldest first)
    wins: int
    losses: int
    current_win_streak: int
    upset_wins: int  # games won against higher-rated opponents
    follower_count: int  # number of PrepRank users following this team


@dataclass
class HypeResult:
    hype_score: float  # 0-100
    hype_label: str
    rating_velocity: float  # positive = rising
    win_streak: int
    components: dict  # breakdown of score components


def calculate_hype_score(inp: HypeInput) -> HypeResult:
    """Calculate hype score from input data.

    Scoring weights:
    - Rating velocity: 40 points max
    - Win streak: 25 points max
    - Upset factor: 20 points max
    - Buzz factor: 15 points max
    """
    # Rating velocity (0-40 points)
    # Weighted average of week-over-week changes, recent weeks weighted 2x
    velocity = 0.0
    if len(inp.weekly_ratings) >= 2:
        changes = []
        for i in range(1, len(inp.weekly_ratings)):
            changes.append(inp.weekly_ratings[i] - inp.weekly_ratings[i - 1])
        # Weight recent changes higher
        total_weight = 0.0
        weighted_sum = 0.0
        for i, change in enumerate(changes):
            weight = 1.0 + (i / max(len(changes) - 1, 1))  # 1.0 to 2.0
            weighted_sum += change * weight
            total_weight += weight
        velocity = weighted_sum / total_weight if total_weight > 0 else 0.0

    # Normalize velocity to 0-40 points
    # Typical range: -2.0 to +2.0 per week
    velocity_score = max(0.0, min(40.0, (velocity + 2.0) / 4.0 * 40.0))

    # Win streak (0-25 points)
    # 1 win = 5pts, 2 = 10, 3 = 15, 4 = 20, 5+ = 25
    streak_score = min(25.0, inp.current_win_streak * 5.0)

    # Upset factor (0-20 points)
    # Each upset win = 5 points, max 20
    upset_score = min(20.0, inp.upset_wins * 5.0)

    # Buzz factor (0-15 points)
    # Logarithmic: 1 follower = 3pts, 5 = 7pts, 10 = 10pts, 50 = 13pts, 100+ = 15pts
    import math
    if inp.follower_count > 0:
        buzz_score = min(15.0, 3.0 * math.log2(inp.follower_count + 1))
    else:
        buzz_score = 0.0

    total = velocity_score + streak_score + upset_score + buzz_score
    total = max(0.0, min(100.0, total))

    return HypeResult(
        hype_score=round(total, 1),
        hype_label=get_hype_label(total),
        rating_velocity=round(velocity, 3),
        win_streak=inp.current_win_streak,
        components={
            "velocity_score": round(velocity_score, 1),
            "streak_score": round(streak_score, 1),
            "upset_score": round(upset_score, 1),
            "buzz_score": round(buzz_score, 1),
        },
    )
