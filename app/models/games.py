from datetime import date, datetime

from sqlalchemy import Integer, ForeignKey, String, Boolean, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    season_year: Mapped[int] = mapped_column(Integer, nullable=False)
    game_date: Mapped[date | None] = mapped_column(Date)
    week_number: Mapped[int | None] = mapped_column(Integer)
    home_score: Mapped[int | None] = mapped_column(Integer)
    away_score: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")  # scheduled, final, disputed, cancelled, forfeit
    is_district: Mapped[bool] = mapped_column(Boolean, default=False)
    is_playoff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_championship: Mapped[bool] = mapped_column(Boolean, default=False)
    is_out_of_state: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str | None] = mapped_column(String(50))  # lhsaa, scorestream, maxpreps, user
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
