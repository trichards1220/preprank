"""Simulation endpoints: run simulations, get results, game impact analysis."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth.premium import require_premium, get_premium_or_preview
from app.models import (
    Simulation, ProjectedRating, GamePrediction, GameImpactAnalysis,
    Team, School, Sport, Game,
)
from app.schemas.simulations import (
    SimulationRunRequest, SimulationOut,
    ProjectedRatingOut, GameImpactOut,
)
from engine.types import (
    TeamRecord, GameResult, GameStatus as EngineGameStatus,
    ScheduledGame, SimulationConfig,
)
from engine.power_rating import calculate_all_ratings
from engine.monte_carlo import run_simulation
from engine.win_probability import win_probability

DIVISION_TO_CLASSIFICATION = {"I": "5A", "II": "4A", "III": "3A", "IV": "2A", "V": "1A"}

router = APIRouter()


def _load_teams(db: Session, sport_name: str, season_year: int) -> dict[int, TeamRecord]:
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


def _load_played_games(db: Session, sport_name: str, season_year: int, up_to_week: int) -> list[GameResult]:
    rows = (
        db.query(Game)
        .join(Sport, Game.sport_id == Sport.id)
        .filter(
            Sport.name == sport_name,
            Game.season_year == season_year,
            Game.status.in_(["final", "forfeit"]),
            Game.week_number <= up_to_week,
        )
        .all()
    )
    return [
        GameResult(
            game_id=g.id, home_team_id=g.home_team_id, away_team_id=g.away_team_id,
            home_score=g.home_score, away_score=g.away_score,
            status=EngineGameStatus(g.status),
            is_forfeit=(g.status == "forfeit"),
            week_number=g.week_number,
        )
        for g in rows
    ]


def _load_remaining_games(db: Session, sport_name: str, season_year: int, after_week: int) -> list[ScheduledGame]:
    rows = (
        db.query(Game)
        .join(Sport, Game.sport_id == Sport.id)
        .filter(
            Sport.name == sport_name,
            Game.season_year == season_year,
            Game.status == "scheduled",
            Game.week_number > after_week,
        )
        .all()
    )
    return [
        ScheduledGame(game_id=g.id, home_team_id=g.home_team_id, away_team_id=g.away_team_id, week_number=g.week_number)
        for g in rows
    ]


def _run_and_store(sim_id: int, teams, played, remaining, config, db_url: str):
    """Run simulation and store results. Called as background task."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    eng = create_engine(db_url)
    Session = sessionmaker(bind=eng)
    db = Session()
    try:
        db.query(Simulation).filter(Simulation.id == sim_id).update({
            "status": "running", "started_at": datetime.now(timezone.utc),
        })
        db.commit()

        projections = run_simulation(teams, played, remaining, config)

        for tid, proj in projections.items():
            db.add(ProjectedRating(
                simulation_id=sim_id, team_id=tid,
                projected_rating_mean=proj.projected_rating_mean,
                projected_rating_median=proj.projected_rating_median,
                projected_rating_p10=proj.projected_rating_p10,
                projected_rating_p90=proj.projected_rating_p90,
                projected_rank_mean=proj.projected_rank_mean,
                playoff_probability=proj.playoff_probability,
                championship_probability=proj.championship_probability,
                projected_wins_mean=proj.projected_wins_mean,
                projected_losses_mean=proj.projected_losses_mean,
            ))

        db.query(Simulation).filter(Simulation.id == sim_id).update({
            "status": "completed", "completed_at": datetime.now(timezone.utc),
        })
        db.commit()
    except Exception:
        db.query(Simulation).filter(Simulation.id == sim_id).update({"status": "failed"})
        db.commit()
        raise
    finally:
        db.close()


