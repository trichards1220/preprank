from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.games import Game
from app.models.predictions import GameImpactAnalysis
from app.models.users import User
from app.auth import require_premium
from app.schemas.schemas import GameBase, GameOut, GameImpactOut

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


@router.get("/{game_id}/impact-analysis", response_model=list[GameImpactOut])
async def get_game_impact_analysis(
    game_id: int,
    simulation_id: int | None = None,
    user: User = Depends(require_premium),
    db: AsyncSession = Depends(get_db),
):
    """Get impact analysis for a game — how each outcome affects team ratings. Premium only.

    Shows for each affected team: projected rating if home wins vs away wins,
    projected rank in each scenario, and playoff probability in each scenario.
    """
    result = await db.execute(select(Game).where(Game.id == game_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Game not found")

    query = select(GameImpactAnalysis).where(GameImpactAnalysis.game_id == game_id)
    if simulation_id:
        query = query.where(GameImpactAnalysis.simulation_id == simulation_id)
    result = await db.execute(query)
    return result.scalars().all()
