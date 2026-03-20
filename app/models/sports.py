from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Sport(Base):
    __tablename__ = "sports"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    season: Mapped[str] = mapped_column(String(10))  # fall, winter, spring
    has_power_rating: Mapped[bool] = mapped_column(Boolean, default=True)
