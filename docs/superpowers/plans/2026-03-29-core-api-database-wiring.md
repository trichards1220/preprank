# Core API + Database Wiring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire FastAPI to PostgreSQL via SQLAlchemy, implement real CRUD endpoints for schools/teams/games/ratings with filtering and pagination, and serve seed data through the API.

**Architecture:** SQLAlchemy 2.0 async-style ORM models map 1:1 to the existing Alembic schema. Pydantic v2 schemas handle serialization. A `get_db` dependency provides request-scoped sessions. Each router gets real query logic with optional filters (division, classification, sport, season_year). The Next.js frontend gets a minimal API client to fetch and display rankings.

**Tech Stack:** SQLAlchemy 2.0 (sync), Pydantic v2 response schemas, FastAPI dependency injection, pytest + httpx for testing, Next.js fetch for frontend.

**Existing files to understand:**
- `apps/api/app/main.py` — FastAPI app with 4 routers already mounted at `/api/v1/*`
- `apps/api/app/config.py` — `Settings` with `DATABASE_URL`
- `apps/api/app/routers/{schools,teams,games,ratings}.py` — stub endpoints returning placeholder messages
- `apps/api/alembic/versions/a5a94be6e8d8_initial_schema.py` — full schema (14 tables)
- `apps/api/pyproject.toml` — already has sqlalchemy, psycopg2-binary, fastapi, pydantic

---

### Task 1: Database Session Factory

**Files:**
- Create: `apps/api/app/database.py`
- Test: `apps/api/tests/test_database.py`

- [ ] **Step 1: Create `apps/api/tests/__init__.py`**

```python
```

(Empty file to make tests a package.)

- [ ] **Step 2: Write failing test for database engine creation**

Create `apps/api/tests/test_database.py`:

```python
from sqlalchemy import text

from app.database import engine, SessionLocal


def test_engine_is_configured():
    assert engine is not None
    assert "preprank" in str(engine.url)


def test_session_factory_returns_session():
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        session.close()
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_database.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.database'`

- [ ] **Step 4: Implement database.py**

Create `apps/api/app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_database.py -v`
Expected: PASS (requires local PostgreSQL running via `docker compose up -d` from repo root)

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/database.py apps/api/tests/
git commit -m "feat(api): add SQLAlchemy database session factory"
```

---

### Task 2: SQLAlchemy ORM Models

**Files:**
- Create: `apps/api/app/models.py`
- Test: `apps/api/tests/test_models.py`

- [ ] **Step 1: Write failing test for model imports and table names**

Create `apps/api/tests/test_models.py`:

```python
from app.models import Sport, School, Team, Game, PowerRating


def test_sport_table_name():
    assert Sport.__tablename__ == "sports"


def test_school_table_name():
    assert School.__tablename__ == "schools"


def test_team_table_name():
    assert Team.__tablename__ == "teams"


def test_game_table_name():
    assert Game.__tablename__ == "games"


def test_power_rating_table_name():
    assert PowerRating.__tablename__ == "power_ratings"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.models'`

- [ ] **Step 3: Implement models.py**

Create `apps/api/app/models.py`:

