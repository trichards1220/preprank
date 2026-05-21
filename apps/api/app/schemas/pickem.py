from datetime import datetime
from pydantic import BaseModel


class ContestOut(BaseModel):
    id: int
    sport_id: int
    season_year: int
    week_number: int
    title: str
    status: str
    opens_at: datetime | None = None
    locks_at: datetime | None = None
    scored_at: datetime | None = None
    game_count: int = 0

    model_config = {"from_attributes": True}


class ContestCreateRequest(BaseModel):
    sport: str
    season_year: int
    week_number: int
    title: str | None = None
    opens_at: datetime | None = None
    locks_at: datetime | None = None


class PickRequest(BaseModel):
    game_id: int
    picked_team_id: int


class PicksBatchRequest(BaseModel):
    picks: list[PickRequest]


class EntryOut(BaseModel):
    id: int
    game_id: int
    picked_team_id: int
    picked_team_name: str | None = None
    home_team_name: str | None = None
    away_team_name: str | None = None
    home_score: int | None = None
    away_score: int | None = None
    is_correct: bool | None = None
    points_earned: int = 0

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    display_name: str
    total_correct: int
    total_picks: int
    accuracy_pct: float
    total_points: int


class SchoolLeaderboardEntry(BaseModel):
    rank: int
    school_name: str
    school_id: int
    total_correct: int
    total_picks: int
    accuracy_pct: float
    participant_count: int


class BadgeOut(BaseModel):
    id: int
    badge_type: str
    badge_name: str
    description: str | None = None
    earned_at: datetime

    model_config = {"from_attributes": True}
