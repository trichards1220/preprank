from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100))
    parish: Mapped[str] = mapped_column(String(100))
    classification: Mapped[str] = mapped_column(String(10))  # 1A-5A
    division: Mapped[int] = mapped_column(Integer, nullable=True)
    select_status: Mapped[bool] = mapped_column(Boolean, default=False)
    enrollment: Mapped[int] = mapped_column(Integer, nullable=True)
    lhsaa_member_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=True)

    teams = relationship("Team", back_populates="school")
    athletes = relationship("Athlete", back_populates="school")
