"""Data types for the PrepRank engine. No database dependency."""
from __future__ import annotations

from enum import IntEnum, Enum
from pydantic import BaseModel, computed_field


class GameStatus(str, Enum):
    SCHEDULED = "scheduled"
    FINAL = "final"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"
    FORFEIT = "forfeit"


class ClassificationLevel(IntEnum):
    """Numeric ordering: 1A=1, 2A=2, 3A=3, 4A=4, 5A=5."""
    ONE_A = 1
    TWO_A = 2
    THREE_A = 3
    FOUR_A = 4
    FIVE_A = 5

    @classmethod
    def from_str(cls, s: str) -> ClassificationLevel:
        mapping = {"1A": cls.ONE_A, "2A": cls.TWO_A, "3A": cls.THREE_A, "4A": cls.FOUR_A, "5A": cls.FIVE_A}
        return mapping[s]

    @staticmethod
    def play_up_levels(my_classification: str, opponent_classification: str) -> int:
        """How many classification levels the opponent is ABOVE me. 0 if same or below."""
        my_level = ClassificationLevel.from_str(my_classification)
        opp_level = ClassificationLevel.from_str(opponent_classification)
        diff = int(opp_level) - int(my_level)
        return max(0, diff)


class TeamRecord(BaseModel):
    team_id: int
    school_name: str
    division: str
    classification: str
    wins: int = 0
    losses: int = 0
    power_rating: float = 0.0
    strength_factor: float = 0.0

    @computed_field
    @property
    def games_played(self) -> int:
        return self.wins + self.losses


class GameResult(BaseModel):
    game_id: int
    home_team_id: int
    away_team_id: int
    home_score: int | None = None
    away_score: int | None = None
    status: GameStatus = GameStatus.SCHEDULED
    is_forfeit: bool = False
    week_number: int | None = None

    @computed_field
    @property
    def home_won(self) -> bool | None:
        if self.status == GameStatus.FORFEIT:
            return self.home_score is not None and self.away_score is not None and self.home_score > self.away_score
        if self.home_score is None or self.away_score is None:
            return None
        return self.home_score > self.away_score

    @computed_field
    @property
    def margin(self) -> int | None:
        if self.home_score is None or self.away_score is None:
            return None
        return self.home_score - self.away_score


class ScheduledGame(BaseModel):
    """A future game that hasn't been played yet."""
    game_id: int
    home_team_id: int
    away_team_id: int
    week_number: int | None = None


class SimulationConfig(BaseModel):
    sport_name: str
    season_year: int
    week_number: int
    num_runs: int = 10000
    home_advantage: float = 0.5
    k_factor: float = 0.8
    playoff_spots: int = 8


class TeamProjection(BaseModel):
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


class GameImpact(BaseModel):
    game_id: int
    affected_team_id: int
    rating_if_home_wins: float
    rating_if_away_wins: float
    rank_if_home_wins: int
    rank_if_away_wins: int
    playoff_prob_if_home_wins: float
    playoff_prob_if_away_wins: float
