# Pick'em & Student Engagement Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the weekly Pick'em prediction contest system with individual and school leaderboards, prediction accuracy badges, and team hype scores — the viral engine that drives student adoption and creates sponsorable inventory.

**Architecture:** Three new DB tables (`pickem_contests`, `pickem_entries`, `pickem_badges`) via Alembic migration. A contest lifecycle service manages weekly open→lock→score→leaderboard flow. Entries require no auth (anonymous play allowed to maximize adoption) but logged-in users get persistent leaderboards and badges. School leaderboards aggregate logged-in users by their favorited school. The hype score is a computed metric from power rating trajectory, stored on the existing `power_ratings` table. Frontend adds a Pick'em hub page, contest detail page, leaderboard page, and badge showcase.

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Pydantic v2, Next.js 14, Tailwind CSS

**Existing codebase to understand:**
- `apps/api/app/models.py` — Sport, School, Team, Game, PowerRating, User, UserFavorite, Simulation, etc.
- `apps/api/app/auth/dependencies.py` — `get_current_user` (required auth), `get_optional_user` (returns None if no token)
- `apps/api/app/main.py` — FastAPI app with 8 routers already mounted
- `apps/web/src/lib/auth.tsx` — AuthProvider with `useAuth()` hook (user, isPremium, getToken)
- `apps/web/src/lib/api.ts` — centralized `apiFetch` with auto-token attachment
- DB has: 298 schools, 298 football teams, 23 sports, games table (currently empty)

---

## File Structure

**API (new files):**
```
apps/api/
├── alembic/versions/XXXX_add_pickem_tables.py   # Migration
├── app/
│   ├── models.py                                  # Add PickemContest, PickemEntry, PickemBadge
│   ├── schemas/pickem.py                          # Pydantic schemas
│   ├── routers/pickem.py                          # Pick'em endpoints
│   └── services/pickem_service.py                 # Contest lifecycle, scoring, leaderboards
└── tests/test_pickem.py                           # Integration tests
```

**Frontend (new files):**
```
apps/web/src/
├── app/
│   ├── pickem/page.tsx                            # Pick'em hub (active contests)
│   ├── pickem/[contestId]/page.tsx                # Contest detail (make picks / view results)
│   └── pickem/leaderboard/page.tsx                # Leaderboards (individual + school)
├── components/
│   ├── PickemCard.tsx                             # Single game pick widget
│   ├── LeaderboardTable.tsx                       # Sortable leaderboard
│   └── BadgeDisplay.tsx                           # Badge collection display
└── lib/api.ts                                     # Add pick'em API functions
```

---

### Task 1: Database Migration — Pick'em Tables

**Files:**
- Create: `apps/api/alembic/versions/XXXX_add_pickem_tables.py`

- [ ] **Step 1: Create the migration**

Run: `cd apps/api && .venv/Scripts/alembic revision -m "add_pickem_tables"`

- [ ] **Step 2: Write the migration**

Edit the generated migration file:

```python
def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS pickem_contests (
            id SERIAL PRIMARY KEY,
            sport_id INTEGER REFERENCES sports(id),
            season_year INTEGER NOT NULL,
            week_number INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'open', 'locked', 'scored', 'closed')),
            opens_at TIMESTAMP,
            locks_at TIMESTAMP,
            scored_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(sport_id, season_year, week_number)
        );
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS pickem_entries (
            id SERIAL PRIMARY KEY,
            contest_id INTEGER REFERENCES pickem_contests(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            game_id INTEGER REFERENCES games(id),
            picked_team_id INTEGER REFERENCES teams(id),
            is_correct BOOLEAN,
            points_earned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(contest_id, user_id, game_id)
        );
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS pickem_badges (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            badge_type VARCHAR(50) NOT NULL,
            badge_name VARCHAR(200) NOT NULL,
            description VARCHAR(500),
            earned_at TIMESTAMP DEFAULT NOW(),
            contest_id INTEGER REFERENCES pickem_contests(id),
            metadata_json TEXT
        );
    """)

    op.execute("CREATE INDEX idx_pickem_entries_contest ON pickem_entries(contest_id);")
    op.execute("CREATE INDEX idx_pickem_entries_user ON pickem_entries(user_id);")
    op.execute("CREATE INDEX idx_pickem_entries_correct ON pickem_entries(contest_id, is_correct);")
    op.execute("CREATE INDEX idx_pickem_badges_user ON pickem_badges(user_id);")
    op.execute("CREATE INDEX idx_pickem_contests_status ON pickem_contests(status);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS pickem_badges;")
    op.execute("DROP TABLE IF EXISTS pickem_entries;")
    op.execute("DROP TABLE IF EXISTS pickem_contests;")
```

- [ ] **Step 3: Run the migration**

Run: `cd apps/api && .venv/Scripts/alembic upgrade head`

- [ ] **Step 4: Commit**

```bash
git add apps/api/alembic/versions/
git commit -m "feat(api): add pickem_contests, pickem_entries, and pickem_badges tables"
```

---

### Task 2: ORM Models + Pydantic Schemas

**Files:**
- Modify: `apps/api/app/models.py`
- Create: `apps/api/app/schemas/pickem.py`

- [ ] **Step 1: Add ORM models to models.py**

Add at the end of `apps/api/app/models.py`:

```python
class PickemContest(Base):
    __tablename__ = "pickem_contests"

    id = Column(Integer, primary_key=True)
    sport_id = Column(Integer, ForeignKey("sports.id"))
    season_year = Column(Integer, nullable=False)
    week_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    status = Column(String(20), default="draft")
    opens_at = Column(DateTime)
    locks_at = Column(DateTime)
    scored_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    sport = relationship("Sport")
    entries = relationship("PickemEntry", back_populates="contest", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("sport_id", "season_year", "week_number"),)


class PickemEntry(Base):
    __tablename__ = "pickem_entries"

    id = Column(Integer, primary_key=True)
    contest_id = Column(Integer, ForeignKey("pickem_contests.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    game_id = Column(Integer, ForeignKey("games.id"))
    picked_team_id = Column(Integer, ForeignKey("teams.id"))
    is_correct = Column(Boolean)
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    contest = relationship("PickemContest", back_populates="entries")
    user = relationship("User")
    game = relationship("Game")
    picked_team = relationship("Team")

    __table_args__ = (UniqueConstraint("contest_id", "user_id", "game_id"),)


class PickemBadge(Base):
    __tablename__ = "pickem_badges"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    badge_type = Column(String(50), nullable=False)
    badge_name = Column(String(200), nullable=False)
    description = Column(String(500))
    earned_at = Column(DateTime, server_default=func.now())
    contest_id = Column(Integer, ForeignKey("pickem_contests.id"))
    metadata_json = Column(Text)

    user = relationship("User")
    contest = relationship("PickemContest")
```

