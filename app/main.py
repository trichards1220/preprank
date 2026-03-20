from fastapi import FastAPI

from app.routers import sports, schools, teams, games, power_ratings, predictions, auth, users, webhooks, pickem, hype, badges_router

app = FastAPI(
    title="PrepRank",
    description="Louisiana high school sports power ranking prediction engine",
    version="0.2.0",
)

# Public endpoints
app.include_router(sports.router, prefix="/api/v1")
app.include_router(schools.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")
app.include_router(games.router, prefix="/api/v1")
app.include_router(power_ratings.router, prefix="/api/v1")

# Premium-gated prediction endpoints
app.include_router(predictions.router, prefix="/api/v1")

# Social engagement endpoints
app.include_router(pickem.router, prefix="/api/v1")
app.include_router(hype.router, prefix="/api/v1")
app.include_router(badges_router.router, prefix="/api/v1")

# Auth & user endpoints
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")

# Stripe webhooks (no /api/v1 prefix — Stripe calls these directly)
app.include_router(webhooks.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
