from datetime import date

from pydantic import BaseModel


class GameOut(BaseModel):
    id: int
    home_team_id: int
    away_team_id: int
    sport_id: int
    season_year: int
    game_date: date | None = None
    week_number: int | None = None
    home_score: int | None = None
    away_score: int | None = None
    status: str
    is_district: bool
    is_playoff: bool
    is_championship: bool
    is_out_of_state: bool
    home_team_name: str | None = None
    away_team_name: str | None = None

    model_config = {"from_attributes": True}
