"""What-If Scenario Builder endpoints. Premium only."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Team, School, Sport, Game, User
from app.auth.premium import require_premium
from app.schemas.scenarios import (
    ScenarioRequest, ScenarioTeamRequest, CompareRequest,
    ScenarioResult, CompareResult,
)
from engine.types import (
    TeamRecord, GameResult, GameStatus as EngineGameStatus,
    ScheduledGame, SimulationConfig,
)
from engine.scenario import calculate_scenario, calculate_best_case, calculate_worst_case

DIVISION_TO_CLASSIFICATION = {"I": "5A", "II": "4A", "III": "3A", "IV": "2A", "V": "1A"}

router = APIRouter()


def _load_teams(db, sport_name, season_year):
    rows = (
        db.query(Team, School)
        .join(School, Team.school_id == School.id)
        .join(Sport, Team.sport_id == Sport.id)
        .filter(Sport.name == sport_name, Team.season_year == season_year)
        .all()
    )
    teams = {}
    for team, school in rows:
        cls = school.classification or DIVISION_TO_CLASSIFICATION.get(team.division, "5A")
        teams[team.id] = TeamRecord(
            team_id=team.id, school_name=school.name,
            division=team.division, classification=cls,
        )
    return teams


def _load_played(db, sport_name, season_year, week_number):
    sport = db.query(Sport).filter(Sport.name == sport_name).first()
    if not sport:
        return []
    rows = db.query(Game).filter(
        Game.sport_id == sport.id, Game.season_year == season_year,
        Game.status.in_(["final", "forfeit"]), Game.week_number <= week_number,
    ).all()
    return [
        GameResult(
            game_id=g.id, home_team_id=g.home_team_id, away_team_id=g.away_team_id,
            home_score=g.home_score, away_score=g.away_score,
            status=EngineGameStatus(g.status), week_number=g.week_number,
        )
        for g in rows
    ]


def _load_remaining(db, sport_name, season_year, week_number):
    sport = db.query(Sport).filter(Sport.name == sport_name).first()
    if not sport:
        return []
    rows = db.query(Game).filter(
        Game.sport_id == sport.id, Game.season_year == season_year,
        Game.status == "scheduled", Game.week_number > week_number,
    ).all()
    return [
        ScheduledGame(game_id=g.id, home_team_id=g.home_team_id,
                      away_team_id=g.away_team_id, week_number=g.week_number)
        for g in rows
    ]


def _to_result(proj, teams, locked_count=0, remaining_count=0) -> ScenarioResult:
    team = teams.get(proj.team_id)
    return ScenarioResult(
        team_id=proj.team_id,
        school_name=team.school_name if team else None,
        projected_rating=proj.projected_rating_mean,
        projected_rank=proj.projected_rank_mean,
        playoff_probability=proj.playoff_probability,
        championship_probability=proj.championship_probability,
        projected_wins=proj.projected_wins_mean,
        projected_losses=proj.projected_losses_mean,
        locked_count=locked_count,
        remaining_count=remaining_count,
    )


@router.post("/calculate", response_model=ScenarioResult)
def calculate(
    req: ScenarioRequest,
    _: User = Depends(require_premium),
    db: Session = Depends(get_db),
):
    teams = _load_teams(db, req.sport, req.season_year)
    if req.team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    played = _load_played(db, req.sport, req.season_year, req.week_number)
    remaining = _load_remaining(db, req.sport, req.season_year, req.week_number)
    config = SimulationConfig(
        sport_name=req.sport, season_year=req.season_year,
        week_number=req.week_number, num_runs=1000, playoff_spots=8,
    )
    locked = [{"game_id": lo.game_id, "winner_team_id": lo.winner_team_id} for lo in req.locked_outcomes]
    result = calculate_scenario(teams, played, remaining, locked, req.team_id, config)
    if not result["target"]:
        raise HTTPException(status_code=400, detail="Could not calculate scenario")
    return _to_result(result["target"], teams, result["locked_count"], result["remaining_count"])


@router.post("/best-case", response_model=ScenarioResult)
def best_case(
    req: ScenarioTeamRequest,
    _: User = Depends(require_premium),
    db: Session = Depends(get_db),
):
    teams = _load_teams(db, req.sport, req.season_year)
    if req.team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    played = _load_played(db, req.sport, req.season_year, req.week_number)
    remaining = _load_remaining(db, req.sport, req.season_year, req.week_number)
    config = SimulationConfig(
        sport_name=req.sport, season_year=req.season_year,
        week_number=req.week_number, num_runs=1000, playoff_spots=8,
    )
    result = calculate_best_case(teams, played, remaining, req.team_id, config)
    if not result["target"]:
        raise HTTPException(status_code=400, detail="Could not calculate")
    return _to_result(result["target"], teams, result.get("locked_count", 0), result.get("remaining_count", 0))


@router.post("/worst-case", response_model=ScenarioResult)
def worst_case(
    req: ScenarioTeamRequest,
    _: User = Depends(require_premium),
    db: Session = Depends(get_db),
):
    teams = _load_teams(db, req.sport, req.season_year)
    if req.team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    played = _load_played(db, req.sport, req.season_year, req.week_number)
    remaining = _load_remaining(db, req.sport, req.season_year, req.week_number)
    config = SimulationConfig(
        sport_name=req.sport, season_year=req.season_year,
        week_number=req.week_number, num_runs=1000, playoff_spots=8,
    )
    result = calculate_worst_case(teams, played, remaining, req.team_id, config)
    if not result["target"]:
        raise HTTPException(status_code=400, detail="Could not calculate")
    return _to_result(result["target"], teams, result.get("locked_count", 0), result.get("remaining_count", 0))


@router.post("/compare", response_model=CompareResult)
def compare(
    req: CompareRequest,
    _: User = Depends(require_premium),
    db: Session = Depends(get_db),
):
    teams = _load_teams(db, req.sport, req.season_year)
    if req.team_id not in teams:
        raise HTTPException(status_code=404, detail="Team not found")
    played = _load_played(db, req.sport, req.season_year, req.week_number)
    remaining = _load_remaining(db, req.sport, req.season_year, req.week_number)
    config = SimulationConfig(
        sport_name=req.sport, season_year=req.season_year,
        week_number=req.week_number, num_runs=1000, playoff_spots=8,
    )
    locked_a = [{"game_id": lo.game_id, "winner_team_id": lo.winner_team_id} for lo in req.scenario_a]
    locked_b = [{"game_id": lo.game_id, "winner_team_id": lo.winner_team_id} for lo in req.scenario_b]
    res_a = calculate_scenario(teams, played, remaining, locked_a, req.team_id, config, seed=42)
    res_b = calculate_scenario(teams, played, remaining, locked_b, req.team_id, config, seed=42)
    if not res_a["target"] or not res_b["target"]:
        raise HTTPException(status_code=400, detail="Could not calculate scenarios")
    sa = _to_result(res_a["target"], teams)
    sb = _to_result(res_b["target"], teams)
    team = teams.get(req.team_id)
    return CompareResult(
        team_id=req.team_id,
        school_name=team.school_name if team else None,
        scenario_a=sa, scenario_b=sb,
        rating_delta=round(sa.projected_rating - sb.projected_rating, 2),
        rank_delta=round(sa.projected_rank - sb.projected_rank, 1),
        playoff_delta=round(sa.playoff_probability - sb.playoff_probability, 2),
    )
