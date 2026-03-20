from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Athlete(Base):
    __tablename__ = "athletes"

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    graduation_year: Mapped[int] = mapped_column(Integer, nullable=True)
    position: Mapped[str] = mapped_column(String(50), nullable=True)
    jersey_number: Mapped[int] = mapped_column(Integer, nullable=True)

    school = relationship("School", back_populates="athletes")
    stats = relationship("AthleteStat", back_populates="athlete")


class AthleteStat(Base):
    __tablename__ = "athlete_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    athlete_id: Mapped[int] = mapped_column(ForeignKey("athletes.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    stat_type: Mapped[str] = mapped_column(String(50), nullable=False)
    stat_value: Mapped[float] = mapped_column(Float, nullable=False)

    athlete = relationship("Athlete", back_populates="stats")
