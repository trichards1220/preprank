from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.teams import Team
from app.schemas.schemas import TeamOut

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/", response_model=list[TeamOut])
async def list_teams(
    school_id: int | None = None,
    sport_id: int | None = None,
    season_year: int | None = None,
    division: str | None = None,
    select_status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Team)
    if school_id:
        query = query.where(Team.school_id == school_id)
    if sport_id:
        query = query.where(Team.sport_id == sport_id)
    if season_year:
        query = query.where(Team.season_year == season_year)
    if division:
        query = query.where(Team.division == division)
    if select_status:
        query = query.where(Team.select_status == select_status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{team_id}", response_model=TeamOut)
async def get_team(team_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
