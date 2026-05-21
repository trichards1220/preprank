from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Team, School, Sport
from app.schemas.teams import TeamOut

router = APIRouter()


@router.get("/", response_model=list[TeamOut])
def list_teams(
    sport: str | None = Query(None, description="Filter by sport name"),
    season_year: int | None = Query(None, description="Filter by season year"),
    division: str | None = Query(None, description="Filter by division"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Team).options(joinedload(Team.school), joinedload(Team.sport))
    if sport:
        query = query.join(Sport).filter(Sport.name == sport)
    if season_year:
        query = query.filter(Team.season_year == season_year)
    if division:
        query = query.filter(Team.division == division)
    teams = query.order_by(Team.id).offset(offset).limit(limit).all()
    return [
        TeamOut(
            id=t.id,
            school_id=t.school_id,
            sport_id=t.sport_id,
            season_year=t.season_year,
            head_coach=t.head_coach,
            division=t.division,
            select_status=t.select_status,
            school_name=t.school.name,
            sport_name=t.sport.name,
        )
        for t in teams
    ]


@router.get("/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = (
        db.query(Team)
        .options(joinedload(Team.school), joinedload(Team.sport))
        .filter(Team.id == team_id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamOut(
        id=team.id,
        school_id=team.school_id,
        sport_id=team.sport_id,
        season_year=team.season_year,
        head_coach=team.head_coach,
        division=team.division,
        select_status=team.select_status,
        school_name=team.school.name,
        sport_name=team.sport.name,
    )
