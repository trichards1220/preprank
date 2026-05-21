from datetime import date
from pydantic import BaseModel, Field


class GameCreateRequest(BaseModel):
    home_team_id: int
    away_team_id: int
    sport_id: int
    season_year: int
    game_date: date
    week_number: int | None = None
    home_score: int | None = Field(None, ge=0)
    away_score: int | None = Field(None, ge=0)
    status: str = "scheduled"
    is_district: bool = False
    is_playoff: bool = False
    is_championship: bool = False
    source: str = "user"


class GameUpdateRequest(BaseModel):
    home_score: int | None = Field(None, ge=0)
    away_score: int | None = Field(None, ge=0)
    status: str | None = None
    week_number: int | None = None
