from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, EmailStr


# --- Schools ---

class SchoolBase(BaseModel):
    name: str
    city: str | None = None
    parish: str | None = None
    classification: str | None = None
    division: str | None = None
    select_status: str | None = None
    enrollment: int | None = None

class SchoolOut(SchoolBase):
    id: int
    created_at: datetime | None = None
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
    division: str | None = None
    select_status: str | None = None
    model_config = {"from_attributes": True}


# --- Games ---

class GameBase(BaseModel):
    home_team_id: int
    away_team_id: int
    sport_id: int
    season_year: int
    game_date: date | None = None
    week_number: int | None = None
    home_score: int | None = None
    away_score: int | None = None
    status: str = "scheduled"
    is_district: bool = False
    is_playoff: bool = False
    is_championship: bool = False
    is_out_of_state: bool = False
    source: str | None = None

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
    total_teams_in_division: int | None = None
    calculated_at: datetime | None = None
    model_config = {"from_attributes": True}


# --- Predictions ---

class ProjectedRatingOut(BaseModel):
    team_id: int
    projected_rating_mean: float | None = None
    projected_rating_median: float | None = None
    projected_rating_p10: float | None = None
    projected_rating_p90: float | None = None
    projected_rank_mean: float | None = None
    playoff_probability: float | None = None
    championship_probability: float | None = None
    projected_wins_mean: float | None = None
    projected_losses_mean: float | None = None
    made_playoffs: float | None = None
    won_round1: float | None = None
    reached_quarters: float | None = None
    reached_semis: float | None = None
    reached_championship: float | None = None
    won_title: float | None = None
    model_config = {"from_attributes": True}

class GamePredictionOut(BaseModel):
    game_id: int
    home_win_probability: float | None = None
    predicted_home_score: float | None = None
    predicted_away_score: float | None = None
    predicted_spread: float | None = None
    model_config = {"from_attributes": True}

class GameImpactOut(BaseModel):
    game_id: int
    affected_team_id: int
    rating_if_home_wins: float | None = None
    rating_if_away_wins: float | None = None
    rank_if_home_wins: int | None = None
    rank_if_away_wins: int | None = None
    playoff_prob_if_home_wins: float | None = None
    playoff_prob_if_away_wins: float | None = None
    model_config = {"from_attributes": True}


# --- Users / Auth ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None

class UserOut(BaseModel):
    id: int
    email: str
    first_name: str | None = None
    last_name: str | None = None
    subscription_tier: str
    subscription_expires: datetime | None = None
    created_at: datetime | None = None
    model_config = {"from_attributes": True}

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# --- Favorites ---

class FavoriteCreate(BaseModel):
    entity_type: str  # team, athlete, school
    entity_id: int

class FavoriteOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    created_at: datetime | None = None
    model_config = {"from_attributes": True}


# --- Notifications ---

class NotificationOut(BaseModel):
    id: int
    notification_type: str
    title: str | None = None
    message: str | None = None
    game_id: int | None = None
    read_status: bool
    sent_at: datetime | None = None
    model_config = {"from_attributes": True}