```python
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, Numeric,
    ForeignKey, DateTime, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Sport(Base):
    __tablename__ = "sports"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    season = Column(String(20), nullable=False)
    has_power_rating = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    teams = relationship("Team", back_populates="sport")


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    city = Column(String(100))
    parish = Column(String(100))
    classification = Column(String(10))
    division = Column(String(10))
    select_status = Column(String(20))
    enrollment = Column(Integer)
    lhsaa_member_id = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    teams = relationship("Team", back_populates="school")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    sport_id = Column(Integer, ForeignKey("sports.id"))
    season_year = Column(Integer, nullable=False)
    head_coach = Column(String(200))
    division = Column(String(10))
    select_status = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

    school = relationship("School", back_populates="teams")
    sport = relationship("Sport", back_populates="teams")
    power_ratings = relationship("PowerRating", back_populates="team")
    home_games = relationship("Game", foreign_keys="Game.home_team_id", back_populates="home_team")
    away_games = relationship("Game", foreign_keys="Game.away_team_id", back_populates="away_team")

    __table_args__ = (UniqueConstraint("school_id", "sport_id", "season_year"),)


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    sport_id = Column(Integer, ForeignKey("sports.id"))
    season_year = Column(Integer, nullable=False)
    game_date = Column(Date)
    week_number = Column(Integer)
    home_score = Column(Integer)
    away_score = Column(Integer)
    status = Column(String(20), default="scheduled")
    is_district = Column(Boolean, default=False)
    is_playoff = Column(Boolean, default=False)
    is_championship = Column(Boolean, default=False)
    is_out_of_state = Column(Boolean, default=False)
    source = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_games")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_games")


class PowerRating(Base):
    __tablename__ = "power_ratings"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    week_number = Column(Integer, nullable=False)
    season_year = Column(Integer, nullable=False)
    power_rating = Column(Numeric(6, 2), nullable=False)
    strength_factor = Column(Numeric(6, 2))
    rank_in_division = Column(Integer)
    total_teams_in_division = Column(Integer)
    calculated_at = Column(DateTime, server_default=func.now())

    team = relationship("Team", back_populates="power_ratings")

    __table_args__ = (UniqueConstraint("team_id", "week_number", "season_year"),)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/models.py apps/api/tests/test_models.py
git commit -m "feat(api): add SQLAlchemy ORM models for core tables"
```

---

### Task 3: Pydantic Response Schemas

**Files:**
- Create: `apps/api/app/schemas/__init__.py`
- Create: `apps/api/app/schemas/schools.py`
- Create: `apps/api/app/schemas/teams.py`
- Create: `apps/api/app/schemas/games.py`
- Create: `apps/api/app/schemas/ratings.py`
- Test: `apps/api/tests/test_schemas.py`

- [ ] **Step 1: Write failing test for schema validation**

Create `apps/api/tests/test_schemas.py`:

```python
from app.schemas.schools import SchoolOut
from app.schemas.teams import TeamOut
from app.schemas.ratings import PowerRatingOut, RankedTeamOut


def test_school_out_schema():
    s = SchoolOut(
        id=1, name="Ruston", city=None, parish=None,
        classification="5A", division="I", select_status="Non-Select",
        enrollment=None
    )
    assert s.name == "Ruston"
    assert s.classification == "5A"


def test_team_out_schema():
    t = TeamOut(
        id=1, school_id=1, sport_id=1, season_year=2025,
        head_coach=None, division="I", select_status="Non-Select",
        school_name="Ruston", sport_name="Football"
    )
    assert t.school_name == "Ruston"


def test_power_rating_out_schema():
    r = PowerRatingOut(
        id=1, team_id=1, week_number=11, season_year=2025,
        power_rating=14.40, strength_factor=11.40,
        rank_in_division=1, total_teams_in_division=64
    )
    assert float(r.power_rating) == 14.40


def test_ranked_team_out_schema():
    rt = RankedTeamOut(
        rank=1, school_name="Ruston", division="I",
        classification="5A", select_status="Non-Select",
        power_rating=14.40, strength_factor=11.40,
        team_id=1, school_id=1
    )
    assert rt.rank == 1
    assert rt.school_name == "Ruston"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_schemas.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.schemas'`

- [ ] **Step 3: Create schemas/__init__.py**

Create `apps/api/app/schemas/__init__.py`:

```python
```

- [ ] **Step 4: Create schools schema**

Create `apps/api/app/schemas/schools.py`:

```python
from pydantic import BaseModel


class SchoolOut(BaseModel):
    id: int
    name: str
    city: str | None = None
    parish: str | None = None
    classification: str | None = None
    division: str | None = None
    select_status: str | None = None
    enrollment: int | None = None

    model_config = {"from_attributes": True}
```

