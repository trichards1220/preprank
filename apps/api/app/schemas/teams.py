from pydantic import BaseModel


class TeamOut(BaseModel):
    id: int
    school_id: int
    sport_id: int
    season_year: int
    head_coach: str | None = None
    division: str | None = None
    select_status: str | None = None
    school_name: str
    sport_name: str

    model_config = {"from_attributes": True}