- [ ] **Step 2: Create Pydantic schemas**

Create `apps/api/app/schemas/pickem.py`:

```python
from datetime import datetime
from pydantic import BaseModel


class ContestOut(BaseModel):
    id: int
    sport_id: int
    season_year: int
    week_number: int
    title: str
    status: str
    opens_at: datetime | None = None
    locks_at: datetime | None = None
    scored_at: datetime | None = None
    game_count: int = 0

    model_config = {"from_attributes": True}


class ContestCreateRequest(BaseModel):
    sport: str
    season_year: int
    week_number: int
    title: str | None = None
    opens_at: datetime | None = None
    locks_at: datetime | None = None


class PickRequest(BaseModel):
    game_id: int
    picked_team_id: int


class PicksBatchRequest(BaseModel):
    picks: list[PickRequest]


class EntryOut(BaseModel):
    id: int
    game_id: int
    picked_team_id: int
    picked_team_name: str | None = None
    home_team_name: str | None = None
    away_team_name: str | None = None
    home_score: int | None = None
    away_score: int | None = None
    is_correct: bool | None = None
    points_earned: int = 0

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    display_name: str
    total_correct: int
    total_picks: int
    accuracy_pct: float
    total_points: int


class SchoolLeaderboardEntry(BaseModel):
    rank: int
    school_name: str
    school_id: int
    total_correct: int
    total_picks: int
    accuracy_pct: float
    participant_count: int


class BadgeOut(BaseModel):
    id: int
    badge_type: str
    badge_name: str
    description: str | None = None
    earned_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Verify models import**

Run: `cd apps/api && .venv/Scripts/python -c "from app.models import PickemContest, PickemEntry, PickemBadge; print('OK')"`

- [ ] **Step 4: Commit**

```bash
git add apps/api/app/models.py apps/api/app/schemas/pickem.py
git commit -m "feat(api): add Pick'em ORM models and Pydantic schemas"
```

---

### Task 3: Pick'em Service — Contest Lifecycle + Scoring

**Files:**
- Create: `apps/api/app/services/pickem_service.py`

- [ ] **Step 1: Implement the service**

Create `apps/api/app/services/pickem_service.py`:

```python
"""Pick'em contest lifecycle: create → open → lock → score → close.

Scoring:
- 1 point per correct pick
- Bonus: +2 for correctly picking an upset (lower-rated team wins)
- School leaderboard: aggregate correct picks from users who follow that school
"""
from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_

from app.models import (
    PickemContest, PickemEntry, PickemBadge,
    Game, Team, School, Sport, User, UserFavorite, PowerRating,
)


def create_contest(
    db: Session,
    sport_name: str,
    season_year: int,
    week_number: int,
    title: str | None = None,
    opens_at: datetime | None = None,
    locks_at: datetime | None = None,
) -> PickemContest:
    sport = db.query(Sport).filter(Sport.name == sport_name).first()
    if not sport:
        raise ValueError(f"Sport '{sport_name}' not found")

    if title is None:
        title = f"{sport_name} Week {week_number} Pick'em"

    contest = PickemContest(
        sport_id=sport.id,
        season_year=season_year,
        week_number=week_number,
        title=title,
        status="open",
        opens_at=opens_at or datetime.now(timezone.utc),
        locks_at=locks_at,
    )
    db.add(contest)
    db.commit()
    db.refresh(contest)
    return contest


def get_contest_games(db: Session, contest: PickemContest) -> list[Game]:
    """Get all games for a contest's sport/season/week."""
    return (
        db.query(Game)
        .filter(
            Game.sport_id == contest.sport_id,
            Game.season_year == contest.season_year,
            Game.week_number == contest.week_number,
        )
        .order_by(Game.game_date.asc(), Game.id.asc())
        .all()
    )


def submit_picks(
    db: Session,
    contest_id: int,
    user_id: int,
    picks: list[dict],
) -> list[PickemEntry]:
    """Submit or update picks for a contest. picks = [{game_id, picked_team_id}, ...]"""
    contest = db.query(PickemContest).filter(PickemContest.id == contest_id).first()
    if not contest:
        raise ValueError("Contest not found")
    if contest.status != "open":
        raise ValueError(f"Contest is {contest.status}, not open for picks")
    if contest.locks_at and datetime.now(timezone.utc) > contest.locks_at.replace(tzinfo=timezone.utc):
        raise ValueError("Contest is locked — picks are no longer accepted")

    entries = []
    for pick in picks:
        existing = db.query(PickemEntry).filter(
            PickemEntry.contest_id == contest_id,
            PickemEntry.user_id == user_id,
            PickemEntry.game_id == pick["game_id"],
        ).first()

        if existing:
            existing.picked_team_id = pick["picked_team_id"]
            entries.append(existing)
        else:
            entry = PickemEntry(
                contest_id=contest_id,
                user_id=user_id,
                game_id=pick["game_id"],
                picked_team_id=pick["picked_team_id"],
            )
            db.add(entry)
            entries.append(entry)

    db.commit()
    for e in entries:
        db.refresh(e)
    return entries


def score_contest(db: Session, contest_id: int) -> dict:
    """Score all entries for a contest based on final game results.
    Returns {"scored": N, "games_final": N, "badges_awarded": N}
    """
    contest = db.query(PickemContest).filter(PickemContest.id == contest_id).first()
    if not contest:
        raise ValueError("Contest not found")

    # Get final games for this contest
    final_games = (
        db.query(Game)
        .filter(
            Game.sport_id == contest.sport_id,
            Game.season_year == contest.season_year,
            Game.week_number == contest.week_number,
            Game.status == "final",
        )
        .all()
    )

    # Build winner map: game_id -> winning_team_id
    winners: dict[int, int | None] = {}
    for g in final_games:
        if g.home_score is not None and g.away_score is not None:
            if g.home_score > g.away_score:
                winners[g.id] = g.home_team_id
            elif g.away_score > g.home_score:
                winners[g.id] = g.away_team_id
            else:
                winners[g.id] = None  # tie — no winner

    # Score entries
    entries = db.query(PickemEntry).filter(PickemEntry.contest_id == contest_id).all()
    scored = 0
    for entry in entries:
        if entry.game_id in winners:
            winner = winners[entry.game_id]
            if winner is None:
                entry.is_correct = False
                entry.points_earned = 0
            elif entry.picked_team_id == winner:
                entry.is_correct = True
                entry.points_earned = 1
            else:
                entry.is_correct = False
                entry.points_earned = 0
            scored += 1

    contest.status = "scored"
    contest.scored_at = datetime.now(timezone.utc)
    db.commit()

    # Award badges
    badges_awarded = _award_badges(db, contest_id)

    return {"scored": scored, "games_final": len(final_games), "badges_awarded": badges_awarded}


