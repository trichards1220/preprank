from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sports import Sport
from app.models.teams import Team
from app.models.schools import School
from app.models.power_ratings import PowerRating
from app.schemas.schemas import SportOut, TeamOut, StandingsOut, StandingEntry

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


@router.get("/{sport_id}/standings", response_model=list[StandingsOut])
async def get_standings(
    sport_id: int,
    season_year: int,
    division: str | None = None,
    select_status: str | None = None,
    week_number: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get division standings/leaderboard for a sport and season.

    Returns one StandingsOut per division+select_status bracket, each containing
    teams ranked by power rating. If week_number is not specified, uses the
    most recent week with data.
    """
    sport_result = await db.execute(select(Sport).where(Sport.id == sport_id))
    if not sport_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sport not found")

    # Find the target week
    if week_number is None:
        max_week_result = await db.execute(
            select(sa_func.max(PowerRating.week_number))
            .join(Team, PowerRating.team_id == Team.id)
            .where(Team.sport_id == sport_id, PowerRating.season_year == season_year)
        )
        week_number = max_week_result.scalar()
        if week_number is None:
            return []

    # Query power ratings joined with team and school info
    query = (
        select(PowerRating, Team, School)
        .join(Team, PowerRating.team_id == Team.id)
        .join(School, Team.school_id == School.id)
        .where(
            Team.sport_id == sport_id,
            PowerRating.season_year == season_year,
            PowerRating.week_number == week_number,
        )
    )
    if division:
        query = query.where(Team.division == division)
    if select_status:
        query = query.where(Team.select_status == select_status)

    query = query.order_by(Team.division, Team.select_status, PowerRating.power_rating.desc())
    result = await db.execute(query)
    rows = result.all()

    # Group by bracket
    brackets: dict[tuple[str, str], list[StandingEntry]] = {}
    for pr, team, school in rows:
        key = (team.division or "", team.select_status or "")
        brackets.setdefault(key, []).append(StandingEntry(
            team_id=team.id,
            school_name=school.name,
            division=team.division,
            select_status=team.select_status,
            power_rating=float(pr.power_rating),
            strength_factor=float(pr.strength_factor) if pr.strength_factor else None,
            rank_in_division=pr.rank_in_division,
        ))

    standings_list = []
    for (div, sel), entries in sorted(brackets.items()):
        standings_list.append(StandingsOut(
            sport_id=sport_id,
            season_year=season_year,
            division=div,
            select_status=sel,
            week_number=week_number,
            standings=entries,
        ))

    return standings_list
