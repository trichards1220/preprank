from datetime import datetime

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str | None] = mapped_column(String(100))
    parish: Mapped[str | None] = mapped_column(String(100))
    classification: Mapped[str | None] = mapped_column(String(10))  # 5A, 4A, 3A, 2A, 1A
    division: Mapped[str | None] = mapped_column(String(10))  # I, II, III, IV
    select_status: Mapped[str | None] = mapped_column(String(20))  # Select, Non-Select
    enrollment: Mapped[int | None] = mapped_column(Integer)
    lhsaa_member_id: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    teams = relationship("Team", back_populates="school")
    athletes = relationship("Athlete", back_populates="school")
