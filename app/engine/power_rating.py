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
# Division / Classification mappings
# ---------------------------------------------------------------------------

_DIVISION_ORDER = {"I": 1, "II": 2, "III": 3, "IV": 4}
_CLASS_ORDER = {"1A": 1, "2A": 2, "3A": 3, "4A": 4, "5A": 5}


def division_rank(div: str) -> int:
    """Convert roman numeral division to numeric rank. Higher = larger schools."""
    return _DIVISION_ORDER.get(div.upper().strip(), 0)


def classification_rank(cls: str) -> int:
    """Convert classification string to numeric rank. Higher = larger schools."""
    return _CLASS_ORDER.get(cls.upper().strip(), 0)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TeamRecord:
    team_id: int
    classification: str  # "1A" .. "5A"
    division: str  # "I", "II", "III", "IV"
    select_status: str = "Non-Select"  # "Select" or "Non-Select"
    wins: int = 0
    losses: int = 0

    @property
    def games_played(self) -> int:
        return self.wins + self.losses


@dataclass
class GameResult:
    """A single game from one team's perspective."""
    team_id: int
    opponent_id: int
    won: bool
    opponent_division: str  # "I", "II", "III", "IV"
    opponent_classification: str  # "1A" .. "5A"


@dataclass
class GamePowerPoints:
    """Breakdown of power points earned in a single game."""
    opponent_id: int
    result_points: float
    play_up_points: float
    opponent_wins_points: float

    @property
    def total(self) -> float:
        return self.result_points + self.play_up_points + self.opponent_wins_points


@dataclass
class PowerRatingResult:
    team_id: int
    power_rating: float
    strength_factor: float
    game_details: list[GamePowerPoints] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------------

def calculate_play_up_points(
    team_division: str,
    team_classification: str,
    opponent_division: str,
    opponent_classification: str,
) -> float:
    """Return +2 for each level the opponent is above the team in division & class.

    Per LHSAA rules (April 2023 change): play-up bonus is based on playoff
    division, not classification. The bonus is +2 per combined division + class
    level the opponent exceeds the team.
    """
    div_diff = division_rank(opponent_division) - division_rank(team_division)
    class_diff = classification_rank(opponent_classification) - classification_rank(team_classification)
    levels_above = max(div_diff + class_diff, 0)
    return levels_above * 2.0


def calculate_opponent_wins_points(opponent_wins: int, opponent_games: int) -> float:
    """Calculate opponent wins component: (opponent wins / opponent total games) * 10."""
    if opponent_games == 0:
        return 0.0
    return (opponent_wins / opponent_games) * 10.0


def calculate_strength_factor(
    games: list[GameResult],
    records: dict[int, TeamRecord],
) -> float:
    """Calculate tiebreaker strength factor.

    Formula: (Sum of opponents' classification rank + Sum of opponents' wins) / games played
    """
    if not games:
        return 0.0

    opponent_class_sum = 0
    opponent_wins_sum = 0
    for g in games:
        opp = records[g.opponent_id]
        opponent_class_sum += classification_rank(opp.classification)
        opponent_wins_sum += opp.wins

    return round((opponent_class_sum + opponent_wins_sum) / len(games), 2)


def calculate_power_rating(
    team: TeamRecord,
    games: list[GameResult],
    records: dict[int, TeamRecord],
) -> PowerRatingResult:
    """Calculate a team's LHSAA power rating from their game results.

    Args:
        team: The team being rated.
        games: List of games the team has played (from their perspective).
        records: Mapping of team_id -> TeamRecord for all teams. Used to look up
                 current opponent win totals, which recalculate retroactively.

    Returns:
        PowerRatingResult with the calculated rating and per-game breakdown.
    """
    if not games:
        return PowerRatingResult(team_id=team.team_id, power_rating=0.0, strength_factor=0.0)

    game_points: list[GamePowerPoints] = []

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

    total_power = sum(gp.total for gp in game_points)
    num_games = len(games)
    power_rating = round(total_power / num_games, 2)
    strength = calculate_strength_factor(games, records)

    return PowerRatingResult(
        team_id=team.team_id,
        power_rating=power_rating,
        strength_factor=strength,
        game_details=game_points,
    )


def calculate_all_power_ratings(
    all_records: dict[int, TeamRecord],
    all_games: dict[int, list[GameResult]],
) -> dict[int, PowerRatingResult]:
    """Calculate power ratings for every team in the league.

    Because opponent wins points are retroactive (they depend on the opponent's
    current record, not their record at game time), this function computes all
    ratings in a single pass using the current state of all records.

    Args:
        all_records: team_id -> TeamRecord for every team.
        all_games: team_id -> list of GameResults for every team.

    Returns:
        team_id -> PowerRatingResult for every team.
    """
    results = {}
    for team_id, team in all_records.items():
        games = all_games.get(team_id, [])
        results[team_id] = calculate_power_rating(team, games, all_records)
    return results
