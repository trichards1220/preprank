from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class PowerRating(Base):
    __tablename__ = "power_ratings"
    __table_args__ = (
        UniqueConstraint("team_id", "week_number", "season_year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    season_year: Mapped[int] = mapped_column(Integer, nullable=False)
    power_rating: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    strength_factor: Mapped[float | None] = mapped_column(Numeric(6, 2))
    rank_in_division: Mapped[int | None] = mapped_column(Integer)
    total_teams_in_division: Mapped[int | None] = mapped_column(Integer)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    team = relationship("Team", back_populates="power_ratings")
