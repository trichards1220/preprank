from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Game, Team, School, Sport
from app.schemas.games import GameOut
from app.schemas.games_write import GameCreateRequest, GameUpdateRequest

router = APIRouter()


@router.get("/", response_model=list[GameOut])
def list_games(
    season_year: int = Query(..., description="Season year"),
    sport: str = Query(..., description="Sport name"),
    week_number: int | None = Query(None, description="Filter by week"),
    status: str | None = Query(None, description="Filter by status"),
    team_id: int | None = Query(None, description="Filter by team (home or away)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Game)
        .join(Sport, Game.sport_id == Sport.id)
        .options(
            joinedload(Game.home_team).joinedload(Team.school),
            joinedload(Game.away_team).joinedload(Team.school),
        )
        .filter(Game.season_year == season_year, Sport.name == sport)
    )
    if week_number is not None:
        query = query.filter(Game.week_number == week_number)
    if status:
        query = query.filter(Game.status == status)
    if team_id is not None:
        query = query.filter(
            (Game.home_team_id == team_id) | (Game.away_team_id == team_id)
        )
    games = query.order_by(Game.game_date.asc(), Game.id.asc()).offset(offset).limit(limit).all()
    return [
        GameOut(
            id=g.id,
            home_team_id=g.home_team_id,
            away_team_id=g.away_team_id,
            sport_id=g.sport_id,
            season_year=g.season_year,
            game_date=g.game_date,
            week_number=g.week_number,
            home_score=g.home_score,
            away_score=g.away_score,
            status=g.status,
            is_district=g.is_district,
            is_playoff=g.is_playoff,
            is_championship=g.is_championship,
            is_out_of_state=g.is_out_of_state,
            home_team_name=g.home_team.school.name if g.home_team else None,
            away_team_name=g.away_team.school.name if g.away_team else None,
        )
        for g in games
    ]


@router.get("/{game_id}", response_model=GameOut)
def get_game(game_id: int, db: Session = Depends(get_db)):
    game = (
        db.query(Game)
        .options(
            joinedload(Game.home_team).joinedload(Team.school),
            joinedload(Game.away_team).joinedload(Team.school),
        )
        .filter(Game.id == game_id)
        .first()
    )
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return GameOut(
        id=game.id,
        home_team_id=game.home_team_id,
        away_team_id=game.away_team_id,
        sport_id=game.sport_id,
        season_year=game.season_year,
        game_date=game.game_date,
        week_number=game.week_number,
        home_score=game.home_score,
        away_score=game.away_score,
        status=game.status,
        is_district=game.is_district,
        is_playoff=game.is_playoff,
        is_championship=game.is_championship,
        is_out_of_state=game.is_out_of_state,
        home_team_name=game.home_team.school.name if game.home_team else None,
        away_team_name=game.away_team.school.name if game.away_team else None,
    )


@router.post("/", response_model=GameOut, status_code=201)
def create_game(req: GameCreateRequest, db: Session = Depends(get_db)):
    """Create a new game. Use for manual score entry."""
    # Validate teams exist
    home_team = db.query(Team).filter(Team.id == req.home_team_id).first()
    if not home_team:
        raise HTTPException(status_code=404, detail=f"Home team {req.home_team_id} not found")
    away_team = db.query(Team).filter(Team.id == req.away_team_id).first()
    if not away_team:
        raise HTTPException(status_code=404, detail=f"Away team {req.away_team_id} not found")

    game = Game(
        home_team_id=req.home_team_id,
        away_team_id=req.away_team_id,
        sport_id=req.sport_id,
        season_year=req.season_year,
        game_date=req.game_date,
        week_number=req.week_number,
        home_score=req.home_score,
        away_score=req.away_score,
        status=req.status,
        is_district=req.is_district,
        is_playoff=req.is_playoff,
        is_championship=req.is_championship,
        source=req.source,
    )
    db.add(game)
    db.commit()
    db.refresh(game)

    # Eager load relationships for response
    game = (
        db.query(Game)
        .options(
            joinedload(Game.home_team).joinedload(Team.school),
            joinedload(Game.away_team).joinedload(Team.school),
        )
        .filter(Game.id == game.id)
        .first()
    )
    return GameOut(
        id=game.id,
        home_team_id=game.home_team_id,
        away_team_id=game.away_team_id,
        sport_id=game.sport_id,
        season_year=game.season_year,
        game_date=game.game_date,
        week_number=game.week_number,
        home_score=game.home_score,
        away_score=game.away_score,
        status=game.status,
        is_district=game.is_district,
        is_playoff=game.is_playoff,
        is_championship=game.is_championship,
        is_out_of_state=game.is_out_of_state,
        home_team_name=game.home_team.school.name if game.home_team else None,
        away_team_name=game.away_team.school.name if game.away_team else None,
    )


@router.patch("/{game_id}", response_model=GameOut)
def update_game(game_id: int, req: GameUpdateRequest, db: Session = Depends(get_db)):
    """Update a game's score or status."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if req.home_score is not None:
        game.home_score = req.home_score
    if req.away_score is not None:
        game.away_score = req.away_score
    if req.status is not None:
        game.status = req.status
    if req.week_number is not None:
        game.week_number = req.week_number

    db.commit()

    game = (
        db.query(Game)
        .options(
            joinedload(Game.home_team).joinedload(Team.school),
            joinedload(Game.away_team).joinedload(Team.school),
        )
        .filter(Game.id == game_id)
        .first()
    )
    return GameOut(
        id=game.id,
        home_team_id=game.home_team_id,
        away_team_id=game.away_team_id,
        sport_id=game.sport_id,
        season_year=game.season_year,
        game_date=game.game_date,
        week_number=game.week_number,
        home_score=game.home_score,
        away_score=game.away_score,
        status=game.status,
        is_district=game.is_district,
        is_playoff=game.is_playoff,
        is_championship=game.is_championship,
        is_out_of_state=game.is_out_of_state,
        home_team_name=game.home_team.school.name if game.home_team else None,
        away_team_name=game.away_team.school.name if game.away_team else None,
    )
