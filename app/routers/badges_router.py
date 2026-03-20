from fastapi import APIRouter, Depends
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.badges import Badge, UserBadge
from app.models.users import User
from app.schemas.schemas import BadgeOut, BadgeLeaderboardEntry

router = APIRouter(prefix="/badges", tags=["badges"])


@router.get("/", response_model=list[BadgeOut])
async def list_badges(db: AsyncSession = Depends(get_db)):
    """Get all available badges."""
    result = await db.execute(select(Badge).order_by(Badge.name))
    return result.scalars().all()


@router.get("/leaderboard", response_model=list[BadgeLeaderboardEntry])
async def get_badge_leaderboard(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Users with the most badges."""
    # Subquery to find each user's rarest badge
    rarity_order = sa_func.case(
        (Badge.rarity == "legendary", 1),
        (Badge.rarity == "rare", 2),
        (Badge.rarity == "uncommon", 3),
        else_=4,
    )

    query = (
        select(
            UserBadge.user_id,
            User.first_name,
            User.last_name,
            sa_func.count(UserBadge.id).label("badge_count"),
            sa_func.min(
                sa_func.case(
                    (rarity_order == sa_func.min(rarity_order), Badge.name),
                )
            ).label("rarest_badge"),
        )
        .join(User, UserBadge.user_id == User.id)
        .join(Badge, UserBadge.badge_id == Badge.id)
        .group_by(UserBadge.user_id, User.first_name, User.last_name)
        .order_by(sa_func.count(UserBadge.id).desc())
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()
    return [
        BadgeLeaderboardEntry(
            user_id=r.user_id,
            first_name=r.first_name,
            last_name=r.last_name,
            badge_count=r.badge_count,
            rarest_badge=r.rarest_badge,
        )
        for r in rows
    ]
