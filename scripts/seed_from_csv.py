"""Seed the database from the 2025 football power ratings CSV.

Usage:
    python -m scripts.seed_from_csv

Loads:
1. All 23 LHSAA sports into the sports table
2. Schools from the CSV into the schools table
3. Football teams for 2025 into the teams table
4. Final power ratings (week 10) into the power_ratings table
"""

import asyncio
import csv
from collections import Counter
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, async_session, Base
from app.models.sports import Sport
from app.models.schools import School
from app.models.teams import Team
from app.models.power_ratings import PowerRating

CSV_PATH = Path(__file__).parent.parent / "data" / "seed" / "2025_football_power_ratings_final.csv"

LHSAA_SPORTS = [
    ("Football", "fall", True),
    ("Volleyball", "fall", True),
    ("Cross Country", "fall", False),
    ("Swimming", "fall", False),
    ("Boys Basketball", "winter", True),
    ("Girls Basketball", "winter", True),
    ("Wrestling", "winter", False),
    ("Bowling", "winter", False),
    ("Indoor Track and Field", "winter", False),
    ("Gymnastics", "winter", False),
    ("Baseball", "spring", True),
    ("Softball", "spring", True),
    ("Boys Soccer", "spring", True),
    ("Girls Soccer", "spring", True),
    ("Tennis", "spring", False),
    ("Golf", "spring", False),
    ("Outdoor Track and Field", "spring", False),
    ("Boys Golf", "spring", False),
    ("Girls Golf", "spring", False),
    ("Boys Tennis", "spring", False),
    ("Girls Tennis", "spring", False),
    ("Boys Swimming", "fall", False),
    ("Girls Swimming", "fall", False),
]


async def seed_sports(session: AsyncSession) -> int:
    """Seed sports table. Returns football sport_id."""
    football_id = None
    for name, season, has_pr in LHSAA_SPORTS:
        existing = await session.execute(select(Sport).where(Sport.name == name))
        if existing.scalar_one_or_none():
            continue
        sport = Sport(name=name, season=season, has_power_rating=has_pr)
        session.add(sport)

    await session.flush()

    result = await session.execute(select(Sport).where(Sport.name == "Football"))
    football = result.scalar_one()
    return football.id


async def seed_from_csv(session: AsyncSession, football_sport_id: int):
    """Load schools, teams, and power ratings from the CSV."""
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Count teams per bracket (division + select_status) for total_teams_in_division
    bracket_counts: Counter = Counter()
    for row in rows:
        key = (row["division"], row["select_status"])
        bracket_counts[key] += 1

    school_cache: dict[str, int] = {}

    for row in rows:
        school_name = row["school"].strip()
        division = row["division"].strip()
        select_status = row["select_status"].strip()
        season_year = int(row["season_year"])
        rank = int(row["rank"])
        wins = int(row["wins"])
        losses = int(row["losses"])
        power_rating = float(row["power_rating"])
        strength_factor = float(row["strength_factor"])
        bracket_key = (division, select_status)

        # Upsert school
        if school_name not in school_cache:
            result = await session.execute(select(School).where(School.name == school_name))
            existing_school = result.scalar_one_or_none()
            if existing_school:
                existing_school.division = division
                existing_school.select_status = select_status
                school_cache[school_name] = existing_school.id
            else:
                school = School(
                    name=school_name,
                    division=division,
                    select_status=select_status,
                )
                session.add(school)
                await session.flush()
                school_cache[school_name] = school.id

        school_id = school_cache[school_name]

        # Create team
        result = await session.execute(
            select(Team).where(
                Team.school_id == school_id,
                Team.sport_id == football_sport_id,
                Team.season_year == season_year,
            )
        )
        existing_team = result.scalar_one_or_none()
        if existing_team:
            team_id = existing_team.id
        else:
            team = Team(
                school_id=school_id,
                sport_id=football_sport_id,
                season_year=season_year,
                division=division,
                select_status=select_status,
            )
            session.add(team)
            await session.flush()
            team_id = team.id

        # Create power rating (week 10 = final)
        result = await session.execute(
            select(PowerRating).where(
                PowerRating.team_id == team_id,
                PowerRating.week_number == 10,
                PowerRating.season_year == season_year,
            )
        )
        if not result.scalar_one_or_none():
            pr = PowerRating(
                team_id=team_id,
                week_number=10,
                season_year=season_year,
                power_rating=power_rating,
                strength_factor=strength_factor,
                rank_in_division=rank,
                total_teams_in_division=bracket_counts[bracket_key],
            )
            session.add(pr)

    await session.commit()
    print(f"Seeded {len(school_cache)} schools, {len(rows)} teams/power ratings")


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        football_id = await seed_sports(session)
        await session.commit()
        await seed_from_csv(session, football_id)

    await engine.dispose()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
