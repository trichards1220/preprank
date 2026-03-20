from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sports import Sport
from app.models.teams import Team
from app.schemas.schemas import SportOut, TeamOut

router = APIRouter(prefix="/sports", tags=["sports"])


@router.get("/", response_model=list[SportOut])
async def list_sports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sport).order_by(Sport.season, Sport.name))
    return result.scalars().all()


@router.get("/{sport_id}", response_model=SportOut)
async def get_sport(sport_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sport).where(Sport.id == sport_id))
    sport = result.scalar_one_or_none()
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    return sport


@router.get("/{sport_id}/teams", response_model=list[TeamOut])
async def list_sport_teams(
    sport_id: int,
    season_year: int | None = None,
    division: str | None = None,
    select_status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    # Verify sport exists
    sport_result = await db.execute(select(Sport).where(Sport.id == sport_id))
    if not sport_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sport not found")

    query = select(Team).where(Team.sport_id == sport_id)
    if season_year:
        query = query.where(Team.season_year == season_year)
    if division:
        query = query.where(Team.division == division)
    if select_status:
        query = query.where(Team.select_status == select_status)
    result = await db.execute(query)
    return result.scalars().all()