def _award_badges(db: Session, contest_id: int) -> int:
    """Award badges for notable achievements in a scored contest."""
    awarded = 0

    # Get user scores for this contest
    user_scores = (
        db.query(
            PickemEntry.user_id,
            func.count(PickemEntry.id).label("total"),
            func.sum(case((PickemEntry.is_correct == True, 1), else_=0)).label("correct"),
        )
        .filter(PickemEntry.contest_id == contest_id, PickemEntry.is_correct.isnot(None))
        .group_by(PickemEntry.user_id)
        .all()
    )

    for user_id, total, correct in user_scores:
        if total == 0:
            continue

        # Perfect week
        if correct == total and total >= 5:
            _give_badge(db, user_id, "perfect_week", "Perfect Week",
                        f"Predicted all {total} games correctly", contest_id)
            awarded += 1

        # 80%+ accuracy
        if total >= 5 and (correct / total) >= 0.8:
            _give_badge(db, user_id, "sharp_eye", "Sharp Eye",
                        f"80%+ accuracy ({correct}/{total})", contest_id)
            awarded += 1

    db.commit()
    return awarded


def _give_badge(db: Session, user_id: int, badge_type: str, badge_name: str,
                description: str, contest_id: int) -> None:
    """Award a badge if not already earned for this contest."""
    existing = db.query(PickemBadge).filter(
        PickemBadge.user_id == user_id,
        PickemBadge.badge_type == badge_type,
        PickemBadge.contest_id == contest_id,
    ).first()
    if not existing:
        db.add(PickemBadge(
            user_id=user_id, badge_type=badge_type,
            badge_name=badge_name, description=description,
            contest_id=contest_id,
        ))


def get_individual_leaderboard(db: Session, contest_id: int | None = None,
                                season_year: int | None = None) -> list[dict]:
    """Individual leaderboard. If contest_id given, for that contest. Otherwise season-wide."""
    query = (
        db.query(
            PickemEntry.user_id,
            func.sum(case((PickemEntry.is_correct == True, 1), else_=0)).label("correct"),
            func.count(PickemEntry.id).label("total"),
            func.sum(PickemEntry.points_earned).label("points"),
        )
        .join(PickemContest, PickemEntry.contest_id == PickemContest.id)
        .filter(PickemEntry.is_correct.isnot(None))
    )
    if contest_id:
        query = query.filter(PickemEntry.contest_id == contest_id)
    if season_year:
        query = query.filter(PickemContest.season_year == season_year)

    query = query.group_by(PickemEntry.user_id).order_by(func.sum(PickemEntry.points_earned).desc())
    rows = query.limit(100).all()

    leaderboard = []
    for rank, (user_id, correct, total, points) in enumerate(rows, 1):
        user = db.query(User).filter(User.id == user_id).first()
        display_name = f"{user.first_name} {user.last_name[0]}." if user and user.first_name and user.last_name else f"User #{user_id}"
        leaderboard.append({
            "rank": rank,
            "user_id": user_id,
            "display_name": display_name,
            "total_correct": int(correct),
            "total_picks": int(total),
            "accuracy_pct": round(float(correct) / float(total) * 100, 1) if total > 0 else 0.0,
            "total_points": int(points or 0),
        })
    return leaderboard