@router.post("/run", response_model=SimulationOut)
def run_sim(
    req: SimulationRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    sport = db.query(Sport).filter(Sport.name == req.sport).first()
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport '{req.sport}' not found")

    sim = Simulation(
        sport_id=sport.id, season_year=req.season_year,
        week_number=req.week_number, run_count=req.num_runs, status="pending",
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)

    teams = _load_teams(db, req.sport, req.season_year)
    played = _load_played_games(db, req.sport, req.season_year, req.week_number)
    remaining = _load_remaining_games(db, req.sport, req.season_year, req.week_number)
    config = SimulationConfig(
        sport_name=req.sport, season_year=req.season_year,
        week_number=req.week_number, num_runs=req.num_runs,
        playoff_spots=req.playoff_spots,
    )

    from app.config import settings
    background_tasks.add_task(_run_and_store, sim.id, teams, played, remaining, config, settings.DATABASE_URL)

    return sim


@router.get("/{sim_id}/results", response_model=list[ProjectedRatingOut])
def get_simulation_results(
    sim_id: int,
    division: str | None = Query(None),
    premium_info: dict = Depends(get_premium_or_preview),
    db: Session = Depends(get_db),
):
    sim = db.query(Simulation).filter(Simulation.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    query = (
        db.query(ProjectedRating, Team, School)
        .join(Team, ProjectedRating.team_id == Team.id)
        .join(School, Team.school_id == School.id)
        .filter(ProjectedRating.simulation_id == sim_id)
    )
    if division:
        query = query.filter(Team.division == division)
    query = query.order_by(ProjectedRating.projected_rank_mean.asc())
    rows = query.all()

    results_list = [
        ProjectedRatingOut(
            team_id=pr.team_id,
            school_name=school.name,
            division=team.division,
            projected_rating_mean=float(pr.projected_rating_mean),
            projected_rating_median=float(pr.projected_rating_median),
            projected_rating_p10=float(pr.projected_rating_p10),
            projected_rating_p90=float(pr.projected_rating_p90),
            projected_rank_mean=float(pr.projected_rank_mean),
            playoff_probability=float(pr.playoff_probability),
            championship_probability=float(pr.championship_probability),
            projected_wins_mean=float(pr.projected_wins_mean),
            projected_losses_mean=float(pr.projected_losses_mean),
        )
        for pr, team, school in rows
    ]

    # Free users get a preview (first 3 teams only)
    if not premium_info["is_premium"]:
        return results_list[:3]
    return results_list


@router.get("/{sim_id}", response_model=SimulationOut)
def get_simulation(sim_id: int, db: Session = Depends(get_db)):
    sim = db.query(Simulation).filter(Simulation.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim


@router.get("/game/{game_id}/impact", response_model=list[GameImpactOut])
def get_game_impact(
    game_id: int,
    _: User = Depends(require_premium),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(GameImpactAnalysis, Team, School)
        .join(Team, GameImpactAnalysis.affected_team_id == Team.id)
        .join(School, Team.school_id == School.id)
        .filter(GameImpactAnalysis.game_id == game_id)
        .order_by(GameImpactAnalysis.simulation_id.desc())
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="No impact analysis found for this game")
    latest_sim = rows[0][0].simulation_id
    return [
        GameImpactOut(
            affected_team_id=gia.affected_team_id,
            school_name=school.name,
            rating_if_home_wins=float(gia.rating_if_home_wins),
            rating_if_away_wins=float(gia.rating_if_away_wins),
            rank_if_home_wins=gia.rank_if_home_wins,
            rank_if_away_wins=gia.rank_if_away_wins,
            playoff_prob_if_home_wins=float(gia.playoff_prob_if_home_wins),
            playoff_prob_if_away_wins=float(gia.playoff_prob_if_away_wins),
        )
        for gia, team, school in rows if gia.simulation_id == latest_sim
    ]


@router.get("/team/{team_id}/projections", response_model=ProjectedRatingOut | None)
def get_team_projections(
    team_id: int,
    premium_info: dict = Depends(get_premium_or_preview),
    db: Session = Depends(get_db),
):
    row = (
        db.query(ProjectedRating, Team, School)
        .join(Team, ProjectedRating.team_id == Team.id)
        .join(School, Team.school_id == School.id)
        .filter(ProjectedRating.team_id == team_id)
        .order_by(ProjectedRating.simulation_id.desc())
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="No projections found for this team")
    pr, team, school = row
    return ProjectedRatingOut(
        team_id=pr.team_id,
        school_name=school.name,
        division=team.division,
        projected_rating_mean=float(pr.projected_rating_mean),
        projected_rating_median=float(pr.projected_rating_median),
        projected_rating_p10=float(pr.projected_rating_p10),
        projected_rating_p90=float(pr.projected_rating_p90),
        projected_rank_mean=float(pr.projected_rank_mean),
        playoff_probability=float(pr.playoff_probability),
        championship_probability=float(pr.championship_probability),
        projected_wins_mean=float(pr.projected_wins_mean),
        projected_losses_mean=float(pr.projected_losses_mean),
    )
