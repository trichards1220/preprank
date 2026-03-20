from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.predictions import ProjectedRating, GamePrediction
from app.schemas.schemas import ProjectedRatingOut, GamePredictionOut

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/projected-ratings", response_model=list[ProjectedRatingOut])
async def list_projected_ratings(
    simulation_id: int | None = None,
    team_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(ProjectedRating)
    if simulation_id:
        query = query.where(ProjectedRating.simulation_id == simulation_id)
    if team_id:
        query = query.where(ProjectedRating.team_id == team_id)
    query = query.order_by(ProjectedRating.projected_rating_mean.desc())
    result = await db.execute(query)
    return result.scalars().all()


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
