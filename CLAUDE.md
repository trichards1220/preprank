# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

PrepRank — LHSAA high school sports power rankings with Monte Carlo playoff predictions. Subscription web + mobile product. A two-language monorepo: TypeScript (Next.js web) and Python (FastAPI API + simulation engine).

## Monorepo layout & the npm/Python split

This is the single most important thing to understand before running anything: **npm workspaces only cover `apps/web` and `packages/shared`.** The two Python projects are installed and run separately — they are NOT npm workspaces.

- `apps/web` — Next.js 14 App Router + Tailwind (npm workspace `@preprank/web`)
- `packages/shared` — shared TS types/constants (npm workspace)
- `apps/api` — FastAPI backend; install with `pip install -e ".[dev]"` from `apps/api`
- `packages/engine` — `preprank-engine`, the power-rating + Monte Carlo core (NumPy/SciPy); installed/tested independently
- `apps/mobile` — Expo React Native (early; uses mock data)
- `supabase/`, `scripts/`, `data/`, `docs/`

## Commands

Web / workspace (run from repo root):
- `npm install` — install web + shared
- `npm run dev:web` — Next.js dev on **port 3001**
- `npm run build:web` — production build (this is what Vercel runs: `cd apps/web && npm run build`)
- `npm run lint` — ESLint (next lint) on the web app

API (from `apps/api`, in its own venv):
- `pip install -e ".[dev]"`
- `npm run dev:api` from root **or** `uvicorn app.main:app --reload --port 8001`
- `pytest` — full API suite; single test: `pytest tests/test_routers_teams.py::test_name`
- `ruff check .` — lint

Engine (from `packages/engine`, own venv):
- `pip install -e ".[dev]"` then `pytest`

Database (local):
- `docker compose up -d` — local Postgres on 5432
- Alembic migrations live in `apps/api/alembic/` (`alembic upgrade head`)

## Port reality (a known footgun)

The dev ports are inconsistent across files — align them or local dev silently fails to connect:
- API dev script (`dev:api`) runs uvicorn on **8001**; the README example says 8000.
- The web client (`apps/web/src/lib/api.ts`) defaults its base URL to **`http://localhost:8002`**.

Set `NEXT_PUBLIC_API_URL` in `apps/web` to the port you actually run the API on (or change `dev:api`). Don't assume the defaults match.

## API architecture

- Entry: `apps/api/app/main.py`. Every router is mounted under **`/api/v1/*`** (schools, teams, games, ratings, simulations, auth, subscriptions, favorites, pickem, share, hype, scenarios). Health at `/health`. CORS origins come from `settings.CORS_ORIGINS`.
- DB layer (`app/database.py`): **synchronous** SQLAlchemy + psycopg2, `pool_pre_ping`, and `connect_args={"sslmode":"require"}` auto-added when `DATABASE_URL` contains "supabase". Do not reintroduce async/asyncpg (see archive caveat below).
- Auth: app-issued JWTs (python-jose + bcrypt pinned `<4.1.0` for passlib), 15-min access / 7-day refresh. Premium gating in `app/auth/premium.py`.
- The API consumes `packages/engine` for ratings/simulation math — keep simulation logic in the engine, not the routers.

## The web→API contract

`apps/web/src/lib/api.ts` is the single source of the frontend's API contract; `auth.tsx` handles login/register/me. Both expect `/api/v1/...` paths. If you change a route prefix in the API, update `api.ts` — they must match exactly.

## Deployment

- **Web:** Vercel project `preprank-web`, git-connected to this repo, **auto-deploys on push to `master`** (production branch is `master`, not `main`). Build = `cd apps/web && npm run build`.
- **API:** intended for a container host. `railway.json`, `fly.toml`, and `Dockerfile.api` all exist; the live API host is currently undecided/down — confirm before assuming an endpoint.

## Archive-branch caveat (avoid editing the wrong API)

The `archive/pre-consolidation` branch holds a **divergent, retired** API implementation: it uses a `/power-ratings` contract (no `/api/v1`), an async `asyncpg` engine, and a `models/` package instead of `app/models.py`. The canonical API on `master` is the `/api/v1` sync-SQLAlchemy one. If you encounter `power_ratings` routers or `create_async_engine`, you are looking at the old code — do not port its patterns forward.
