from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, EmailStr


# --- Schools ---

class SchoolBase(BaseModel):
    name: str
    city: str | None = None
    parish: str | None = None
    classification: str | None = None
    division: int | None = None
    select_status: bool = False
    enrollment: int | None = None

class SchoolOut(SchoolBase):
    id: int
    model_config = {"from_attributes": True}


# --- Sports ---

class SportOut(BaseModel):
    id: int
    name: str
    season: str
    has_power_rating: bool
    model_config = {"from_attributes": True}


# --- Teams ---

class TeamOut(BaseModel):
    id: int
    school_id: int
    sport_id: int
    season_year: int
    head_coach: str | None = None
    model_config = {"from_attributes": True}


# --- Games ---

class GameBase(BaseModel):
    home_team_id: int
    away_team_id: int
    sport_id: int
    game_date: date
    home_score: int | None = None
    away_score: int | None = None
    status: str = "scheduled"
    is_district: bool = False
    is_playoff: bool = False
    week_number: int | None = None

class GameOut(GameBase):
    id: int
    model_config = {"from_attributes": True}


# --- Power Ratings ---

class PowerRatingOut(BaseModel):
    id: int
    team_id: int
    week_number: int
    season_year: int
    power_rating: float
    strength_factor: float | None = None
    rank_in_division: int | None = None
    calculated_at: datetime
    model_config = {"from_attributes": True}


# --- Predictions ---

class ProjectedRatingOut(BaseModel):
    team_id: int
    projected_rating_mean: float
    projected_rating_p10: float
    projected_rating_p90: float
    playoff_probability: float
    projected_rank: int | None = None
    model_config = {"from_attributes": True}

class GamePredictionOut(BaseModel):
    game_id: int
    home_win_probability: float
    predicted_home_score: float | None = None
    predicted_away_score: float | None = None
    model_config = {"from_attributes": True}


# --- What's At Stake ---

class StakeAnalysis(BaseModel):
    game_id: int
    team_id: int
    current_rating: float
    projected_rating_if_win: float
    projected_rating_if_loss: float
    playoff_prob_if_win: float
    playoff_prob_if_loss: float
    projected_rank_if_win: int | None = None
    projected_rank_if_loss: int | None = None
