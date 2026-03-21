from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.users import User, UserFavorite, Notification
from app.models.badges import Badge, UserBadge
from app.auth import get_current_user
from app.schemas.schemas import UserOut, UserUpdate, FavoriteCreate, FavoriteOut, NotificationOut, UserBadgeOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
async def update_me(
    body: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile. Only provided fields are updated."""
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.put("/me/push-token")
async def register_push_token(
    token: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register or update FCM push token for the current user."""
    user.push_token = token
    await db.commit()
    return {"status": "ok"}


@router.get("/me/favorites", response_model=list[FavoriteOut])
async def list_favorites(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserFavorite)
        .where(UserFavorite.user_id == user.id)
        .order_by(UserFavorite.created_at.desc())
    )
    return result.scalars().all()


@router.post("/me/favorites", response_model=FavoriteOut, status_code=201)
async def add_favorite(
    body: FavoriteCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.entity_type not in ("team", "athlete", "school"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="entity_type must be 'team', 'athlete', or 'school'",
        )

    # Check for duplicate
    result = await db.execute(
        select(UserFavorite).where(
            UserFavorite.user_id == user.id,
            UserFavorite.entity_type == body.entity_type,
            UserFavorite.entity_id == body.entity_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already in favorites",
        )

    fav = UserFavorite(
        user_id=user.id,
        entity_type=body.entity_type,
        entity_id=body.entity_id,
    )
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return fav


@router.delete("/me/favorites/{favorite_id}", status_code=204)
async def remove_favorite(
    favorite_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserFavorite).where(
            UserFavorite.id == favorite_id,
            UserFavorite.user_id == user.id,
        )
    )
    fav = result.scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    await db.delete(fav)
    await db.commit()


@router.get("/me/notifications", response_model=list[NotificationOut])
async def list_notifications(
    unread_only: bool = False,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.sent_at.desc())
    )
    if unread_only:
        query = query.where(Notification.read_status == False)  # noqa: E712
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/me/notifications/{notification_id}/read", response_model=NotificationOut)
async def mark_notification_read(
    notification_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.read_status = True
    await db.commit()
    await db.refresh(notif)
    return notif


@router.get("/me/badges", response_model=list[UserBadgeOut])
async def list_my_badges(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get badges for the current user."""
    result = await db.execute(
        select(
            UserBadge.id,
            UserBadge.badge_id,
            Badge.name.label("badge_name"),
            Badge.icon.label("badge_icon"),
            Badge.rarity.label("badge_rarity"),
            UserBadge.earned_at,
            UserBadge.description,
        )
        .join(Badge, UserBadge.badge_id == Badge.id)
        .where(UserBadge.user_id == user.id)
        .order_by(UserBadge.earned_at.desc())
    )
    rows = result.all()
    return [
        UserBadgeOut(
            id=r.id,
            badge_id=r.badge_id,
            badge_name=r.badge_name,
            badge_icon=r.badge_icon,
            badge_rarity=r.badge_rarity,
            earned_at=r.earned_at,
            description=r.description,
        )
        for r in rows
    ]


@router.get("/{user_id}/badges", response_model=list[UserBadgeOut])
async def list_user_badges(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get badges for any user."""
    result = await db.execute(
        select(
            UserBadge.id,
            UserBadge.badge_id,
            Badge.name.label("badge_name"),
            Badge.icon.label("badge_icon"),
            Badge.rarity.label("badge_rarity"),
            UserBadge.earned_at,
            UserBadge.description,
        )
        .join(Badge, UserBadge.badge_id == Badge.id)
        .where(UserBadge.user_id == user_id)
        .order_by(UserBadge.earned_at.desc())
    )
    rows = result.all()
    return [
        UserBadgeOut(
            id=r.id,
            badge_id=r.badge_id,
            badge_name=r.badge_name,
            badge_icon=r.badge_icon,
            badge_rarity=r.badge_rarity,
            earned_at=r.earned_at,
            description=r.description,
        )
        for r in rows
    ]
