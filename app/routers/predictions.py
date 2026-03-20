from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.predictions import ProjectedRating, GamePrediction
from app.models.teams import Team
from app.schemas.schemas import ProjectedRatingOut, GamePredictionOut

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/projected-ratings", response_model=list[ProjectedRatingOut])
async def list_projected_ratings(
    simulation_id: int | None = None,
    team_id: int | None = None,
    division: str | None = None,
    select_status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(ProjectedRating)
    if division or select_status:
        query = query.join(Team, ProjectedRating.team_id == Team.id)
        if division:
            query = query.where(Team.division == division)
        if select_status:
            query = query.where(Team.select_status == select_status)
    if simulation_id:
        query = query.where(ProjectedRating.simulation_id == simulation_id)
    if team_id:
        query = query.where(ProjectedRating.team_id == team_id)
    query = query.order_by(ProjectedRating.projected_rating_mean.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/teams/{team_id}/playoff-probabilities", response_model=ProjectedRatingOut)
async def get_team_playoff_probabilities(
    team_id: int,
    simulation_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get full playoff probability breakdown for a specific team.

    Returns made_playoffs, won_round1, reached_quarters, reached_semis,
    reached_championship, and won_title probabilities from the most recent
    simulation (or a specific simulation_id if provided).
    """
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


@router.get("/game-predictions", response_model=list[GamePredictionOut])
async def list_game_predictions(
    simulation_id: int | None = None,
    game_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(GamePrediction)
    if simulation_id:
        query = query.where(GamePrediction.simulation_id == simulation_id)
    if game_id:
        query = query.where(GamePrediction.game_id == game_id)
    result = await db.execute(query)
    return result.scalars().all()
