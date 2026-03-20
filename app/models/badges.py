from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    icon: Mapped[str] = mapped_column(String(100), nullable=False)
    rarity: Mapped[str] = mapped_column(String(20), nullable=False)  # common, uncommon, rare, legendary
    criteria_type: Mapped[str] = mapped_column(String(50), nullable=False)
    criteria_value: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UserBadge(Base):
    __tablename__ = "user_badges"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id: Mapped[int] = mapped_column(ForeignKey("badges.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    game_id: Mapped[int | None] = mapped_column(ForeignKey("games.id"))
    description: Mapped[str | None] = mapped_column(String(500))
