#!/usr/bin/env python3
"""Deploy database: run migrations + seed data. Idempotent and safe to run multiple times.

Usage:
    DATABASE_URL="postgresql://..." python scripts/deploy_db.py
"""
import os
import sys
import subprocess

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable required")
    sys.exit(1)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(REPO_ROOT, "apps", "api")
SEED_SCRIPT = os.path.join(REPO_ROOT, "supabase", "seed", "seed.py")
CSV_PATH = os.path.join(REPO_ROOT, "2025_football_power_ratings_final.csv")

# Also check parent directory for CSV (when running from monorepo root)
if not os.path.exists(CSV_PATH):
    CSV_PATH = os.path.join(os.path.dirname(REPO_ROOT), "2025_football_power_ratings_final.csv")


def run_migrations():
    print("=== Running Alembic migrations ===")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=API_DIR,
        env={**os.environ, "DATABASE_URL": DATABASE_URL},
    )
    if result.returncode != 0:
        print("ERROR: Migrations failed")
        sys.exit(1)
    print("Migrations complete.\n")


def run_seed():
    print("=== Running seed script ===")
    if not os.path.exists(CSV_PATH):
        print(f"WARNING: CSV not found at {CSV_PATH}, skipping seed")
        return
    result = subprocess.run(
        [sys.executable, SEED_SCRIPT, "--csv", CSV_PATH],
        env={**os.environ, "DATABASE_URL": DATABASE_URL},
    )
    if result.returncode != 0:
        print("ERROR: Seed script failed")
        sys.exit(1)
    print("Seed complete.\n")


def verify():
    print("=== Verifying database ===")
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check tables exist
    cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")
    table_count = cur.fetchone()[0]
    print(f"  Tables: {table_count}")

    # Check seed data
    checks = [
        ("sports", 23),
        ("schools", 298),
        ("teams", 298),
        ("power_ratings", 298),
    ]
    all_ok = True
    for table, expected_min in checks:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        status = "OK" if count >= expected_min else "WARN"
        if count < expected_min:
            all_ok = False
        print(f"  {table}: {count} (expected >= {expected_min}) [{status}]")

    # Sample query
    cur.execute("SELECT name, power_rating FROM power_ratings pr JOIN teams t ON pr.team_id = t.id JOIN schools s ON t.school_id = s.id ORDER BY pr.power_rating DESC LIMIT 3")
    print("\n  Top 3 by power rating:")
    for name, rating in cur.fetchall():
        print(f"    {name}: {float(rating):.2f}")

    conn.close()
    print(f"\nVerification {'PASSED' if all_ok else 'NEEDS ATTENTION'}")


if __name__ == "__main__":
    run_migrations()
    run_seed()
    verify()
    print("\n=== Deploy complete ===")
