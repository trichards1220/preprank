# PREP/RANK

LHSAA high school sports power rankings, Monte Carlo simulations, and playoff predictions.

## Structure

```
preprank/
├── apps/
│   ├── api/          # Python 3.12 + FastAPI backend
│   ├── web/          # Next.js 14 (App Router) + Tailwind CSS
│   └── mobile/       # Expo React Native (future)
├── packages/
│   ├── shared/       # Shared types, constants, validation schemas
│   └── engine/       # Power rating calculation + Monte Carlo engine
├── supabase/         # Migrations and seed data
└── docs/
```

## Local Development

```bash
# Start PostgreSQL
docker compose up -d

# API (Python)
cd apps/api
python -m venv .venv
source .venv/Scripts/activate  # Windows
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Web (Next.js)
npm install
npm run dev:web
```
