from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.teams import Team
from app.models.schools import School
from app.models.games import Game
from app.models.power_ratings import PowerRating
from app.models.predictions import ProjectedRating, GameImpactAnalysis
from app.models.hype import HypeScore
from app.models.users import User
from app.auth import get_current_user, require_premium
from app.schemas.schemas import TeamOut, GameOut, PowerRatingOut, ProjectedRatingOut, WhatsAtStakeOut, HypeScoreOut

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


@router.get("/{team_id}/whats-at-stake", response_model=WhatsAtStakeOut)
async def get_whats_at_stake(
    team_id: int,
    user: User = Depends(require_premium),
    db: AsyncSession = Depends(get_db),
):
    """Simplified card data for the next upcoming game.

    Shows current rating/rank plus projected rating, rank, and playoff
    probability under win vs loss scenarios. Premium only.
    """
    # Verify team exists
    team_result = await db.execute(select(Team).where(Team.id == team_id))
    team = team_result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Find next scheduled (unplayed) game
    next_game_query = (
        select(Game)
        .where(
            ((Game.home_team_id == team_id) | (Game.away_team_id == team_id)),
            Game.status == "scheduled",
        )
        .order_by(Game.game_date, Game.week_number)
        .limit(1)
    )
    result = await db.execute(next_game_query)
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="No upcoming games found")

    is_home = game.home_team_id == team_id
    opponent_id = game.away_team_id if is_home else game.home_team_id

    # Get opponent school name
    opp_team_result = await db.execute(
        select(Team).where(Team.id == opponent_id)
    )
    opp_team = opp_team_result.scalar_one_or_none()
    opp_school_name = None
    if opp_team:
        school_result = await db.execute(
            select(School).where(School.id == opp_team.school_id)
        )
        opp_school = school_result.scalar_one_or_none()
        if opp_school:
            opp_school_name = opp_school.name

    # Get current power rating
    pr_query = (
        select(PowerRating)
        .where(PowerRating.team_id == team_id)
        .order_by(PowerRating.season_year.desc(), PowerRating.week_number.desc())
        .limit(1)
    )
    pr_result = await db.execute(pr_query)
    current_pr = pr_result.scalar_one_or_none()

    # Get impact analysis for this game
    impact_query = (
        select(GameImpactAnalysis)
        .where(
            GameImpactAnalysis.game_id == game.id,
            GameImpactAnalysis.affected_team_id == team_id,
        )
        .order_by(GameImpactAnalysis.created_at.desc())
        .limit(1)
    )
    impact_result = await db.execute(impact_query)
    impact = impact_result.scalar_one_or_none()

    # Build response — use impact data if available, otherwise nulls
    if impact:
        if is_home:
            rating_win = float(impact.rating_if_home_wins) if impact.rating_if_home_wins else None
            rating_loss = float(impact.rating_if_away_wins) if impact.rating_if_away_wins else None
            rank_win = impact.rank_if_home_wins
            rank_loss = impact.rank_if_away_wins
            pp_win = float(impact.playoff_prob_if_home_wins) if impact.playoff_prob_if_home_wins else None
            pp_loss = float(impact.playoff_prob_if_away_wins) if impact.playoff_prob_if_away_wins else None
        else:
            rating_win = float(impact.rating_if_away_wins) if impact.rating_if_away_wins else None
            rating_loss = float(impact.rating_if_home_wins) if impact.rating_if_home_wins else None
            rank_win = impact.rank_if_away_wins
            rank_loss = impact.rank_if_home_wins
            pp_win = float(impact.playoff_prob_if_away_wins) if impact.playoff_prob_if_away_wins else None
            pp_loss = float(impact.playoff_prob_if_home_wins) if impact.playoff_prob_if_home_wins else None
    else:
        rating_win = rating_loss = None
        rank_win = rank_loss = None
        pp_win = pp_loss = None

    return WhatsAtStakeOut(
        team_id=team_id,
        game_id=game.id,
        opponent_team_id=opponent_id,
        opponent_school_name=opp_school_name,
        game_date=game.game_date,
        week_number=game.week_number,
        is_home=is_home,
        current_rating=float(current_pr.power_rating) if current_pr else None,
        current_rank=current_pr.rank_in_division if current_pr else None,
        projected_rating_if_win=rating_win,
        projected_rank_if_win=rank_win,
        playoff_prob_if_win=pp_win,
        projected_rating_if_loss=rating_loss,
        projected_rank_if_loss=rank_loss,
        playoff_prob_if_loss=pp_loss,
    )


@router.get("/{team_id}/hype", response_model=HypeScoreOut)
async def get_team_hype(team_id: int, db: AsyncSession = Depends(get_db)):
    """Get latest hype score for a team."""
    result = await db.execute(select(Team).where(Team.id == team_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Team not found")

    hype_result = await db.execute(
        select(HypeScore)
        .where(HypeScore.team_id == team_id)
        .order_by(HypeScore.season_year.desc(), HypeScore.week_number.desc())
        .limit(1)
    )
    hype = hype_result.scalar_one_or_none()
    if not hype:
        raise HTTPException(status_code=404, detail="No hype data found for this team")
    return hype
