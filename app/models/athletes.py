from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Athlete(Base):
    __tablename__ = "athletes"

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    graduation_year: Mapped[int | None] = mapped_column(Integer)
    position: Mapped[str | None] = mapped_column(String(50))
    jersey_number: Mapped[str | None] = mapped_column(String(10))
    height: Mapped[str | None] = mapped_column(String(10))
    weight: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    school = relationship("School", back_populates="athletes")
    stats = relationship("AthleteStat", back_populates="athlete")


class AthleteStat(Base):
    __tablename__ = "athlete_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    athlete_id: Mapped[int] = mapped_column(ForeignKey("athletes.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    stat_type: Mapped[str] = mapped_column(String(50), nullable=False)
    stat_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    source: Mapped[str | None] = mapped_column(String(50))  # maxpreps, gamechanger, user, coach
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    athlete = relationship("Athlete", back_populates="stats")
