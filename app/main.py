from fastapi import FastAPI

from app.routers import schools, teams, games, power_ratings, predictions

app = FastAPI(
    title="PrepRank",
    description="Louisiana high school sports power ranking prediction engine",
    version="0.1.0",
)

app.include_router(schools.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")
app.include_router(games.router, prefix="/api/v1")
app.include_router(power_ratings.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
