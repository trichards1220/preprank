import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session
from app.models.games import Game
from app.models.predictions import GameImpactAnalysis
from app.models.users import User
from app.auth import require_premium
from app.schemas.schemas import GameBase, GameOut, GameImpactOut, GameResultConfirm

logger = logging.getLogger("preprank.games")

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/", response_model=list[GameOut])
async def list_games(
    sport_id: int | None = None,
    season_year: int | None = None,
    week_number: int | None = None,
    team_id: int | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Game)
    if sport_id:
        query = query.where(Game.sport_id == sport_id)
    if season_year:
        query = query.where(Game.season_year == season_year)
    if week_number:
        query = query.where(Game.week_number == week_number)
    if team_id:
        query = query.where((Game.home_team_id == team_id) | (Game.away_team_id == team_id))
    if status:
        query = query.where(Game.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=GameOut, status_code=201)
async def create_game(game: GameBase, db: AsyncSession = Depends(get_db)):
    db_game = Game(**game.model_dump())
    db.add(db_game)
    await db.commit()
    await db.refresh(db_game)
    return db_game


@router.get("/{game_id}", response_model=GameOut)
async def get_game(game_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.post("/{game_id}/confirm-result", response_model=GameOut)
async def confirm_game_result(
    game_id: int,
    body: GameResultConfirm,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Confirm a game result and trigger the notification cascade.

    Sets the game status to 'final', records the score, and kicks off
    a background task that:
    1. Walks the opponent network to find all affected teams
    2. Sends score_update notifications to followers of the two teams
    3. Sends ranking_change notifications to followers of all teams
       whose power ratings are affected by the result change
    """
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.status == "final":
        raise HTTPException(status_code=409, detail="Game result already confirmed")

    game.home_score = body.home_score
    game.away_score = body.away_score
    game.status = "final"
    await db.commit()
    await db.refresh(game)

    # Trigger notification cascade in background
    # Use a fresh session since background tasks outlive the request
    game_id_for_bg = game.id
    background_tasks.add_task(_notification_cascade_bg, game_id_for_bg)

    logger.info(f"Game {game_id} confirmed: {game.home_score}-{game.away_score}, cascade queued")
    return game


async def _notification_cascade_bg(game_id: int):
    """Background task that runs the notification cascade with its own DB session."""
    from app.services.notifications import process_game_result

    async with async_session() as db:
        result = await db.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()
        if game:
            await process_game_result(game, db)


@router.get("/{game_id}/impact-analysis", response_model=list[GameImpactOut])
async def get_game_impact_analysis(
    game_id: int,
    simulation_id: int | None = None,
    user: User = Depends(require_premium),
    db: AsyncSession = Depends(get_db),
):
    """Get impact analysis for a game — how each outcome affects team ratings. Premium only."""
    result = await db.execute(select(Game).where(Game.id == game_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Game not found")

    query = select(GameImpactAnalysis).where(GameImpactAnalysis.game_id == game_id)
    if simulation_id:
        query = query.where(GameImpactAnalysis.simulation_id == simulation_id)
    result = await db.execute(query)
    return result.scalars().all()
