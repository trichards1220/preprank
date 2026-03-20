from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class HypeScore(Base):
    __tablename__ = "hype_scores"
    __table_args__ = (
        UniqueConstraint("team_id", "week_number", "season_year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    season_year: Mapped[int] = mapped_column(Integer, nullable=False)
    hype_score: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    momentum_direction: Mapped[str] = mapped_column(String(10), nullable=False)  # rising, falling, steady
    win_streak: Mapped[int] = mapped_column(Integer, default=0)
    rating_change_4wk: Mapped[float | None] = mapped_column(Numeric(5, 2))
    calculated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
