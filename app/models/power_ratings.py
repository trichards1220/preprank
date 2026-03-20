from datetime import datetime

from sqlalchemy import Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PowerRating(Base):
    __tablename__ = "power_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    season_year: Mapped[int] = mapped_column(Integer, nullable=False)
    power_rating: Mapped[float] = mapped_column(Float, nullable=False)
    strength_factor: Mapped[float] = mapped_column(Float, nullable=True)
    rank_in_division: Mapped[int] = mapped_column(Integer, nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    team = relationship("Team", back_populates="power_ratings")
