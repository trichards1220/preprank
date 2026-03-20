from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.predictions import ProjectedRating, GamePrediction
from app.models.teams import Team
from app.models.users import User
from app.auth import require_premium
from app.schemas.schemas import ProjectedRatingOut, GamePredictionOut

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/projected-ratings", response_model=list[ProjectedRatingOut])
async def list_projected_ratings(
    simulation_id: int | None = None,
    team_id: int | None = None,
    division: str | None = None,
    select_status: str | None = None,
    user: User = Depends(require_premium),
    db: AsyncSession = Depends(get_db),
):
    """List projected ratings. Premium only."""
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


@router.get("/game-predictions", response_model=list[GamePredictionOut])
async def list_game_predictions(
    simulation_id: int | None = None,
    game_id: int | None = None,
    user: User = Depends(require_premium),
    db: AsyncSession = Depends(get_db),
):
    """List game predictions. Premium only."""
    query = select(GamePrediction)
    if simulation_id:
        query = query.where(GamePrediction.simulation_id == simulation_id)
    if game_id:
        query = query.where(GamePrediction.game_id == game_id)
    result = await db.execute(query)
    return result.scalars().all()
