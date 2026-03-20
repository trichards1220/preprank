from datetime import date

from sqlalchemy import Integer, ForeignKey, String, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    game_date: Mapped[date] = mapped_column(Date, nullable=False)
    home_score: Mapped[int] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")  # scheduled, final, disputed
    is_district: Mapped[bool] = mapped_column(Boolean, default=False)
    is_playoff: Mapped[bool] = mapped_column(Boolean, default=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=True)