- [ ] **Step 5: Create teams schema**

Create `apps/api/app/schemas/teams.py`:

```python
from pydantic import BaseModel


class TeamOut(BaseModel):
    id: int
    school_id: int
    sport_id: int
    season_year: int
    head_coach: str | None = None
    division: str | None = None
    select_status: str | None = None
    school_name: str
    sport_name: str

    model_config = {"from_attributes": True}
```

- [ ] **Step 6: Create games schema**

Create `apps/api/app/schemas/games.py`:

```python
from datetime import date

from pydantic import BaseModel


class GameOut(BaseModel):
    id: int
    home_team_id: int
    away_team_id: int
    sport_id: int
    season_year: int
    game_date: date | None = None
    week_number: int | None = None
    home_score: int | None = None
    away_score: int | None = None
    status: str
    is_district: bool
    is_playoff: bool
    is_championship: bool
    is_out_of_state: bool
    home_team_name: str | None = None
    away_team_name: str | None = None

    model_config = {"from_attributes": True}
```

- [ ] **Step 7: Create ratings schema**

Create `apps/api/app/schemas/ratings.py`:

```python
from pydantic import BaseModel


class PowerRatingOut(BaseModel):
    id: int
    team_id: int
    week_number: int
    season_year: int
    power_rating: float
    strength_factor: float | None = None
    rank_in_division: int | None = None
    total_teams_in_division: int | None = None

    model_config = {"from_attributes": True}


class RankedTeamOut(BaseModel):
    rank: int
    school_name: str
    division: str
    classification: str
    select_status: str
    power_rating: float
    strength_factor: float | None = None
    team_id: int
    school_id: int

    model_config = {"from_attributes": True}
```

- [ ] **Step 8: Run test to verify it passes**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_schemas.py -v`
Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add apps/api/app/schemas/ apps/api/tests/test_schemas.py
git commit -m "feat(api): add Pydantic response schemas for schools, teams, games, ratings"
```

---

### Task 4: Schools Router — Real CRUD

**Files:**
- Modify: `apps/api/app/routers/schools.py`
- Test: `apps/api/tests/test_routers_schools.py`

- [ ] **Step 1: Write failing test for schools endpoints**

