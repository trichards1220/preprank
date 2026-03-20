from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Simulation(Base):
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    season_year: Mapped[int] = mapped_column(Integer, nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    run_count: Mapped[int] = mapped_column(Integer, default=10_000)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, running, completed, failed
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ProjectedRating(Base):
    __tablename__ = "projected_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    projected_rating_mean: Mapped[float | None] = mapped_column(Numeric(6, 2))
    projected_rating_median: Mapped[float | None] = mapped_column(Numeric(6, 2))
    projected_rating_p10: Mapped[float | None] = mapped_column(Numeric(6, 2))
    projected_rating_p90: Mapped[float | None] = mapped_column(Numeric(6, 2))
    projected_rank_mean: Mapped[float | None] = mapped_column(Numeric(6, 1))
    playoff_probability: Mapped[float | None] = mapped_column(Numeric(5, 2))
    championship_probability: Mapped[float | None] = mapped_column(Numeric(5, 2))
    projected_wins_mean: Mapped[float | None] = mapped_column(Numeric(4, 1))
    projected_losses_mean: Mapped[float | None] = mapped_column(Numeric(4, 1))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class GamePrediction(Base):
    __tablename__ = "game_predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False)
    home_win_probability: Mapped[float | None] = mapped_column(Numeric(5, 2))
    predicted_home_score: Mapped[float | None] = mapped_column(Numeric(5, 1))
    predicted_away_score: Mapped[float | None] = mapped_column(Numeric(5, 1))
    predicted_spread: Mapped[float | None] = mapped_column(Numeric(5, 1))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class GameImpactAnalysis(Base):
    __tablename__ = "game_impact_analysis"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False)
    affected_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    rating_if_home_wins: Mapped[float | None] = mapped_column(Numeric(6, 2))
    rating_if_away_wins: Mapped[float | None] = mapped_column(Numeric(6, 2))
    rank_if_home_wins: Mapped[int | None] = mapped_column(Integer)
    rank_if_away_wins: Mapped[int | None] = mapped_column(Integer)
    playoff_prob_if_home_wins: Mapped[float | None] = mapped_column(Numeric(5, 2))
    playoff_prob_if_away_wins: Mapped[float | None] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
