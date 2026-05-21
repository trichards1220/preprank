"""Pick'em contest, picks, leaderboard, and badge endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import (
    PickemContest, PickemEntry, PickemBadge,
    Game, Team, School, Sport,
)
from app.schemas.pickem import (
    ContestOut, ContestCreateRequest, PicksBatchRequest,
    EntryOut, LeaderboardEntry, SchoolLeaderboardEntry, BadgeOut,
)
from app.auth.dependencies import get_current_user
from app.services import pickem_service
from app.models import User

router = APIRouter()


def _game_count(db: Session, contest: PickemContest) -> int:
    return (
        db.query(Game)
        .filter(
            Game.sport_id == contest.sport_id,
            Game.season_year == contest.season_year,
            Game.week_number == contest.week_number,
        )
        .count()
    )


def _contest_out(db: Session, contest: PickemContest) -> ContestOut:
    return ContestOut(
        id=contest.id,
        sport_id=contest.sport_id,
        season_year=contest.season_year,
        week_number=contest.week_number,
        title=contest.title,
        status=contest.status,
        opens_at=contest.opens_at,
        locks_at=contest.locks_at,
        scored_at=contest.scored_at,
        game_count=_game_count(db, contest),
    )


def _entry_out(entry: PickemEntry) -> EntryOut:
    game = entry.game
    picked_team = entry.picked_team
    return EntryOut(
        id=entry.id,
        game_id=entry.game_id,
        picked_team_id=entry.picked_team_id,
        picked_team_name=(
            picked_team.school.name if picked_team and picked_team.school else None
        ),
        home_team_name=(
            game.home_team.school.name
            if game and game.home_team and game.home_team.school
            else None
        ),
        away_team_name=(
            game.away_team.school.name
            if game and game.away_team and game.away_team.school
            else None
        ),
        home_score=game.home_score if game else None,
        away_score=game.away_score if game else None,
        is_correct=entry.is_correct,
        points_earned=entry.points_earned or 0,
    )


# ── Contests ──────────────────────────────────────────────────────────

@router.get("/contests", response_model=list[ContestOut])
def list_contests(
    sport: str | None = Query(None),
    season_year: int | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(PickemContest)
    if sport:
        query = query.join(Sport, PickemContest.sport_id == Sport.id).filter(Sport.name == sport)
    if season_year is not None:
        query = query.filter(PickemContest.season_year == season_year)
    if status:
        query = query.filter(PickemContest.status == status)
    contests = query.order_by(PickemContest.season_year.desc(), PickemContest.week_number.desc()).all()
    return [_contest_out(db, c) for c in contests]


@router.post("/contests", response_model=ContestOut, status_code=201)
def create_contest(
    req: ContestCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        contest = pickem_service.create_contest(
            db,
            sport_name=req.sport,
            season_year=req.season_year,
            week_number=req.week_number,
            title=req.title,
            opens_at=req.opens_at,
            locks_at=req.locks_at,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _contest_out(db, contest)


@router.get("/contests/{contest_id}", response_model=ContestOut)
def get_contest(contest_id: int, db: Session = Depends(get_db)):
    contest = db.query(PickemContest).filter(PickemContest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    return _contest_out(db, contest)


# ── Games for a contest ──────────────────────────────────────────────

@router.get("/contests/{contest_id}/games")
def get_contest_games(contest_id: int, db: Session = Depends(get_db)):
    contest = db.query(PickemContest).filter(PickemContest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    games = pickem_service.get_contest_games(db, contest)
    result = []
    for g in games:
        home_name = g.home_team.school.name if g.home_team and g.home_team.school else None
        away_name = g.away_team.school.name if g.away_team and g.away_team.school else None
        result.append({
            "game_id": g.id,
            "home_team_id": g.home_team_id,
            "away_team_id": g.away_team_id,
            "home_team_name": home_name,
            "away_team_name": away_name,
            "game_date": str(g.game_date) if g.game_date else None,
            "status": g.status,
        })
    return result


# ── Picks ─────────────────────────────────────────────────────────────

@router.post("/contests/{contest_id}/picks", response_model=list[EntryOut])
def submit_picks(
    contest_id: int,
    req: PicksBatchRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    picks = [{"game_id": p.game_id, "picked_team_id": p.picked_team_id} for p in req.picks]
    try:
        entries = pickem_service.submit_picks(db, contest_id, user.id, picks)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    # Eager-load relationships for response
    entry_ids = [e.id for e in entries]
    loaded = (
        db.query(PickemEntry)
        .options(
            joinedload(PickemEntry.game).joinedload(Game.home_team).joinedload(Team.school),
            joinedload(PickemEntry.game).joinedload(Game.away_team).joinedload(Team.school),
            joinedload(PickemEntry.picked_team).joinedload(Team.school),
        )
        .filter(PickemEntry.id.in_(entry_ids))
        .all()
    )
    return [_entry_out(e) for e in loaded]


@router.get("/contests/{contest_id}/my-picks", response_model=list[EntryOut])
def get_my_picks(
    contest_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entries = (
        db.query(PickemEntry)
        .options(
            joinedload(PickemEntry.game).joinedload(Game.home_team).joinedload(Team.school),
            joinedload(PickemEntry.game).joinedload(Game.away_team).joinedload(Team.school),
            joinedload(PickemEntry.picked_team).joinedload(Team.school),
        )
        .filter(PickemEntry.contest_id == contest_id, PickemEntry.user_id == user.id)
        .all()
    )
    return [_entry_out(e) for e in entries]


# ── Scoring ───────────────────────────────────────────────────────────

@router.post("/contests/{contest_id}/score")
def score_contest(
    contest_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = pickem_service.score_contest(db, contest_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return result


# ── Leaderboards ──────────────────────────────────────────────────────

@router.get("/leaderboard/individual", response_model=list[LeaderboardEntry])
def individual_leaderboard(
    contest_id: int | None = Query(None),
    season_year: int | None = Query(None),
    db: Session = Depends(get_db),
):
    return pickem_service.get_individual_leaderboard(db, contest_id=contest_id, season_year=season_year)


@router.get("/leaderboard/schools", response_model=list[SchoolLeaderboardEntry])
def school_leaderboard(
    contest_id: int | None = Query(None),
    season_year: int | None = Query(None),
    db: Session = Depends(get_db),
):
    return pickem_service.get_school_leaderboard(db, contest_id=contest_id, season_year=season_year)


# ── Badges ────────────────────────────────────────────────────────────

@router.get("/badges", response_model=list[BadgeOut])
def get_my_badges(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    badges = (
        db.query(PickemBadge)
        .filter(PickemBadge.user_id == user.id)
        .order_by(PickemBadge.earned_at.desc())
        .all()
    )
    return badges