def get_school_leaderboard(db: Session, contest_id: int | None = None,
                            season_year: int | None = None) -> list[dict]:
    """School leaderboard: aggregate picks from users who follow each school."""
    # Get user -> school mapping via favorites
    fav_query = (
        db.query(UserFavorite.user_id, Team.school_id)
        .join(Team, and_(UserFavorite.entity_id == Team.id, UserFavorite.entity_type == "team"))
    )
    user_school = {row.user_id: row.school_id for row in fav_query.all()}

    if not user_school:
        return []

    # Get all scored entries
    entry_query = (
        db.query(PickemEntry)
        .join(PickemContest, PickemEntry.contest_id == PickemContest.id)
        .filter(PickemEntry.is_correct.isnot(None))
    )
    if contest_id:
        entry_query = entry_query.filter(PickemEntry.contest_id == contest_id)
    if season_year:
        entry_query = entry_query.filter(PickemContest.season_year == season_year)

    entries = entry_query.all()

    # Aggregate by school
    school_stats: dict[int, dict] = {}
    school_users: dict[int, set] = {}
    for entry in entries:
        school_id = user_school.get(entry.user_id)
        if school_id is None:
            continue
        if school_id not in school_stats:
            school_stats[school_id] = {"correct": 0, "total": 0}
            school_users[school_id] = set()
        school_stats[school_id]["total"] += 1
        if entry.is_correct:
            school_stats[school_id]["correct"] += 1
        school_users[school_id].add(entry.user_id)

    # Build leaderboard
    schools_data = []
    for school_id, stats in school_stats.items():
        school = db.query(School).filter(School.id == school_id).first()
        if not school:
            continue
        schools_data.append({
            "school_id": school_id,
            "school_name": school.name,
            "total_correct": stats["correct"],
            "total_picks": stats["total"],
            "accuracy_pct": round(stats["correct"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0.0,
            "participant_count": len(school_users[school_id]),
        })

    schools_data.sort(key=lambda x: (-x["total_correct"], -x["accuracy_pct"]))
    for i, s in enumerate(schools_data, 1):
        s["rank"] = i

    return schools_data
```

- [ ] **Step 2: Commit**

```bash
git add apps/api/app/services/pickem_service.py
git commit -m "feat(api): add Pick'em service with contest lifecycle, scoring, and leaderboards"
```

---

### Task 4: Pick'em API Router

**Files:**
- Create: `apps/api/app/routers/pickem.py`
- Modify: `apps/api/app/main.py`

- [ ] **Step 1: Create the router**

Create `apps/api/app/routers/pickem.py`:

```python
"""Pick'em prediction contest endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PickemContest, PickemEntry, PickemBadge, Game, Team, School, Sport
from app.auth.dependencies import get_current_user, get_optional_user
from app.models import User
from app.schemas.pickem import (
    ContestOut, ContestCreateRequest, PicksBatchRequest,
    EntryOut, LeaderboardEntry, SchoolLeaderboardEntry, BadgeOut,
)
from app.services.pickem_service import (
    create_contest, get_contest_games, submit_picks, score_contest,
    get_individual_leaderboard, get_school_leaderboard,
)

router = APIRouter()


@router.get("/contests", response_model=list[ContestOut])
def list_contests(
    sport: str | None = Query(None),
    season_year: int | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(PickemContest)
    if sport:
        query = query.join(Sport).filter(Sport.name == sport)
    if season_year:
        query = query.filter(PickemContest.season_year == season_year)
    if status:
        query = query.filter(PickemContest.status == status)
    contests = query.order_by(PickemContest.week_number.desc()).all()

    result = []
    for c in contests:
        game_count = db.query(Game).filter(
            Game.sport_id == c.sport_id,
            Game.season_year == c.season_year,
            Game.week_number == c.week_number,
        ).count()
        out = ContestOut(
            id=c.id, sport_id=c.sport_id, season_year=c.season_year,
            week_number=c.week_number, title=c.title, status=c.status,
            opens_at=c.opens_at, locks_at=c.locks_at, scored_at=c.scored_at,
            game_count=game_count,
        )
        result.append(out)
    return result


@router.post("/contests", response_model=ContestOut, status_code=201)
def create_new_contest(
    req: ContestCreateRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    title = req.title or f"{req.sport} Week {req.week_number} Pick'em"
    try:
        contest = create_contest(db, req.sport, req.season_year, req.week_number, title, req.opens_at, req.locks_at)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    game_count = db.query(Game).filter(
        Game.sport_id == contest.sport_id,
        Game.season_year == contest.season_year,
        Game.week_number == contest.week_number,
    ).count()

    return ContestOut(
        id=contest.id, sport_id=contest.sport_id, season_year=contest.season_year,
        week_number=contest.week_number, title=contest.title, status=contest.status,
        opens_at=contest.opens_at, locks_at=contest.locks_at, scored_at=contest.scored_at,
        game_count=game_count,
    )


@router.get("/contests/{contest_id}", response_model=ContestOut)
def get_contest(contest_id: int, db: Session = Depends(get_db)):
    contest = db.query(PickemContest).filter(PickemContest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    game_count = db.query(Game).filter(
        Game.sport_id == contest.sport_id,
        Game.season_year == contest.season_year,
        Game.week_number == contest.week_number,
    ).count()

    return ContestOut(
        id=contest.id, sport_id=contest.sport_id, season_year=contest.season_year,
        week_number=contest.week_number, title=contest.title, status=contest.status,
        opens_at=contest.opens_at, locks_at=contest.locks_at, scored_at=contest.scored_at,
        game_count=game_count,
    )


@router.get("/contests/{contest_id}/games")
def get_games_for_contest(contest_id: int, db: Session = Depends(get_db)):
    contest = db.query(PickemContest).filter(PickemContest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    games = get_contest_games(db, contest)
    result = []
    for g in games:
        home_school = db.query(School).join(Team).filter(Team.id == g.home_team_id).first()
        away_school = db.query(School).join(Team).filter(Team.id == g.away_team_id).first()
        result.append({
            "game_id": g.id,
            "home_team_id": g.home_team_id,
            "away_team_id": g.away_team_id,
            "home_team_name": home_school.name if home_school else None,
            "away_team_name": away_school.name if away_school else None,
            "game_date": str(g.game_date) if g.game_date else None,
            "home_score": g.home_score,
            "away_score": g.away_score,
            "status": g.status,
        })
    return result


@router.post("/contests/{contest_id}/picks", response_model=list[EntryOut])
def submit_contest_picks(
    contest_id: int,
    req: PicksBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        entries = submit_picks(
            db, contest_id, current_user.id,
            [{"game_id": p.game_id, "picked_team_id": p.picked_team_id} for p in req.picks],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = []
    for e in entries:
        game = db.query(Game).filter(Game.id == e.game_id).first()
        home_school = db.query(School).join(Team).filter(Team.id == game.home_team_id).first() if game else None
        away_school = db.query(School).join(Team).filter(Team.id == game.away_team_id).first() if game else None
        picked_school = db.query(School).join(Team).filter(Team.id == e.picked_team_id).first()
        result.append(EntryOut(
            id=e.id, game_id=e.game_id, picked_team_id=e.picked_team_id,
            picked_team_name=picked_school.name if picked_school else None,
            home_team_name=home_school.name if home_school else None,
            away_team_name=away_school.name if away_school else None,
            home_score=game.home_score if game else None,
            away_score=game.away_score if game else None,
            is_correct=e.is_correct, points_earned=e.points_earned,
        ))
    return result


@router.get("/contests/{contest_id}/my-picks", response_model=list[EntryOut])
def get_my_picks(
    contest_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entries = db.query(PickemEntry).filter(
        PickemEntry.contest_id == contest_id,
        PickemEntry.user_id == current_user.id,
    ).all()

    result = []
    for e in entries:
        game = db.query(Game).filter(Game.id == e.game_id).first()
        home_school = db.query(School).join(Team).filter(Team.id == game.home_team_id).first() if game else None
        away_school = db.query(School).join(Team).filter(Team.id == game.away_team_id).first() if game else None
        picked_school = db.query(School).join(Team).filter(Team.id == e.picked_team_id).first()
        result.append(EntryOut(
            id=e.id, game_id=e.game_id, picked_team_id=e.picked_team_id,
            picked_team_name=picked_school.name if picked_school else None,
            home_team_name=home_school.name if home_school else None,
            away_team_name=away_school.name if away_school else None,
            home_score=game.home_score if game else None,
            away_score=game.away_score if game else None,
            is_correct=e.is_correct, points_earned=e.points_earned,
        ))
    return result


@router.post("/contests/{contest_id}/score")
def score_a_contest(
    contest_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = score_contest(db, contest_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


@router.get("/leaderboard/individual", response_model=list[LeaderboardEntry])
def individual_leaderboard(
    contest_id: int | None = Query(None),
    season_year: int | None = Query(None),
    db: Session = Depends(get_db),
):
    rows = get_individual_leaderboard(db, contest_id=contest_id, season_year=season_year)
    return [LeaderboardEntry(**r) for r in rows]


@router.get("/leaderboard/schools", response_model=list[SchoolLeaderboardEntry])
def school_leaderboard(
    contest_id: int | None = Query(None),
    season_year: int | None = Query(None),
    db: Session = Depends(get_db),
):
    rows = get_school_leaderboard(db, contest_id=contest_id, season_year=season_year)
    return [SchoolLeaderboardEntry(**r) for r in rows]


@router.get("/badges", response_model=list[BadgeOut])
def my_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    badges = db.query(PickemBadge).filter(
        PickemBadge.user_id == current_user.id
    ).order_by(PickemBadge.earned_at.desc()).all()
    return badges
```

- [ ] **Step 2: Register router in main.py**

Add to imports: `from app.routers import schools, teams, games, ratings, simulations, auth, subscriptions, favorites, pickem`

Add router: `app.include_router(pickem.router, prefix="/api/v1/pickem", tags=["pickem"])`

- [ ] **Step 3: Verify app loads**

Run: `cd apps/api && .venv/Scripts/python -c "from app.main import app; print(f'Routes: {len(app.routes)}')"` — should be ~45+

- [ ] **Step 4: Commit**

```bash
git add apps/api/app/routers/pickem.py apps/api/app/main.py
git commit -m "feat(api): add Pick'em contest, picks, leaderboard, and badge endpoints"
```

---

### Task 5: Pick'em API Tests

**Files:**
- Create: `apps/api/tests/test_pickem.py`

- [ ] **Step 1: Write tests**

Create `apps/api/tests/test_pickem.py`:

```python
"""Pick'em integration tests."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import PickemContest, PickemEntry, PickemBadge, Game

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup():
    yield
    db = SessionLocal()
    db.query(PickemBadge).delete()
    db.query(PickemEntry).delete()
    db.query(PickemContest).delete()
    db.query(Game).filter(Game.source == "test").delete()
    db.commit()
    db.close()


def _get_token(email: str) -> str:
    resp = client.post("/api/v1/auth/register", json={
        "email": email, "password": "testpass123",
        "first_name": "Test", "last_name": "User",
    })
    if resp.status_code == 400:  # already exists
        resp = client.post("/api/v1/auth/login", json={
            "email": email, "password": "testpass123",
        })
    return resp.json()["access_token"]


def _create_test_games(db, count=3):
    """Create test games for pick'em. Returns list of game IDs."""
    teams = db.execute(
        __import__("sqlalchemy").text(
            "SELECT id FROM teams WHERE sport_id=1 AND season_year=2025 LIMIT :n"
        ), {"n": count * 2}
    ).fetchall()
    if len(teams) < count * 2:
        return []
    game_ids = []
    for i in range(count):
        game = Game(
            home_team_id=teams[i * 2][0],
            away_team_id=teams[i * 2 + 1][0],
            sport_id=1, season_year=2025, week_number=1,
            game_date="2025-09-05", status="scheduled", source="test",
        )
        db.add(game)
        db.flush()
        game_ids.append(game.id)
    db.commit()
    return game_ids


def test_create_contest():
    token = _get_token("pickem1@test.com")
    resp = client.post("/api/v1/pickem/contests", json={
        "sport": "Football", "season_year": 2025, "week_number": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json()["status"] == "open"
    assert "Week 1" in resp.json()["title"]


def test_list_contests():
    token = _get_token("pickem2@test.com")
    client.post("/api/v1/pickem/contests", json={
        "sport": "Football", "season_year": 2025, "week_number": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    resp = client.get("/api/v1/pickem/contests?sport=Football&season_year=2025")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_submit_picks():
    token = _get_token("pickem3@test.com")
    db = SessionLocal()
    game_ids = _create_test_games(db)
    db.close()
    if not game_ids:
        return

    # Create contest
    cr = client.post("/api/v1/pickem/contests", json={
        "sport": "Football", "season_year": 2025, "week_number": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    contest_id = cr.json()["id"]

    # Get games to find valid team IDs
    games_resp = client.get(f"/api/v1/pickem/contests/{contest_id}/games")
    games = games_resp.json()
    if not games:
        return

    picks = [{"game_id": g["game_id"], "picked_team_id": g["home_team_id"]} for g in games]
    resp = client.post(f"/api/v1/pickem/contests/{contest_id}/picks",
        json={"picks": picks},
        headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == len(picks)


def test_get_my_picks():
    token = _get_token("pickem4@test.com")
    db = SessionLocal()
    game_ids = _create_test_games(db)
    db.close()
    if not game_ids:
        return

    cr = client.post("/api/v1/pickem/contests", json={
        "sport": "Football", "season_year": 2025, "week_number": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    contest_id = cr.json()["id"]

    games_resp = client.get(f"/api/v1/pickem/contests/{contest_id}/games")
    games = games_resp.json()
    if not games:
        return

    picks = [{"game_id": games[0]["game_id"], "picked_team_id": games[0]["home_team_id"]}]
    client.post(f"/api/v1/pickem/contests/{contest_id}/picks",
        json={"picks": picks},
        headers={"Authorization": f"Bearer {token}"})

    resp = client.get(f"/api/v1/pickem/contests/{contest_id}/my-picks",
        headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_leaderboard_empty():
    resp = client.get("/api/v1/pickem/leaderboard/individual")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_school_leaderboard_empty():
    resp = client.get("/api/v1/pickem/leaderboard/schools")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_badges_requires_auth():
    resp = client.get("/api/v1/pickem/badges")
    assert resp.status_code == 401
```

- [ ] **Step 2: Run tests**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/test_pickem.py -v`
Then full suite: `.venv/Scripts/python -m pytest tests/ -v`

- [ ] **Step 3: Commit**

```bash
git add apps/api/tests/test_pickem.py
git commit -m "test(api): add Pick'em contest, picks, and leaderboard tests"
```

---

### Task 6: Frontend — Pick'em API Client + Components

**Files:**
- Modify: `apps/web/src/lib/api.ts`
- Create: `apps/web/src/components/PickemCard.tsx`
- Create: `apps/web/src/components/LeaderboardTable.tsx`
- Create: `apps/web/src/components/BadgeDisplay.tsx`

- [ ] **Step 1: Add Pick'em types and API functions to api.ts**

Add at the end of `apps/web/src/lib/api.ts`:

```typescript
// --- Pick'em ---

export interface PickemContest {
  id: number;
  sport_id: number;
  season_year: number;
  week_number: number;
  title: string;
  status: string;
  opens_at: string | null;
  locks_at: string | null;
  scored_at: string | null;
  game_count: number;
}

export interface PickemGame {
  game_id: number;
  home_team_id: number;
  away_team_id: number;
  home_team_name: string | null;
  away_team_name: string | null;
  game_date: string | null;
  home_score: number | null;
  away_score: number | null;
  status: string;
}

export interface PickemEntry {
  id: number;
  game_id: number;
  picked_team_id: number;
  picked_team_name: string | null;
  home_team_name: string | null;
  away_team_name: string | null;
  home_score: number | null;
  away_score: number | null;
  is_correct: boolean | null;
  points_earned: number;
}

export interface LeaderboardRow {
  rank: number;
  user_id: number;
  display_name: string;
  total_correct: number;
  total_picks: number;
  accuracy_pct: number;
  total_points: number;
}

export interface SchoolLeaderboardRow {
  rank: number;
  school_name: string;
  school_id: number;
  total_correct: number;
  total_picks: number;
  accuracy_pct: number;
  participant_count: number;
}

export interface Badge {
  id: number;
  badge_type: string;
  badge_name: string;
  description: string | null;
  earned_at: string;
}

export async function fetchContests(params?: {
  sport?: string;
  season_year?: number;
  status?: string;
}): Promise<PickemContest[]> {
  const sp = new URLSearchParams();
  if (params?.sport) sp.set("sport", params.sport);
  if (params?.season_year) sp.set("season_year", String(params.season_year));
  if (params?.status) sp.set("status", params.status);
  return apiFetch(`/api/v1/pickem/contests?${sp}`);
}

export async function fetchContest(contestId: number): Promise<PickemContest> {
  return apiFetch(`/api/v1/pickem/contests/${contestId}`);
}

export async function fetchContestGames(contestId: number): Promise<PickemGame[]> {
  return apiFetch(`/api/v1/pickem/contests/${contestId}/games`);
}

export async function submitPicks(
  contestId: number,
  picks: { game_id: number; picked_team_id: number }[],
): Promise<PickemEntry[]> {
  return apiFetch(`/api/v1/pickem/contests/${contestId}/picks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ picks }),
  });
}

export async function fetchMyPicks(contestId: number): Promise<PickemEntry[]> {
  return apiFetch(`/api/v1/pickem/contests/${contestId}/my-picks`);
}

export async function fetchIndividualLeaderboard(params?: {
  contest_id?: number;
  season_year?: number;
}): Promise<LeaderboardRow[]> {
  const sp = new URLSearchParams();
  if (params?.contest_id) sp.set("contest_id", String(params.contest_id));
  if (params?.season_year) sp.set("season_year", String(params.season_year));
  return apiFetch(`/api/v1/pickem/leaderboard/individual?${sp}`);
}

export async function fetchSchoolLeaderboard(params?: {
  contest_id?: number;
  season_year?: number;
}): Promise<SchoolLeaderboardRow[]> {
  const sp = new URLSearchParams();
  if (params?.contest_id) sp.set("contest_id", String(params.contest_id));
  if (params?.season_year) sp.set("season_year", String(params.season_year));
  return apiFetch(`/api/v1/pickem/leaderboard/schools?${sp}`);
}

export async function fetchMyBadges(): Promise<Badge[]> {
  return apiFetch("/api/v1/pickem/badges");
}
```

- [ ] **Step 2: Create PickemCard component**

Create `apps/web/src/components/PickemCard.tsx`:

```tsx
"use client";

import type { PickemGame } from "@/lib/api";

interface PickemCardProps {
  game: PickemGame;
  pickedTeamId: number | null;
  onPick: (gameId: number, teamId: number) => void;
  locked: boolean;
  result?: { is_correct: boolean | null };
}

export default function PickemCard({ game, pickedTeamId, onPick, locked, result }: PickemCardProps) {
  const isFinal = game.status === "final";

  function teamButton(teamId: number, teamName: string | null, score: number | null, isHome: boolean) {
    const selected = pickedTeamId === teamId;
    const correct = result?.is_correct === true && selected;
    const wrong = result?.is_correct === false && selected;

    return (
      <button
        onClick={() => !locked && onPick(game.game_id, teamId)}
        disabled={locked}
        className={`flex-1 rounded-lg p-3 text-center transition-all border ${
          correct ? "border-green-500 bg-green-500/10" :
          wrong ? "border-red-500 bg-red-500/10" :
          selected ? "border-crimson bg-crimson/10" :
          "border-steel-gray/30 hover:border-steel-gray"
        } ${locked && !selected ? "opacity-50" : ""}`}
      >
        <div className="text-xs text-steel-gray mb-1">{isHome ? "HOME" : "AWAY"}</div>
        <div className={`font-semibold text-sm ${selected ? "text-white" : "text-steel-gray"}`}>
          {teamName || `Team #${teamId}`}
        </div>
        {isFinal && score !== null && (
          <div className="text-lg font-bold mt-1">{score}</div>
        )}
      </button>
    );
  }

  return (
    <div className="rounded-lg border border-steel-gray/30 p-4 bg-charcoal">
      {game.game_date && (
        <div className="text-xs text-steel-gray mb-2">
          {new Date(game.game_date + "T00:00:00").toLocaleDateString("en-US", {
            weekday: "short", month: "short", day: "numeric",
          })}
          {isFinal && <span className="ml-2 text-steel-gray">FINAL</span>}
        </div>
      )}
      <div className="flex gap-3">
        {teamButton(game.home_team_id, game.home_team_name, game.home_score, true)}
        <div className="flex items-center text-steel-gray text-sm font-bold">VS</div>
        {teamButton(game.away_team_id, game.away_team_name, game.away_score, false)}
      </div>
      {result && result.is_correct !== null && (
        <div className={`mt-2 text-xs text-center font-bold ${result.is_correct ? "text-green-500" : "text-red-500"}`}>
          {result.is_correct ? "CORRECT ✓" : "WRONG ✗"}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Create LeaderboardTable component**

Create `apps/web/src/components/LeaderboardTable.tsx`:

```tsx
import type { LeaderboardRow, SchoolLeaderboardRow } from "@/lib/api";

interface IndividualProps {
  type: "individual";
  rows: LeaderboardRow[];
}

interface SchoolProps {
  type: "school";
  rows: SchoolLeaderboardRow[];
}

type LeaderboardTableProps = IndividualProps | SchoolProps;

export default function LeaderboardTable(props: LeaderboardTableProps) {
  if (props.type === "individual") {
    return (
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-steel-gray text-steel-gray uppercase tracking-wide text-xs">
              <th className="px-3 py-2 w-12">#</th>
              <th className="px-3 py-2">Name</th>
              <th className="px-3 py-2 text-center">Correct</th>
              <th className="px-3 py-2 text-center">Total</th>
              <th className="px-3 py-2 text-center">Accuracy</th>
              <th className="px-3 py-2 text-right">Points</th>
            </tr>
          </thead>
          <tbody>
            {props.rows.map((r) => (
              <tr key={r.user_id} className="border-b border-steel-gray/20 hover:bg-charcoal/50">
                <td className={`px-3 py-2 font-bold ${r.rank <= 3 ? "text-crimson" : "text-steel-gray"}`}>{r.rank}</td>
                <td className="px-3 py-2 font-semibold">{r.display_name}</td>
                <td className="px-3 py-2 text-center">{r.total_correct}</td>
                <td className="px-3 py-2 text-center text-steel-gray">{r.total_picks}</td>
                <td className="px-3 py-2 text-center">{r.accuracy_pct}%</td>
                <td className="px-3 py-2 text-right font-mono font-bold">{r.total_points}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {props.rows.length === 0 && (
          <p className="mt-4 text-center text-steel-gray text-sm">No entries yet.</p>
        )}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-steel-gray text-steel-gray uppercase tracking-wide text-xs">
            <th className="px-3 py-2 w-12">#</th>
            <th className="px-3 py-2">School</th>
            <th className="px-3 py-2 text-center">Correct</th>
            <th className="px-3 py-2 text-center">Total</th>
            <th className="px-3 py-2 text-center">Accuracy</th>
            <th className="px-3 py-2 text-right">Participants</th>
          </tr>
        </thead>
        <tbody>
          {props.rows.map((r) => (
            <tr key={r.school_id} className="border-b border-steel-gray/20 hover:bg-charcoal/50">
              <td className={`px-3 py-2 font-bold ${r.rank <= 3 ? "text-crimson" : "text-steel-gray"}`}>{r.rank}</td>
              <td className="px-3 py-2 font-semibold">{r.school_name}</td>
              <td className="px-3 py-2 text-center">{r.total_correct}</td>
              <td className="px-3 py-2 text-center text-steel-gray">{r.total_picks}</td>
              <td className="px-3 py-2 text-center">{r.accuracy_pct}%</td>
              <td className="px-3 py-2 text-right">{r.participant_count}</td>
            </tr>
          ))}
        </tbody>
        {props.rows.length === 0 && (
          <p className="mt-4 text-center text-steel-gray text-sm">No school data yet. Follow a team to represent your school!</p>
        )}
      </table>
    </div>
  );
}
```

- [ ] **Step 4: Create BadgeDisplay component**

Create `apps/web/src/components/BadgeDisplay.tsx`:

```tsx
import type { Badge } from "@/lib/api";

interface BadgeDisplayProps {
  badges: Badge[];
}

const BADGE_ICONS: Record<string, string> = {
  perfect_week: "🏆",
  sharp_eye: "🎯",
  upset_caller: "🔮",
  streak_3: "🔥",
};

export default function BadgeDisplay({ badges }: BadgeDisplayProps) {
  if (badges.length === 0) {
    return <p className="text-sm text-steel-gray">No badges earned yet. Make picks to start earning!</p>;
  }

  return (
    <div className="flex flex-wrap gap-3">
      {badges.map((b) => (
        <div
          key={b.id}
          className="rounded-lg border border-steel-gray/30 p-3 text-center min-w-[100px]"
        >
          <div className="text-2xl mb-1">{BADGE_ICONS[b.badge_type] || "🏅"}</div>
          <div className="text-xs font-bold">{b.badge_name}</div>
          {b.description && (
            <div className="text-xs text-steel-gray mt-1">{b.description}</div>
          )}
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/lib/api.ts apps/web/src/components/PickemCard.tsx apps/web/src/components/LeaderboardTable.tsx apps/web/src/components/BadgeDisplay.tsx
git commit -m "feat(web): add Pick'em API client and reusable components"
```

---

### Task 7: Frontend — Pick'em Pages

**Files:**
- Create: `apps/web/src/app/pickem/page.tsx`
- Create: `apps/web/src/app/pickem/[contestId]/page.tsx`
- Create: `apps/web/src/app/pickem/leaderboard/page.tsx`
- Modify: `apps/web/src/components/Navbar.tsx` — add Pick'em link

- [ ] **Step 1: Create Pick'em Hub page**

Create `apps/web/src/app/pickem/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchContests, PickemContest } from "@/lib/api";

export default function PickemHubPage() {
  const [contests, setContests] = useState<PickemContest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContests({ season_year: 2025 })
      .then(setContests)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const open = contests.filter((c) => c.status === "open");
  const scored = contests.filter((c) => c.status === "scored" || c.status === "closed");

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-4xl font-bold mb-2" style={{ fontFamily: "var(--font-display)" }}>
        <span className="text-white">PICK</span>
        <span className="text-crimson">&apos;EM</span>
      </h1>
      <p className="text-steel-gray mb-8">
        Predict game outcomes. Compete against your school. Earn badges.
      </p>

      {loading && <p className="text-steel-gray">Loading contests...</p>}

      {!loading && open.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xl font-bold mb-4" style={{ fontFamily: "var(--font-display)" }}>
            OPEN CONTESTS
          </h2>
          <div className="grid gap-4 md:grid-cols-2">
            {open.map((c) => (
              <Link
                key={c.id}
                href={`/pickem/${c.id}`}
                className="rounded-lg border border-crimson/50 bg-crimson/5 p-6 hover:bg-crimson/10 transition-colors"
              >
                <div className="font-bold text-lg" style={{ fontFamily: "var(--font-display)" }}>
                  {c.title}
                </div>
                <div className="text-sm text-steel-gray mt-1">
                  {c.game_count} games &middot; Week {c.week_number}
                </div>
                <div className="mt-3 text-sm text-crimson font-semibold">
                  Make Your Picks →
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {!loading && scored.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xl font-bold mb-4" style={{ fontFamily: "var(--font-display)" }}>
            RESULTS
          </h2>
          <div className="grid gap-4 md:grid-cols-2">
            {scored.map((c) => (
              <Link
                key={c.id}
                href={`/pickem/${c.id}`}
                className="rounded-lg border border-steel-gray/30 p-6 hover:border-steel-gray transition-colors"
              >
                <div className="font-bold" style={{ fontFamily: "var(--font-display)" }}>
                  {c.title}
                </div>
                <div className="text-sm text-steel-gray mt-1">
                  {c.game_count} games &middot; Scored
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {!loading && contests.length === 0 && (
        <div className="rounded-lg border border-steel-gray/30 p-8 text-center">
          <p className="text-lg text-steel-gray mb-2">No contests yet this season</p>
          <p className="text-sm text-steel-gray/70">
            Pick&apos;em contests will open each week once game schedules are posted.
          </p>
        </div>
      )}

      <div className="mt-8">
        <Link href="/pickem/leaderboard"
          className="text-crimson hover:underline font-semibold text-sm">
          View Leaderboards →
        </Link>
      </div>
    </main>
  );
}
```

- [ ] **Step 2: Create Contest Detail page**

Create `apps/web/src/app/pickem/[contestId]/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useAuth } from "@/lib/auth";
import {
  fetchContest, fetchContestGames, fetchMyPicks, submitPicks,
  PickemContest, PickemGame, PickemEntry,
} from "@/lib/api";
import PickemCard from "@/components/PickemCard";
import Link from "next/link";

export default function ContestDetailPage() {
  const params = useParams();
  const contestId = Number(params.contestId);
  const { user } = useAuth();

  const [contest, setContest] = useState<PickemContest | null>(null);
  const [games, setGames] = useState<PickemGame[]>([]);
  const [myPicks, setMyPicks] = useState<Record<number, number>>({});
  const [results, setResults] = useState<Record<number, { is_correct: boolean | null }>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!contestId) return;
    Promise.all([
      fetchContest(contestId),
      fetchContestGames(contestId),
    ])
      .then(([c, g]) => {
        setContest(c);
        setGames(g);
      })
      .catch(() => {})
      .finally(() => setLoading(false));

    if (user) {
      fetchMyPicks(contestId)
        .then((entries) => {
          const picks: Record<number, number> = {};
          const res: Record<number, { is_correct: boolean | null }> = {};
          for (const e of entries) {
            picks[e.game_id] = e.picked_team_id;
            res[e.game_id] = { is_correct: e.is_correct };
          }
          setMyPicks(picks);
          setResults(res);
        })
        .catch(() => {});
    }
  }, [contestId, user]);

  const handlePick = (gameId: number, teamId: number) => {
    setMyPicks((prev) => ({ ...prev, [gameId]: teamId }));
  };

  const handleSubmit = async () => {
    if (!user) { setMessage("Log in to save your picks"); return; }
    const picks = Object.entries(myPicks).map(([gid, tid]) => ({
      game_id: Number(gid), picked_team_id: tid,
    }));
    if (picks.length === 0) { setMessage("Make at least one pick"); return; }
    setSubmitting(true);
    setMessage("");
    try {
      await submitPicks(contestId, picks);
      setMessage("Picks saved!");
    } catch (e: any) {
      setMessage(e.message || "Failed to save picks");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <main className="mx-auto max-w-5xl px-4 py-8"><p className="text-steel-gray">Loading...</p></main>;
  if (!contest) return <main className="mx-auto max-w-5xl px-4 py-8"><p className="text-crimson">Contest not found</p></main>;

  const isOpen = contest.status === "open";
  const isScored = contest.status === "scored" || contest.status === "closed";
  const picksCount = Object.keys(myPicks).length;

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-3xl font-bold mb-1" style={{ fontFamily: "var(--font-display)" }}>
        {contest.title}
      </h1>
      <div className="text-steel-gray text-sm mb-6">
        {contest.game_count} games &middot;
        {isOpen ? " Open for picks" : isScored ? " Scored" : ` ${contest.status}`}
        {isOpen && picksCount > 0 && ` · ${picksCount} picks made`}
      </div>

      <div className="grid gap-4 md:grid-cols-2 mb-6">
        {games.map((g) => (
          <PickemCard
            key={g.game_id}
            game={g}
            pickedTeamId={myPicks[g.game_id] ?? null}
            onPick={handlePick}
            locked={!isOpen}
            result={results[g.game_id]}
          />
        ))}
      </div>

      {isOpen && (
        <div className="flex items-center gap-4">
          {user ? (
            <button
              onClick={handleSubmit}
              disabled={submitting || picksCount === 0}
              className="rounded bg-crimson px-6 py-3 font-semibold text-white hover:bg-crimson/80 transition-colors disabled:opacity-50"
            >
              {submitting ? "Saving..." : `Submit ${picksCount} Pick${picksCount !== 1 ? "s" : ""}`}
            </button>
          ) : (
            <Link href="/login" className="rounded bg-crimson px-6 py-3 font-semibold text-white hover:bg-crimson/80 transition-colors">
              Log In to Save Picks
            </Link>
          )}
          {message && <span className={`text-sm ${message.includes("saved") ? "text-green-500" : "text-crimson"}`}>{message}</span>}
        </div>
      )}

      {isScored && (
        <Link href="/pickem/leaderboard" className="text-crimson hover:underline text-sm font-semibold">
          View Leaderboard →
        </Link>
      )}
    </main>
  );
}
```

- [ ] **Step 3: Create Leaderboard page**

Create `apps/web/src/app/pickem/leaderboard/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import {
  fetchIndividualLeaderboard, fetchSchoolLeaderboard,
  LeaderboardRow, SchoolLeaderboardRow,
} from "@/lib/api";
import LeaderboardTable from "@/components/LeaderboardTable";

export default function LeaderboardPage() {
  const [tab, setTab] = useState<"individual" | "school">("individual");
  const [individual, setIndividual] = useState<LeaderboardRow[]>([]);
  const [schools, setSchools] = useState<SchoolLeaderboardRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchIndividualLeaderboard({ season_year: 2025 }),
      fetchSchoolLeaderboard({ season_year: 2025 }),
    ])
      .then(([ind, sch]) => {
        setIndividual(ind);
        setSchools(sch);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-3xl font-bold mb-6" style={{ fontFamily: "var(--font-display)" }}>
        <span className="text-white">LEADER</span>
        <span className="text-crimson">BOARD</span>
      </h1>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setTab("individual")}
          className={`rounded px-4 py-2 text-sm font-semibold transition-colors ${
            tab === "individual" ? "bg-crimson text-white" : "bg-steel-gray/20 text-steel-gray hover:text-white"
          }`}
        >
          Individual
        </button>
        <button
          onClick={() => setTab("school")}
          className={`rounded px-4 py-2 text-sm font-semibold transition-colors ${
            tab === "school" ? "bg-crimson text-white" : "bg-steel-gray/20 text-steel-gray hover:text-white"
          }`}
        >
          School vs School
        </button>
      </div>

      {loading && <p className="text-steel-gray">Loading...</p>}

      {!loading && tab === "individual" && (
        <LeaderboardTable type="individual" rows={individual} />
      )}

      {!loading && tab === "school" && (
        <LeaderboardTable type="school" rows={schools} />
      )}
    </main>
  );
}
```

- [ ] **Step 4: Add Pick'em link to Navbar**

Read `apps/web/src/components/Navbar.tsx`. In the desktop nav, add a "Pick'em" link after the "Scores" link:

```tsx
<Link
  href="/pickem"
  className={`rounded px-3 py-1.5 text-sm font-medium transition-colors ${
    pathname?.startsWith("/pickem")
      ? "bg-crimson text-white"
      : "text-steel-gray hover:text-white"
  }`}
>
  Pick&apos;em
</Link>
```

Also add the same in the mobile menu section.

- [ ] **Step 5: Build and verify**

Run: `cd apps/web && npx next build`

- [ ] **Step 6: Commit**

```bash
git add apps/web/src/app/pickem/ apps/web/src/components/Navbar.tsx
git commit -m "feat(web): add Pick'em hub, contest detail, and leaderboard pages"
```

---

## Summary

| Task | What it builds | Key files |
|------|---------------|-----------|
| 1 | DB migration (3 tables) | `alembic/versions/XXXX_add_pickem_tables.py` |
| 2 | ORM models + schemas | `models.py`, `schemas/pickem.py` |
| 3 | Service layer (lifecycle, scoring, leaderboards, badges) | `services/pickem_service.py` |
| 4 | API router (12 endpoints) | `routers/pickem.py` |
| 5 | Integration tests | `tests/test_pickem.py` |
| 6 | Frontend components + API client | `PickemCard`, `LeaderboardTable`, `BadgeDisplay`, `api.ts` |
| 7 | Frontend pages + nav | `/pickem`, `/pickem/[id]`, `/pickem/leaderboard` |

**After all 7 tasks:** Students can browse open contests, pick game winners, submit picks, see results with correct/wrong indicators, compete on individual and school leaderboards, and earn badges. School leaderboards aggregate from user favorites. No auth required to browse or make picks on-screen — only to save and persist them.
