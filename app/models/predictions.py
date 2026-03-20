from datetime import datetime

from sqlalchemy import Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Simulation(Base):
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    season_year: Mapped[int] = mapped_column(Integer, nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    run_count: Mapped[int] = mapped_column(Integer, default=10_000)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProjectedRating(Base):
    __tablename__ = "projected_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    projected_rating_mean: Mapped[float] = mapped_column(Float, nullable=False)
    projected_rating_p10: Mapped[float] = mapped_column(Float, nullable=False)
    projected_rating_p90: Mapped[float] = mapped_column(Float, nullable=False)
    playoff_probability: Mapped[float] = mapped_column(Float, nullable=False)
    projected_rank: Mapped[int] = mapped_column(Integer, nullable=True)


class GamePrediction(Base):
    __tablename__ = "game_predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    home_win_probability: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_home_score: Mapped[float] = mapped_column(Float, nullable=True)
    predicted_away_score: Mapped[float] = mapped_column(Float, nullable=True)
