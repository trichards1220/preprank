from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.power_ratings import PowerRating
from app.models.teams import Team
from app.schemas.schemas import PowerRatingOut

router = APIRouter(prefix="/power-ratings", tags=["power-ratings"])


@router.get("/", response_model=list[PowerRatingOut])
async def list_power_ratings(
    season_year: int | None = None,
    week_number: int | None = None,
    team_id: int | None = None,
    division: str | None = None,
    select_status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(PowerRating)
    if division or select_status:
        query = query.join(Team, PowerRating.team_id == Team.id)
        if division:
            query = query.where(Team.division == division)
        if select_status:
            query = query.where(Team.select_status == select_status)
    if season_year:
        query = query.where(PowerRating.season_year == season_year)
    if week_number:
        query = query.where(PowerRating.week_number == week_number)
    if team_id:
        query = query.where(PowerRating.team_id == team_id)
    query = query.order_by(PowerRating.power_rating.desc())
    result = await db.execute(query)
    return result.scalars().all()