Create `apps/api/tests/test_routers_schools.py`:

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_schools_returns_200():
    response = client.get("/api/v1/schools/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_schools_filter_by_division():
    response = client.get("/api/v1/schools/?division=I")
    assert response.status_code == 200
    data = response.json()
    for school in data:
        assert school["division"] == "I"


def test_list_schools_filter_by_classification():
    response = client.get("/api/v1/schools/?classification=5A")
    assert response.status_code == 200
    data = response.json()
    for school in data:
        assert school["classification"] == "5A"


def test_get_school_by_id():
    # First get a valid ID from the list
    list_resp = client.get("/api/v1/schools/?limit=1")
    schools = list_resp.json()
    if len(schools) == 0:
        return  # No seed data, skip
    school_id = schools[0]["id"]

    response = client.get(f"/api/v1/schools/{school_id}")
    assert response.status_code == 200
    assert response.json()["id"] == school_id


def test_get_school_not_found():
    response = client.get("/api/v1/schools/999999")
    assert response.status_code == 404
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_routers_schools.py -v`
Expected: FAIL — response is `{"message": "..."}` not a list

- [ ] **Step 3: Implement schools router**

Replace `apps/api/app/routers/schools.py` with:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import School
from app.schemas.schools import SchoolOut

router = APIRouter()


@router.get("/", response_model=list[SchoolOut])
def list_schools(
    division: str | None = Query(None, description="Filter by division (I, II, III, IV, V)"),
    classification: str | None = Query(None, description="Filter by classification (5A, 4A, 3A, 2A, 1A)"),
    select_status: str | None = Query(None, description="Filter by Select or Non-Select"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(School)
    if division:
        query = query.filter(School.division == division)
    if classification:
        query = query.filter(School.classification == classification)
    if select_status:
        query = query.filter(School.select_status == select_status)
    return query.order_by(School.name).offset(offset).limit(limit).all()


@router.get("/{school_id}", response_model=SchoolOut)
def get_school(school_id: int, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_routers_schools.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/routers/schools.py apps/api/tests/test_routers_schools.py
git commit -m "feat(api): implement schools CRUD with division/classification filters"
```

---

### Task 5: Teams Router — Real CRUD

**Files:**
- Modify: `apps/api/app/routers/teams.py`
- Test: `apps/api/tests/test_routers_teams.py`

- [ ] **Step 1: Write failing test for teams endpoints**

Create `apps/api/tests/test_routers_teams.py`:

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_teams_returns_200():
    response = client.get("/api/v1/teams/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_teams_filter_by_sport():
    response = client.get("/api/v1/teams/?sport=Football")
    assert response.status_code == 200


def test_list_teams_filter_by_season_year():
    response = client.get("/api/v1/teams/?season_year=2025")
    assert response.status_code == 200
    for team in response.json():
        assert team["season_year"] == 2025


def test_list_teams_filter_by_division():
    response = client.get("/api/v1/teams/?division=I")
    assert response.status_code == 200
    for team in response.json():
        assert team["division"] == "I"


def test_get_team_not_found():
    response = client.get("/api/v1/teams/999999")
    assert response.status_code == 404
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_routers_teams.py -v`
Expected: FAIL

- [ ] **Step 3: Implement teams router**

Replace `apps/api/app/routers/teams.py` with:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Team, School, Sport
from app.schemas.teams import TeamOut

router = APIRouter()


@router.get("/", response_model=list[TeamOut])
def list_teams(
    sport: str | None = Query(None, description="Filter by sport name"),
    season_year: int | None = Query(None, description="Filter by season year"),
    division: str | None = Query(None, description="Filter by division"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Team).options(joinedload(Team.school), joinedload(Team.sport))
    if sport:
        query = query.join(Sport).filter(Sport.name == sport)
    if season_year:
        query = query.filter(Team.season_year == season_year)
    if division:
        query = query.filter(Team.division == division)
    teams = query.order_by(Team.id).offset(offset).limit(limit).all()
    return [
        TeamOut(
            id=t.id,
            school_id=t.school_id,
            sport_id=t.sport_id,
            season_year=t.season_year,
            head_coach=t.head_coach,
            division=t.division,
            select_status=t.select_status,
            school_name=t.school.name,
            sport_name=t.sport.name,
        )
        for t in teams
    ]


@router.get("/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = (
        db.query(Team)
        .options(joinedload(Team.school), joinedload(Team.sport))
        .filter(Team.id == team_id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamOut(
        id=team.id,
        school_id=team.school_id,
        sport_id=team.sport_id,
        season_year=team.season_year,
        head_coach=team.head_coach,
        division=team.division,
        select_status=team.select_status,
        school_name=team.school.name,
        sport_name=team.sport.name,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_routers_teams.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/routers/teams.py apps/api/tests/test_routers_teams.py
git commit -m "feat(api): implement teams CRUD with sport/season/division filters"
```

---

### Task 6: Ratings Router — Rankings Endpoint

**Files:**
- Modify: `apps/api/app/routers/ratings.py`
- Test: `apps/api/tests/test_routers_ratings.py`

This is the most important endpoint — it returns the ranked power ratings that the frontend displays.

- [ ] **Step 1: Write failing test for ratings endpoints**

Create `apps/api/tests/test_routers_ratings.py`:

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_rankings_returns_200():
    response = client.get("/api/v1/ratings/rankings?sport=Football&season_year=2025&week_number=11")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_rankings_filter_by_division():
    response = client.get("/api/v1/ratings/rankings?sport=Football&season_year=2025&week_number=11&division=I")
    assert response.status_code == 200
    for entry in response.json():
        assert entry["division"] == "I"


def test_list_rankings_ordered_by_rank():
    response = client.get("/api/v1/ratings/rankings?sport=Football&season_year=2025&week_number=11&division=I")
    data = response.json()
    if len(data) >= 2:
        for i in range(len(data) - 1):
            assert data[i]["rank"] <= data[i + 1]["rank"]


def test_get_team_ratings_history():
    # Get a team_id from rankings first
    resp = client.get("/api/v1/ratings/rankings?sport=Football&season_year=2025&week_number=11&limit=1")
    data = resp.json()
    if len(data) == 0:
        return  # No seed data
    team_id = data[0]["team_id"]

    response = client.get(f"/api/v1/ratings/{team_id}?season_year=2025")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_team_ratings_not_found():
    response = client.get("/api/v1/ratings/999999?season_year=2025")
    assert response.status_code == 200
    assert response.json() == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_routers_ratings.py -v`
Expected: FAIL

- [ ] **Step 3: Implement ratings router**

Replace `apps/api/app/routers/ratings.py` with:

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import PowerRating, Team, School, Sport
from app.schemas.ratings import PowerRatingOut, RankedTeamOut

router = APIRouter()


@router.get("/rankings", response_model=list[RankedTeamOut])
def list_rankings(
    sport: str = Query(..., description="Sport name (e.g. Football)"),
    season_year: int = Query(..., description="Season year"),
    week_number: int = Query(..., description="Week number"),
    division: str | None = Query(None, description="Filter by division"),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = (
        db.query(PowerRating, Team, School)
        .join(Team, PowerRating.team_id == Team.id)
        .join(School, Team.school_id == School.id)
        .join(Sport, Team.sport_id == Sport.id)
        .filter(
            Sport.name == sport,
            PowerRating.season_year == season_year,
            PowerRating.week_number == week_number,
        )
    )
    if division:
        query = query.filter(Team.division == division)
    query = query.order_by(PowerRating.rank_in_division.asc())
    results = query.offset(offset).limit(limit).all()
    return [
        RankedTeamOut(
            rank=pr.rank_in_division,
            school_name=school.name,
            division=team.division,
            classification=school.classification,
            select_status=school.select_status or "",
            power_rating=float(pr.power_rating),
            strength_factor=float(pr.strength_factor) if pr.strength_factor else None,
            team_id=team.id,
            school_id=school.id,
        )
        for pr, team, school in results
    ]


@router.get("/{team_id}", response_model=list[PowerRatingOut])
def get_team_ratings(
    team_id: int,
    season_year: int = Query(..., description="Season year"),
    db: Session = Depends(get_db),
):
    ratings = (
        db.query(PowerRating)
        .filter(PowerRating.team_id == team_id, PowerRating.season_year == season_year)
        .order_by(PowerRating.week_number.asc())
        .all()
    )
    return ratings
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_routers_ratings.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/routers/ratings.py apps/api/tests/test_routers_ratings.py
git commit -m "feat(api): implement rankings endpoint with division filter and team history"
```

---

### Task 7: Games Router — Real CRUD

**Files:**
- Modify: `apps/api/app/routers/games.py`
- Test: `apps/api/tests/test_routers_games.py`

- [ ] **Step 1: Write failing test for games endpoints**

Create `apps/api/tests/test_routers_games.py`:

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_games_returns_200():
    response = client.get("/api/v1/games/?season_year=2025&sport=Football")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_games_filter_by_week():
    response = client.get("/api/v1/games/?season_year=2025&sport=Football&week_number=1")
    assert response.status_code == 200


def test_list_games_filter_by_status():
    response = client.get("/api/v1/games/?season_year=2025&sport=Football&status=final")
    assert response.status_code == 200


def test_get_game_not_found():
    response = client.get("/api/v1/games/999999")
    assert response.status_code == 404
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_routers_games.py -v`
Expected: FAIL

- [ ] **Step 3: Implement games router**

Replace `apps/api/app/routers/games.py` with:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Game, Team, School, Sport
from app.schemas.games import GameOut

router = APIRouter()


@router.get("/", response_model=list[GameOut])
def list_games(
    season_year: int = Query(..., description="Season year"),
    sport: str = Query(..., description="Sport name"),
    week_number: int | None = Query(None, description="Filter by week"),
    status: str | None = Query(None, description="Filter by status"),
    team_id: int | None = Query(None, description="Filter by team (home or away)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Game)
        .join(Sport, Game.sport_id == Sport.id)
        .options(
            joinedload(Game.home_team).joinedload(Team.school),
            joinedload(Game.away_team).joinedload(Team.school),
        )
        .filter(Game.season_year == season_year, Sport.name == sport)
    )
    if week_number is not None:
        query = query.filter(Game.week_number == week_number)
    if status:
        query = query.filter(Game.status == status)
    if team_id is not None:
        query = query.filter(
            (Game.home_team_id == team_id) | (Game.away_team_id == team_id)
        )
    games = query.order_by(Game.game_date.asc(), Game.id.asc()).offset(offset).limit(limit).all()
    return [
        GameOut(
            id=g.id,
            home_team_id=g.home_team_id,
            away_team_id=g.away_team_id,
            sport_id=g.sport_id,
            season_year=g.season_year,
            game_date=g.game_date,
            week_number=g.week_number,
            home_score=g.home_score,
            away_score=g.away_score,
            status=g.status,
            is_district=g.is_district,
            is_playoff=g.is_playoff,
            is_championship=g.is_championship,
            is_out_of_state=g.is_out_of_state,
            home_team_name=g.home_team.school.name if g.home_team else None,
            away_team_name=g.away_team.school.name if g.away_team else None,
        )
        for g in games
    ]


@router.get("/{game_id}", response_model=GameOut)
def get_game(game_id: int, db: Session = Depends(get_db)):
    game = (
        db.query(Game)
        .options(
            joinedload(Game.home_team).joinedload(Team.school),
            joinedload(Game.away_team).joinedload(Team.school),
        )
        .filter(Game.id == game_id)
        .first()
    )
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return GameOut(
        id=game.id,
        home_team_id=game.home_team_id,
        away_team_id=game.away_team_id,
        sport_id=game.sport_id,
        season_year=game.season_year,
        game_date=game.game_date,
        week_number=game.week_number,
        home_score=game.home_score,
        away_score=game.away_score,
        status=game.status,
        is_district=game.is_district,
        is_playoff=game.is_playoff,
        is_championship=game.is_championship,
        is_out_of_state=game.is_out_of_state,
        home_team_name=game.home_team.school.name if game.home_team else None,
        away_team_name=game.away_team.school.name if game.away_team else None,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_routers_games.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/routers/games.py apps/api/tests/test_routers_games.py
git commit -m "feat(api): implement games CRUD with week/status/team filters"
```

---

### Task 8: Frontend API Client + Rankings Page

**Files:**
- Create: `apps/web/src/lib/api.ts`
- Create: `apps/web/src/app/rankings/page.tsx`
- Modify: `apps/web/src/app/page.tsx`

- [ ] **Step 1: Create API client**

Create `apps/web/src/lib/api.ts`:

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface RankedTeam {
  rank: number;
  school_name: string;
  division: string;
  classification: string;
  select_status: string;
  power_rating: number;
  strength_factor: number | null;
  team_id: number;
  school_id: number;
}

export interface School {
  id: number;
  name: string;
  city: string | null;
  parish: string | null;
  classification: string | null;
  division: string | null;
  select_status: string | null;
  enrollment: number | null;
}

export async function fetchRankings(
  sport: string,
  seasonYear: number,
  weekNumber: number,
  division?: string,
): Promise<RankedTeam[]> {
  const params = new URLSearchParams({
    sport,
    season_year: String(seasonYear),
    week_number: String(weekNumber),
  });
  if (division) params.set("division", division);
  const res = await fetch(`${API_BASE}/api/v1/ratings/rankings?${params}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchSchools(division?: string): Promise<School[]> {
  const params = new URLSearchParams();
  if (division) params.set("division", division);
  const res = await fetch(`${API_BASE}/api/v1/schools/?${params}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
```

- [ ] **Step 2: Create `.env.local` for web**

Create `apps/web/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

- [ ] **Step 3: Create the rankings page**

Create `apps/web/src/app/rankings/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { fetchRankings, RankedTeam } from "@/lib/api";

const DIVISIONS = [
  { value: "", label: "All Divisions" },
  { value: "I", label: "Division I (5A)" },
  { value: "II", label: "Division II (4A)" },
  { value: "III", label: "Division III (3A)" },
  { value: "IV", label: "Division IV (2A)" },
  { value: "V", label: "Division V (1A)" },
];

export default function RankingsPage() {
  const [rankings, setRankings] = useState<RankedTeam[]>([]);
  const [division, setDivision] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchRankings("Football", 2025, 11, division || undefined)
      .then(setRankings)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [division]);

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <h1
        className="mb-6 text-4xl font-bold tracking-tight"
        style={{ fontFamily: "var(--font-display)" }}
      >
        <span className="text-white">POWER</span>
        <span className="text-crimson"> RANKINGS</span>
      </h1>

      <div className="mb-6 flex items-center gap-4">
        <select
          value={division}
          onChange={(e) => setDivision(e.target.value)}
          className="rounded border border-steel-gray bg-charcoal px-3 py-2 text-white focus:border-crimson focus:outline-none"
        >
          {DIVISIONS.map((d) => (
            <option key={d.value} value={d.value}>
              {d.label}
            </option>
          ))}
        </select>
        <span className="text-steel-gray text-sm">
          2025 Football &middot; Week 11 (Final)
        </span>
      </div>

      {loading && <p className="text-steel-gray">Loading rankings...</p>}
      {error && <p className="text-crimson">Error: {error}</p>}

      {!loading && !error && (
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-steel-gray text-sm uppercase tracking-wide text-steel-gray">
                <th className="px-3 py-3 w-16">Rank</th>
                <th className="px-3 py-3">School</th>
                <th className="px-3 py-3 w-20">Div</th>
                <th className="px-3 py-3 w-24">Class</th>
                <th className="px-3 py-3 w-20 text-right">Rating</th>
                <th className="px-3 py-3 w-20 text-right">SoS</th>
              </tr>
            </thead>
            <tbody>
              {rankings.map((r) => (
                <tr
                  key={r.team_id}
                  className="border-b border-charcoal hover:bg-charcoal/50 transition-colors"
                >
                  <td className="px-3 py-3 font-bold text-crimson">{r.rank}</td>
                  <td className="px-3 py-3 font-semibold">{r.school_name}</td>
                  <td className="px-3 py-3 text-steel-gray">{r.division}</td>
                  <td className="px-3 py-3 text-steel-gray">{r.classification}</td>
                  <td className="px-3 py-3 text-right font-mono">
                    {r.power_rating.toFixed(2)}
                  </td>
                  <td className="px-3 py-3 text-right font-mono text-steel-gray">
                    {r.strength_factor?.toFixed(2) ?? "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {rankings.length === 0 && (
            <p className="mt-4 text-center text-steel-gray">No rankings found.</p>
          )}
        </div>
      )}
    </main>
  );
}
```

- [ ] **Step 4: Update home page to link to rankings**

Replace `apps/web/src/app/page.tsx` with:

```tsx
import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8">
      <h1
        className="text-6xl font-bold tracking-tight"
        style={{ fontFamily: "var(--font-display)" }}
      >
        <span className="text-white">PREP</span>
        <span className="text-crimson">/</span>
        <span className="text-white">RANK</span>
      </h1>
      <p className="text-steel-gray text-lg">
        LHSAA Power Rankings & Predictions
      </p>
      <Link
        href="/rankings"
        className="rounded bg-crimson px-6 py-3 font-semibold text-white transition-colors hover:bg-crimson/80"
        style={{ fontFamily: "var(--font-display)" }}
      >
        VIEW RANKINGS
      </Link>
    </main>
  );
}
```

- [ ] **Step 5: Verify the web app builds**

Run: `cd apps/web && npm run build`
Expected: Build succeeds with no errors

- [ ] **Step 6: Commit**

```bash
git add apps/web/src/lib/api.ts apps/web/src/app/rankings/ apps/web/src/app/page.tsx apps/web/.env.local
git commit -m "feat(web): add rankings page with division filter and API client"
```

---

### Task 9: Full Integration Smoke Test

**Files:**
- Create: `apps/api/tests/test_integration.py`

- [ ] **Step 1: Write integration test that exercises the full pipeline**

Create `apps/api/tests/test_integration.py`:

```python
"""
Integration smoke test — verifies seed data flows through the API correctly.
Requires: PostgreSQL running with seed data loaded.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_schools_have_seed_data():
    resp = client.get("/api/v1/schools/?limit=5")
    assert resp.status_code == 200
    schools = resp.json()
    assert len(schools) > 0
    assert "name" in schools[0]
    assert "classification" in schools[0]


def test_rankings_return_ordered_results():
    resp = client.get("/api/v1/ratings/rankings?sport=Football&season_year=2025&week_number=11&division=I")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    # Verify Ruston is #1 in Division I
    assert data[0]["school_name"] == "Ruston"
    assert data[0]["rank"] == 1
    assert float(data[0]["power_rating"]) == 14.40


def test_division_filter_excludes_other_divisions():
    resp = client.get("/api/v1/ratings/rankings?sport=Football&season_year=2025&week_number=11&division=II")
    data = resp.json()
    for entry in data:
        assert entry["division"] == "II"
        assert entry["classification"] == "4A"


def test_teams_joined_with_school_and_sport():
    resp = client.get("/api/v1/teams/?sport=Football&season_year=2025&division=I&limit=3")
    assert resp.status_code == 200
    teams = resp.json()
    if len(teams) > 0:
        assert teams[0]["sport_name"] == "Football"
        assert teams[0]["school_name"] is not None
```

- [ ] **Step 2: Run full test suite**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 3: Commit**

```bash
git add apps/api/tests/test_integration.py
git commit -m "test(api): add integration smoke tests for seed data pipeline"
```

---

## Summary

| Task | What it builds | Key files |
|------|---------------|-----------|
| 1 | DB session factory | `app/database.py` |
| 2 | ORM models (5 core tables) | `app/models.py` |
| 3 | Pydantic response schemas | `app/schemas/*.py` |
| 4 | Schools CRUD + filters | `app/routers/schools.py` |
| 5 | Teams CRUD + filters | `app/routers/teams.py` |
| 6 | Rankings endpoint + team history | `app/routers/ratings.py` |
| 7 | Games CRUD + filters | `app/routers/games.py` |
| 8 | Frontend API client + rankings UI | `src/lib/api.ts`, `src/app/rankings/page.tsx` |
| 9 | Integration smoke tests | `tests/test_integration.py` |

**After all 9 tasks:** `docker compose up -d` → `alembic upgrade head` → `python seed.py` → `uvicorn` → `npm run dev` → visit `localhost:3000/rankings` → see 298 ranked Louisiana high school football teams.
