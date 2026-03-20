from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.hype import HypeScore
from app.models.teams import Team
from app.models.schools import School
from app.schemas.schemas import HypeRivalryOut, HypeScoreOut

router = APIRouter(prefix="/hype", tags=["hype"])


@router.get("/district/{sport_id}/{district}", response_model=HypeRivalryOut)
async def get_district_hype(
    sport_id: int,
    district: str,
    season_year: int | None = None,
    week_number: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """District rivalry tracker — hype scores for all teams in a district."""
    # Find teams in the given sport and district
    team_query = select(Team).where(
        Team.sport_id == sport_id,
        Team.division == district,
    )
    if season_year:
        team_query = team_query.where(Team.season_year == season_year)

    team_result = await db.execute(team_query)
    teams = team_result.scalars().all()
    if not teams:
        raise HTTPException(status_code=404, detail="No teams found for this district")

    team_ids = [t.id for t in teams]

    # If week_number not specified, find the latest week with hype data
    if week_number is None:
        latest_query = (
            select(HypeScore.week_number)
            .where(HypeScore.team_id.in_(team_ids))
            .order_by(HypeScore.week_number.desc())
            .limit(1)
        )
        latest_result = await db.execute(latest_query)
        latest_week = latest_result.scalar_one_or_none()
        if not latest_week:
            raise HTTPException(status_code=404, detail="No hype data found for this district")
        week_number = latest_week

    # Get hype scores for those teams
    hype_query = select(HypeScore).where(
        HypeScore.team_id.in_(team_ids),
        HypeScore.week_number == week_number,
    )
    if season_year:
        hype_query = hype_query.where(HypeScore.season_year == season_year)

    hype_result = await db.execute(hype_query)
    hype_scores = hype_result.scalars().all()

    return HypeRivalryOut(
        sport_id=sport_id,
        district=district,
        teams=[
            HypeScoreOut(
                team_id=h.team_id,
                week_number=h.week_number,
                season_year=h.season_year,
                hype_score=float(h.hype_score),
                momentum_direction=h.momentum_direction,
                win_streak=h.win_streak,
                rating_change_4wk=float(h.rating_change_4wk) if h.rating_change_4wk else None,
            )
            for h in hype_scores
        ],
    )


@router.get("/share/{team_id}")
async def get_share_card(
    team_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get data for a shareable hype card. Image generation is a future feature."""
    # Get latest hype score
    hype_result = await db.execute(
        select(HypeScore)
        .where(HypeScore.team_id == team_id)
        .order_by(HypeScore.season_year.desc(), HypeScore.week_number.desc())
        .limit(1)
    )
    hype = hype_result.scalar_one_or_none()
    if not hype:
        raise HTTPException(status_code=404, detail="No hype data found for this team")

    # Get team and school name
    team_result = await db.execute(select(Team).where(Team.id == team_id))
    team = team_result.scalar_one_or_none()
    school_name = None
    if team:
        school_result = await db.execute(select(School).where(School.id == team.school_id))
        school = school_result.scalar_one_or_none()
        if school:
            school_name = school.name

    return {
        "share_url": f"/hype/share/{team_id}",
        "hype_score": float(hype.hype_score),
        "school_name": school_name,
        "momentum": hype.momentum_direction,
    }
