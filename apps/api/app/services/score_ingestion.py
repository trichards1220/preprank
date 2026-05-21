"""LHSAA score ingestion service.

Scrapes game results from LHSAA website and inserts into database.
"""
from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session

from app.models import Game, Team, School, Sport
from app.services.name_matcher import find_best_match


def get_school_name_map(db: Session) -> dict[str, int]:
    """Build a name->id map for all schools."""
    schools = db.query(School).all()
    return {s.name: s.id for s in schools}


def get_team_id(db: Session, school_id: int, sport_id: int, season_year: int) -> int | None:
    """Look up team_id for a school/sport/season."""
    team = db.query(Team).filter(
        Team.school_id == school_id,
        Team.sport_id == sport_id,
        Team.season_year == season_year,
    ).first()
    return team.id if team else None


def find_or_create_game(
    db: Session,
    home_team_id: int,
    away_team_id: int,
    sport_id: int,
    season_year: int,
    game_date: date,
    week_number: int | None = None,
    home_score: int | None = None,
    away_score: int | None = None,
    status: str = "final",
    source: str = "lhsaa",
    is_district: bool = False,
    is_playoff: bool = False,
) -> Game:
    """Find existing game or create new. Updates score if game already exists."""
    existing = db.query(Game).filter(
        Game.home_team_id == home_team_id,
        Game.away_team_id == away_team_id,
        Game.game_date == game_date,
    ).first()

    if existing:
        existing.home_score = home_score
        existing.away_score = away_score
        existing.status = status
        if week_number is not None:
            existing.week_number = week_number
        return existing

    # Also check reverse (away at home might be listed differently)
    existing_rev = db.query(Game).filter(
        Game.home_team_id == away_team_id,
        Game.away_team_id == home_team_id,
        Game.game_date == game_date,
    ).first()

    if existing_rev:
        existing_rev.home_score = away_score
        existing_rev.away_score = home_score
        existing_rev.status = status
        if week_number is not None:
            existing_rev.week_number = week_number
        return existing_rev

    game = Game(
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        sport_id=sport_id,
        season_year=season_year,
        game_date=game_date,
        week_number=week_number,
        home_score=home_score,
        away_score=away_score,
        status=status,
        source=source,
        is_district=is_district,
        is_playoff=is_playoff,
    )
    db.add(game)
    return game


def parse_lhsaa_scores(html: str) -> list[dict]:
    """Parse LHSAA score page HTML into structured game data.

    Returns list of dicts with keys:
        home_team, away_team, home_score, away_score, game_date, sport

    This is a best-effort parser -- LHSAA's HTML structure may vary.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    games = []

    # Look for common score table patterns
    # LHSAA typically uses tables or divs with score data
    for row in soup.select("table tr, .game-row, .score-row"):
        cells = row.find_all(["td", "span", "div"])
        text_cells = [c.get_text(strip=True) for c in cells if c.get_text(strip=True)]

        if len(text_cells) < 4:
            continue

        # Try to extract: team1, score1, team2, score2
        # Pattern varies by page -- this handles the most common layouts
        try:
            game_data = _extract_game_from_cells(text_cells)
            if game_data:
                games.append(game_data)
        except (ValueError, IndexError):
            continue

    return games


def _extract_game_from_cells(cells: list[str]) -> dict | None:
    """Try to extract game data from a row of text cells."""
    # Look for cells that are purely numeric (scores)
    score_indices = [i for i, c in enumerate(cells) if c.isdigit()]

    if len(score_indices) < 2:
        return None

    # Assume: text before first score is home team, text before second score is away team
    first_score_idx = score_indices[0]
    second_score_idx = score_indices[1]

    if first_score_idx == 0:
        return None  # No team name before score

    home_team = " ".join(cells[:first_score_idx]).strip()
    home_score = int(cells[first_score_idx])

    away_start = first_score_idx + 1
    away_team = " ".join(cells[away_start:second_score_idx]).strip()
    away_score = int(cells[second_score_idx])

    if not home_team or not away_team:
        return None

    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_score": home_score,
        "away_score": away_score,
    }


def ingest_scores(
    db: Session,
    games_data: list[dict],
    sport_name: str,
    season_year: int,
    week_number: int | None = None,
    source: str = "lhsaa",
) -> dict:
    """Ingest a list of parsed game data into the database.

    Returns summary: {"inserted": N, "updated": N, "skipped": N, "errors": [...]}
    """
    sport = db.query(Sport).filter(Sport.name == sport_name).first()
    if not sport:
        return {"inserted": 0, "updated": 0, "skipped": 0, "errors": [f"Sport '{sport_name}' not found"]}

    school_map = get_school_name_map(db)
    summary: dict = {"inserted": 0, "updated": 0, "skipped": 0, "errors": []}

    for gd in games_data:
        home_school_id = find_best_match(gd["home_team"], school_map)
        away_school_id = find_best_match(gd["away_team"], school_map)

        if home_school_id is None:
            summary["errors"].append(f"No match for home team: {gd['home_team']}")
            summary["skipped"] += 1
            continue
        if away_school_id is None:
            summary["errors"].append(f"No match for away team: {gd['away_team']}")
            summary["skipped"] += 1
            continue

        home_team_id = get_team_id(db, home_school_id, sport.id, season_year)
        away_team_id = get_team_id(db, away_school_id, sport.id, season_year)

        if not home_team_id or not away_team_id:
            summary["skipped"] += 1
            continue

        game_date = gd.get("game_date", date.today())
        if isinstance(game_date, str):
            game_date = date.fromisoformat(game_date)

        # Check if this is an update or insert
        existing = db.query(Game).filter(
            ((Game.home_team_id == home_team_id) & (Game.away_team_id == away_team_id))
            | ((Game.home_team_id == away_team_id) & (Game.away_team_id == home_team_id)),
            Game.game_date == game_date,
        ).first()

        find_or_create_game(
            db, home_team_id, away_team_id, sport.id, season_year,
            game_date, week_number, gd.get("home_score"), gd.get("away_score"),
            status="final", source=source,
        )

        if existing:
            summary["updated"] += 1
        else:
            summary["inserted"] += 1

    db.commit()
    return summary
