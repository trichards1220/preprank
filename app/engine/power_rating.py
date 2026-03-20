"""LHSAA Power Rating Calculation Engine.

Implements the exact LHSAA formula:
  Game Power Points = Result Points + Play-Up Points + Opponent Wins Points
  Season Power Rating = Sum(Game Power Points) / Games Played

Result Points: Win = 10, Loss = 0
Play-Up Points: +2 per division & class above (playoff division basis, April 2023 change)
Opponent Wins Points: (Opponent Wins / Opponent Total Games) * 10

Strength Factor (tiebreaker):
  (Sum of opponents' class + Sum of opponents' wins) / Total games played

Key insight: Opponent Wins Points are retroactive — they recalculate as opponents
play more games. This creates the fully-coupled network that makes prediction hard
and is PrepRank's core technical moat.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TeamRecord:
    team_id: int
    classification: str  # "1A" .. "5A"
    division: int  # playoff division (1, 2, 3 …)
    select: bool = False
    wins: int = 0
    losses: int = 0

    @property
    def games_played(self) -> int:
        return self.wins + self.losses


@dataclass
class GameResult:
    team_id: int
    opponent_id: int
    won: bool
    opponent_division: int
    opponent_classification: str


@dataclass
class PowerRatingResult:
    team_id: int
    power_rating: float
    strength_factor: float
    game_details: list[GamePowerPoints] = field(default_factory=list)


@dataclass
class GamePowerPoints:
    opponent_id: int
    result_points: float
    play_up_points: float
    opponent_wins_points: float

    @property
    def total(self) -> float:
        return self.result_points + self.play_up_points + self.opponent_wins_points


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

_CLASS_ORDER = {"1A": 1, "2A": 2, "3A": 3, "4A": 4, "5A": 5}


def classification_rank(cls: str) -> int:
    return _CLASS_ORDER.get(cls.upper(), 0)


# ---------------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------------

def calculate_play_up_points(
    team_division: int,
    team_classification: str,
    opponent_division: int,
    opponent_classification: str,
) -> float:
    """Return +2 for each level the opponent is above the team in division & class."""
    div_diff = opponent_division - team_division
    class_diff = classification_rank(opponent_classification) - classification_rank(team_classification)
    levels_above = max(div_diff + class_diff, 0)
    return levels_above * 2.0


def calculate_opponent_wins_points(opponent_wins: int, opponent_games: int) -> float:
    if opponent_games == 0:
        return 0.0
    return (opponent_wins / opponent_games) * 10.0


def calculate_power_rating(
    team: TeamRecord,
    games: list[GameResult],
    records: dict[int, TeamRecord],
) -> PowerRatingResult:
    """Calculate a team's LHSAA power rating from their game results.

    Args:
        team: The team being rated.
        games: List of games the team has played.
        records: Mapping of team_id -> TeamRecord for all teams (used to look up
                 current opponent win totals, which change retroactively).

    Returns:
        PowerRatingResult with the calculated rating and per-game breakdown.
    """
    if not games:
        return PowerRatingResult(team_id=team.team_id, power_rating=0.0, strength_factor=0.0)

    game_points: list[GamePowerPoints] = []
    opponent_class_sum = 0
    opponent_wins_sum = 0

    for g in games:
        opp = records[g.opponent_id]

        result_pts = 10.0 if g.won else 0.0
        play_up_pts = calculate_play_up_points(
            team.division, team.classification,
            opp.division, opp.classification,
        )
        opp_wins_pts = calculate_opponent_wins_points(opp.wins, opp.games_played)

        game_points.append(GamePowerPoints(
            opponent_id=g.opponent_id,
            result_points=result_pts,
            play_up_points=play_up_pts,
            opponent_wins_points=opp_wins_pts,
        ))

        opponent_class_sum += classification_rank(opp.classification)
        opponent_wins_sum += opp.wins

    total_power = sum(gp.total for gp in game_points)
    num_games = len(games)
    power_rating = round(total_power / num_games, 2)

    strength_factor = round((opponent_class_sum + opponent_wins_sum) / num_games, 2)

    return PowerRatingResult(
        team_id=team.team_id,
        power_rating=power_rating,
        strength_factor=strength_factor,
        game_details=game_points,
    )
