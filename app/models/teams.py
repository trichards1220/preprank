from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint("school_id", "sport_id", "season_year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    season_year: Mapped[int] = mapped_column(Integer, nullable=False)
    head_coach: Mapped[str | None] = mapped_column(String(200))
    division: Mapped[str | None] = mapped_column(String(10))  # I, II, III, IV
    select_status: Mapped[str | None] = mapped_column(String(20))  # Select, Non-Select
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    school = relationship("School", back_populates="teams")
    power_ratings = relationship("PowerRating", back_populates="team")
