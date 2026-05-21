# Supabase Cloud Database Setup

## 1. Create Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Name: `preprank`
4. Database Password: generate a strong password and save it
5. Region: `us-east-1` (closest to Louisiana)
6. Click "Create new project"

## 2. Get Connection Details

Go to **Project Settings → Database**:

- **Host**: `db.<project-ref>.supabase.co`
- **Port**: `5432` (direct) or `6543` (connection pooler — use this for production)
- **Database**: `postgres`
- **User**: `postgres`
- **Password**: your database password

### Connection String Formats

Direct connection (for migrations):
```
postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres
```

Pooled connection (for API — use this in production):
```
postgresql://postgres.<project-ref>:<password>@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

## 3. Environment Variables

Copy these from your Supabase dashboard (**Settings → API**):

```env
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=eyJ...  (public anon key)
SUPABASE_SERVICE_ROLE_KEY=eyJ...  (service role key — keep secret)
DATABASE_URL=postgresql://postgres.<project-ref>:<password>@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

## 4. Run Migrations

Use the **direct connection** (port 5432) for migrations:

```bash
cd apps/api
DATABASE_URL="postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres" \
  .venv/Scripts/alembic upgrade head
```

Or use the deploy script:
```bash
DATABASE_URL="postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres" \
  python scripts/deploy_db.py
```

## 5. Seed Data

```bash
DATABASE_URL="postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres" \
  python supabase/seed/seed.py --csv 2025_football_power_ratings_final.csv
```

## 6. Verify

```bash
DATABASE_URL="..." python -c "
import psycopg2
conn = psycopg2.connect('YOUR_DATABASE_URL')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM schools')
print(f'Schools: {cur.fetchone()[0]}')
cur.execute('SELECT COUNT(*) FROM teams')
print(f'Teams: {cur.fetchone()[0]}')
cur.execute('SELECT COUNT(*) FROM power_ratings')
print(f'Power ratings: {cur.fetchone()[0]}')
conn.close()
"
```

Expected: 298 schools, 298 teams, 298+ power ratings.

## Notes

- Supabase free tier: 500MB storage, 2 GB bandwidth, 50K monthly active users
- Connection pooler (port 6543) is required for serverless deployments
- Direct connection (port 5432) works for migrations and one-off scripts
- SSL is enabled by default on Supabase
