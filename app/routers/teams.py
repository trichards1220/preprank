from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.teams import Team
from app.models.games import Game
from app.models.power_ratings import PowerRating
from app.models.predictions import ProjectedRating
from app.models.users import User
from app.auth import get_current_user, require_premium
from app.schemas.schemas import TeamOut, GameOut, PowerRatingOut, ProjectedRatingOut

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


@router.get("/{team_id}/schedule", response_model=list[GameOut])
async def get_team_schedule(team_id: int, db: AsyncSession = Depends(get_db)):
    """Get all games for a team, ordered by week number then date."""
    result = await db.execute(select(Team).where(Team.id == team_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Team not found")

    query = (
        select(Game)
        .where((Game.home_team_id == team_id) | (Game.away_team_id == team_id))
        .order_by(Game.week_number, Game.game_date)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{team_id}/power-rating", response_model=list[PowerRatingOut])
async def get_team_power_rating(
    team_id: int,
    season_year: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get power rating history for a team, ordered by week."""
    result = await db.execute(select(Team).where(Team.id == team_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Team not found")

    query = select(PowerRating).where(PowerRating.team_id == team_id)
    if season_year:
        query = query.where(PowerRating.season_year == season_year)
    query = query.order_by(PowerRating.season_year.desc(), PowerRating.week_number.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{team_id}/projections", response_model=ProjectedRatingOut)
async def get_team_projections(
    team_id: int,
    simulation_id: int | None = None,
    user: User = Depends(require_premium),
    db: AsyncSession = Depends(get_db),
):
    """Get projected ratings and playoff probabilities for a team. Premium only."""
    result = await db.execute(select(Team).where(Team.id == team_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Team not found")

    query = select(ProjectedRating).where(ProjectedRating.team_id == team_id)
    if simulation_id:
        query = query.where(ProjectedRating.simulation_id == simulation_id)
    else:
        query = query.order_by(ProjectedRating.created_at.desc())
    query = query.limit(1)

    result = await db.execute(query)
    projection = result.scalar_one_or_none()
    if not projection:
        raise HTTPException(status_code=404, detail="No projections found for this team")
    return projection
