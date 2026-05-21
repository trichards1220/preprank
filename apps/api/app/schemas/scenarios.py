from pydantic import BaseModel


class LockedOutcome(BaseModel):
    game_id: int
    winner_team_id: int


class ScenarioRequest(BaseModel):
    team_id: int
    locked_outcomes: list[LockedOutcome] = []
    sport: str = "Football"
    season_year: int = 2025
    week_number: int = 11


class ScenarioTeamRequest(BaseModel):
    team_id: int
    sport: str = "Football"
    season_year: int = 2025
    week_number: int = 11


class CompareRequest(BaseModel):
    team_id: int
    scenario_a: list[LockedOutcome]
    scenario_b: list[LockedOutcome]
    sport: str = "Football"
    season_year: int = 2025
    week_number: int = 11


class ScenarioResult(BaseModel):
    team_id: int
    school_name: str | None = None
    projected_rating: float
    projected_rank: float
    playoff_probability: float
    championship_probability: float
    projected_wins: float
    projected_losses: float
    locked_count: int = 0
    remaining_count: int = 0


class CompareResult(BaseModel):
    team_id: int
    school_name: str | None = None
    scenario_a: ScenarioResult
    scenario_b: ScenarioResult
    rating_delta: float
    rank_delta: float
    playoff_delta: float
