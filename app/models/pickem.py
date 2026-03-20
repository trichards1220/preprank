from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class PickemContest(Base):
    __tablename__ = "pickem_contests"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    season_year: Mapped[int] = mapped_column(Integer, nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="upcoming")  # upcoming, active, closed, scored
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PickemSlate(Base):
    __tablename__ = "pickem_slates"
    __table_args__ = (
        UniqueConstraint("contest_id", "game_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey("pickem_contests.id", ondelete="CASCADE"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)


class PickemPick(Base):
    __tablename__ = "pickem_picks"
    __table_args__ = (
        UniqueConstraint("user_id", "slate_id", "game_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    slate_id: Mapped[int] = mapped_column(ForeignKey("pickem_slates.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    picked_winner_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    is_correct: Mapped[bool | None] = mapped_column(Boolean)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    picked_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PickemLeaderboard(Base):
    __tablename__ = "pickem_leaderboard"
    __table_args__ = (
        UniqueConstraint("contest_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey("pickem_contests.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    school_id: Mapped[int | None] = mapped_column(ForeignKey("schools.id"))
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    correct_picks: Mapped[int] = mapped_column(Integer, default=0)
    upset_picks: Mapped[int] = mapped_column(Integer, default=0)
    rank: Mapped[int | None] = mapped_column(Integer)
    streak: Mapped[int] = mapped_column(Integer, default=0)
