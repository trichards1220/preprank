from datetime import datetime
from pydantic import BaseModel


class SimulationRunRequest(BaseModel):
    sport: str
    season_year: int
    week_number: int
    num_runs: int = 10000
    playoff_spots: int = 8


class SimulationOut(BaseModel):
    id: int
    sport_id: int
    season_year: int
    week_number: int
    run_count: int
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProjectedRatingOut(BaseModel):
    team_id: int
    school_name: str | None = None
    division: str | None = None
    projected_rating_mean: float
    projected_rating_median: float
    projected_rating_p10: float
    projected_rating_p90: float
    projected_rank_mean: float
    playoff_probability: float
    championship_probability: float
    projected_wins_mean: float
    projected_losses_mean: float

    model_config = {"from_attributes": True}


class GameImpactOut(BaseModel):
    affected_team_id: int
    school_name: str | None = None
    rating_if_home_wins: float
    rating_if_away_wins: float
    rank_if_home_wins: int
    rank_if_away_wins: int
    playoff_prob_if_home_wins: float
    playoff_prob_if_away_wins: float

    model_config = {"from_attributes": True}
