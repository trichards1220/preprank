from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.power_ratings import PowerRating
from app.models.teams import Team
from app.models.schools import School
from app.models.sports import Sport
from app.routers import sports, schools, teams, games, power_ratings, predictions, auth, users, webhooks, pickem, hype, badges_router, subscriptions

app = FastAPI(
    title="PrepRank",
    description="Louisiana high school sports power ranking prediction engine",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://preprank-web.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sports.router, prefix="/api/v1")
app.include_router(schools.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")
app.include_router(games.router, prefix="/api/v1")
app.include_router(power_ratings.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(pickem.router, prefix="/api/v1")
app.include_router(hype.router, prefix="/api/v1")
app.include_router(badges_router.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(subscriptions.router, prefix="/api/v1")
app.include_router(webhooks.router)


@app.get("/api/v1/ratings/rankings")
async def rankings_alias(
    sport: str = Query(default="Football"),
    season_year: int = Query(default=2025),
    week_number: int = Query(default=10),
    division: str | None = None,
    select_status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(
        select(func.max(PowerRating.week_number))
        .join(Team, PowerRating.team_id == Team.id)
        .join(Sport, Team.sport_id == Sport.id)
        .where(Sport.name == sport)
        .where(PowerRating.season_year == season_year)
    )
    latest_week = check.scalar()
    if latest_week is None:
        return []
    if week_number > latest_week:
        week_number = latest_week

    query = (
        select(PowerRating, Team, School, Sport)
        .join(Team, PowerRating.team_id == Team.id)
        .join(School, Team.school_id == School.id)
        .join(Sport, Team.sport_id == Sport.id)
        .where(Sport.name == sport)
        .where(PowerRating.season_year == season_year)
        .where(PowerRating.week_number == week_number)
    )
    if division:
        query = query.where(Team.division == division)
    if select_status:
        query = query.where(Team.select_status == select_status)
    query = query.order_by(PowerRating.power_rating.desc())

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "rank": i + 1,
            "school_name": school.name,
            "school_id": school.id,
            "team_id": team.id,
            "division": team.division,
            "select_status": team.select_status,
            "power_rating": float(pr.power_rating),
            "strength_factor": float(pr.strength_factor),
            "rank_in_division": pr.rank_in_division,
            "total_teams_in_division": pr.total_teams_in_division,
            "week_number": pr.week_number,
            "season_year": pr.season_year,
        }
        for i, (pr, team, school, sport_obj) in enumerate(rows)
    ]

@app.get("/api/v1/ratings/{team_id}")
async def team_ratings(
    team_id: int,
    season_year: int = Query(default=2025),
    db: AsyncSession = Depends(get_db),
):
    """Get all power ratings for a specific team."""
    query = (
        select(PowerRating, Team, School, Sport)
        .join(Team, PowerRating.team_id == Team.id)
        .join(School, Team.school_id == School.id)
        .join(Sport, Team.sport_id == Sport.id)
        .where(PowerRating.team_id == team_id)
        .where(PowerRating.season_year == season_year)
        .order_by(PowerRating.week_number.desc())
    )
    result = await db.execute(query)
    rows = result.all()
    if not rows:
        return []
    return [
        {
            "team_id": team.id,
            "school_name": school.name,
            "school_id": school.id,
            "sport": sport_obj.name,
            "division": team.division,
            "select_status": team.select_status,
            "power_rating": float(pr.power_rating),
            "strength_factor": float(pr.strength_factor),
            "rank_in_division": pr.rank_in_division,
            "total_teams_in_division": pr.total_teams_in_division,
            "week_number": pr.week_number,
            "season_year": pr.season_year,
        }
        for pr, team, school, sport_obj in rows
    ]
@app.get("/health")
async def health():
    return {"status": "ok"}