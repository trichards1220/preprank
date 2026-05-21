# Power Rating & Monte Carlo Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the LHSAA power rating calculator and Monte Carlo prediction engine in `packages/engine/`, wire into the FastAPI backend with simulation endpoints, and provide a CLI for manual runs.

**Architecture:** Pure-Python engine with NumPy vectorization operates on Pydantic data models — no database dependency in the engine itself. The API layer reads game/team data from PostgreSQL, converts to engine types, runs calculations, and writes results back. Monte Carlo batches all game outcomes per run as NumPy arrays for performance. The engine iteratively recalculates ratings until convergence (opponent-wins dependency).

**Tech Stack:** Python 3.12, NumPy, SciPy, Pydantic v2, FastAPI, SQLAlchemy, pytest

**Existing codebase to understand:**
- `packages/engine/pyproject.toml` — has numpy, scipy, pydantic deps (fix build-backend to `setuptools.build_meta`)
- `packages/engine/src/__init__.py` — empty placeholder
- `apps/api/app/models.py` — Sport, School, Team, Game, PowerRating ORM models
- `apps/api/app/database.py` — engine, SessionLocal, get_db
- `apps/api/app/main.py` — FastAPI app with 4 routers
- DB tables already exist: `simulations`, `projected_ratings`, `game_predictions`, `game_impact_analysis`

---

## File Structure

**Engine (pure Python, no DB dependency):**
```
packages/engine/
├── pyproject.toml              # Fix build-backend, add psycopg2-binary for CLI
├── src/
│   ├── __init__.py             # Public API exports
│   ├── types.py                # Pydantic data models: TeamRecord, GameResult, SimulationConfig, etc.
│   ├── power_rating.py         # LHSAA power rating calculator with iterative convergence
│   ├── win_probability.py      # Logistic win probability model
│   ├── monte_carlo.py          # Vectorized Monte Carlo simulation
│   ├── impact.py               # "What's At Stake" game impact analysis
│   └── cli.py                  # CLI entry point
└── tests/
    ├── __init__.py
    ├── test_power_rating.py    # 20+ unit tests for formula, edge cases, convergence
    ├── test_win_probability.py # Win probability model tests
    ├── test_monte_carlo.py     # 4-team mini-league MC tests
    ├── test_impact.py          # Impact analysis tests
    └── test_performance.py     # 298-team perf benchmark
```

**API additions:**
```
apps/api/app/
├── models.py                   # Add Simulation, ProjectedRating, GamePrediction, GameImpactAnalysis
├── schemas/
│   └── simulations.py          # SimulationOut, ProjectedRatingOut, GameImpactOut, etc.
└── routers/
    └── simulations.py          # POST /run, GET /{id}/results, game impact, team projections
```

---

### Task 1: Engine Setup + Data Types

**Files:**
- Modify: `packages/engine/pyproject.toml`
- Create: `packages/engine/src/types.py`
- Modify: `packages/engine/src/__init__.py`
- Create: `packages/engine/tests/__init__.py`
- Create: `packages/engine/tests/test_types.py`

- [ ] **Step 1: Write test for engine data types**

Create `packages/engine/tests/__init__.py` (empty).

Create `packages/engine/tests/test_types.py`:

```python
from engine.types import (
    TeamRecord, GameResult, GameStatus,
    SimulationConfig, ClassificationLevel,
)


def test_team_record_defaults():
    t = TeamRecord(team_id=1, school_name="Ruston", division="I", classification="5A")
    assert t.wins == 0
    assert t.losses == 0
    assert t.power_rating == 0.0
    assert t.games_played == 0


def test_team_record_games_played():
    t = TeamRecord(team_id=1, school_name="Ruston", division="I", classification="5A", wins=8, losses=2)
    assert t.games_played == 10


def test_game_result_construction():
    g = GameResult(
        game_id=1, home_team_id=1, away_team_id=2,
        home_score=28, away_score=14, status=GameStatus.FINAL,
    )
    assert g.home_won is True
    assert g.margin == 14


def test_game_result_away_win():
    g = GameResult(
        game_id=2, home_team_id=1, away_team_id=2,
        home_score=10, away_score=21, status=GameStatus.FINAL,
    )
    assert g.home_won is False
    assert g.margin == -11


def test_classification_level_ordering():
    assert ClassificationLevel.from_str("5A") > ClassificationLevel.from_str("3A")
    assert ClassificationLevel.from_str("1A") < ClassificationLevel.from_str("2A")
    assert ClassificationLevel.play_up_levels("3A", "5A") == 2
    assert ClassificationLevel.play_up_levels("5A", "3A") == 0


def test_simulation_config_defaults():
    cfg = SimulationConfig(sport_name="Football", season_year=2025, week_number=5)
    assert cfg.num_runs == 10000
    assert cfg.home_advantage == 0.5
    assert cfg.k_factor == 0.8
    assert cfg.playoff_spots == 8
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd packages/engine && python -m pytest tests/test_types.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'engine'`

- [ ] **Step 3: Fix pyproject.toml and implement types.py**

Replace `packages/engine/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "preprank-engine"
version = "0.1.0"
description = "PrepRank engine - power rating calculation and Monte Carlo simulations"
requires-python = ">=3.12"
dependencies = [
    "numpy>=1.26.0",
    "scipy>=1.13.0",
    "pydantic>=2.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2.0",
]
cli = [
    "psycopg2-binary>=2.9.9",
    "sqlalchemy>=2.0.30",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["engine*"]

[tool.setuptools.package-dir]
engine = "src"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Create `packages/engine/src/types.py`:

```python
"""Data types for the PrepRank engine. No database dependency."""
from __future__ import annotations

from enum import IntEnum, Enum
from pydantic import BaseModel, computed_field


class GameStatus(str, Enum):
    SCHEDULED = "scheduled"
    FINAL = "final"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"
    FORFEIT = "forfeit"


class ClassificationLevel(IntEnum):
    """Numeric ordering: 1A=1, 2A=2, 3A=3, 4A=4, 5A=5."""
    ONE_A = 1
    TWO_A = 2
    THREE_A = 3
    FOUR_A = 4
    FIVE_A = 5

    @classmethod
    def from_str(cls, s: str) -> ClassificationLevel:
        mapping = {"1A": cls.ONE_A, "2A": cls.TWO_A, "3A": cls.THREE_A, "4A": cls.FOUR_A, "5A": cls.FIVE_A}
        return mapping[s]

    @staticmethod
    def play_up_levels(my_classification: str, opponent_classification: str) -> int:
        """How many classification levels the opponent is ABOVE me. 0 if same or below."""
        my_level = ClassificationLevel.from_str(my_classification)
        opp_level = ClassificationLevel.from_str(opponent_classification)
        diff = int(opp_level) - int(my_level)
        return max(0, diff)


class TeamRecord(BaseModel):
    team_id: int
    school_name: str
    division: str
    classification: str
    wins: int = 0
    losses: int = 0
    power_rating: float = 0.0
    strength_factor: float = 0.0

    @computed_field
    @property
    def games_played(self) -> int:
        return self.wins + self.losses


class GameResult(BaseModel):
    game_id: int
    home_team_id: int
    away_team_id: int
    home_score: int | None = None
    away_score: int | None = None
    status: GameStatus = GameStatus.SCHEDULED
    is_forfeit: bool = False
    week_number: int | None = None

    @computed_field
    @property
    def home_won(self) -> bool | None:
        if self.status == GameStatus.FORFEIT:
            return self.home_score is not None and self.away_score is not None and self.home_score > self.away_score
        if self.home_score is None or self.away_score is None:
            return None
        return self.home_score > self.away_score

    @computed_field
    @property
    def margin(self) -> int | None:
        if self.home_score is None or self.away_score is None:
            return None
        return self.home_score - self.away_score


class ScheduledGame(BaseModel):
    """A future game that hasn't been played yet."""
    game_id: int
    home_team_id: int
    away_team_id: int
    week_number: int | None = None


class SimulationConfig(BaseModel):
    sport_name: str
    season_year: int
    week_number: int
    num_runs: int = 10000
    home_advantage: float = 0.5
    k_factor: float = 0.8
    playoff_spots: int = 8


class TeamProjection(BaseModel):
    team_id: int
    projected_rating_mean: float
    projected_rating_median: float
    projected_rating_p10: float
    projected_rating_p90: float
    projected_rank_mean: float
    playoff_probability: float
    championship_probability: float
    projected_wins_mean: float
    projected_losses_mean: float


class GameImpact(BaseModel):
    game_id: int
    affected_team_id: int
    rating_if_home_wins: float
    rating_if_away_wins: float
    rank_if_home_wins: int
    rank_if_away_wins: int
    playoff_prob_if_home_wins: float
    playoff_prob_if_away_wins: float
```

Replace `packages/engine/src/__init__.py`:

```python
"""PrepRank Engine - Power rating calculation and Monte Carlo simulations."""
from engine.types import (
    TeamRecord, GameResult, GameStatus, ScheduledGame,
    SimulationConfig, TeamProjection, GameImpact,
    ClassificationLevel,
)

__all__ = [
    "TeamRecord", "GameResult", "GameStatus", "ScheduledGame",
    "SimulationConfig", "TeamProjection", "GameImpact",
    "ClassificationLevel",
]
```

- [ ] **Step 4: Install engine package in dev mode and run tests**

Run:
```bash
cd packages/engine
python -m pip install -e ".[dev]"
python -m pytest tests/test_types.py -v
```
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add packages/engine/
git commit -m "feat(engine): add engine data types and project setup"
```

---

### Task 2: LHSAA Power Rating Calculator

**Files:**
- Create: `packages/engine/src/power_rating.py`
- Create: `packages/engine/tests/test_power_rating.py`

- [ ] **Step 1: Write comprehensive power rating tests**

Create `packages/engine/tests/test_power_rating.py`:

```python
"""Tests for the LHSAA power rating calculator."""
import pytest
from engine.types import TeamRecord, GameResult, GameStatus, ClassificationLevel
from engine.power_rating import (
    calculate_game_points,
    calculate_power_rating,
    calculate_strength_factor,
    calculate_all_ratings,
)


# --- calculate_game_points tests ---

def test_win_gives_10_result_points():
    """Win = 10 result points."""
    pts = calculate_game_points(
        won=True, my_classification="5A", opponent_classification="5A",
        opponent_wins=5, opponent_total_games=10,
    )
    # 10 (win) + 0 (same class) + 5.0 (5/10 * 10)
    assert pts == 15.0


def test_loss_gives_0_result_points():
    pts = calculate_game_points(
        won=False, my_classification="5A", opponent_classification="5A",
        opponent_wins=5, opponent_total_games=10,
    )
    # 0 (loss) + 0 (same class) + 5.0 (5/10 * 10)
    assert pts == 5.0


def test_play_up_bonus_one_level():
    """3A team playing 4A team gets +2 play-up points."""
    pts = calculate_game_points(
        won=True, my_classification="3A", opponent_classification="4A",
        opponent_wins=7, opponent_total_games=10,
    )
    # 10 (win) + 2 (play up 1 level) + 7.0 (7/10 * 10)
    assert pts == 19.0


def test_play_up_bonus_two_levels():
    """3A team playing 5A team gets +4 play-up points."""
    pts = calculate_game_points(
        won=True, my_classification="3A", opponent_classification="5A",
        opponent_wins=6, opponent_total_games=10,
    )
    # 10 (win) + 4 (play up 2 levels) + 6.0
    assert pts == 20.0


def test_play_down_no_bonus():
    """5A team playing 3A team gets 0 play-up points, not negative."""
    pts = calculate_game_points(
        won=True, my_classification="5A", opponent_classification="3A",
        opponent_wins=8, opponent_total_games=10,
    )
    # 10 (win) + 0 (play down) + 8.0
    assert pts == 18.0


def test_opponent_undefeated():
    pts = calculate_game_points(
        won=False, my_classification="4A", opponent_classification="4A",
        opponent_wins=10, opponent_total_games=10,
    )
    # 0 (loss) + 0 (same) + 10.0
    assert pts == 10.0


def test_opponent_winless():
    pts = calculate_game_points(
        won=True, my_classification="4A", opponent_classification="4A",
        opponent_wins=0, opponent_total_games=10,
    )
    # 10 (win) + 0 + 0.0
    assert pts == 10.0


def test_opponent_zero_games_defaults_to_zero():
    """Opponent with 0 games played gives 0 opponent-wins points."""
    pts = calculate_game_points(
        won=True, my_classification="4A", opponent_classification="4A",
        opponent_wins=0, opponent_total_games=0,
    )
    # 10 (win) + 0 + 0
    assert pts == 10.0


# --- calculate_power_rating / calculate_strength_factor ---

def test_power_rating_simple_season():
    """Team with 2 games, known points, verify average."""
    game_points = [15.0, 18.0]  # two games
    rating = calculate_power_rating(game_points)
    assert rating == pytest.approx(16.50)


def test_power_rating_rounds_to_hundredths():
    game_points = [15.0, 18.0, 12.0]
    rating = calculate_power_rating(game_points)
    assert rating == pytest.approx(15.0)


def test_power_rating_no_games():
    rating = calculate_power_rating([])
    assert rating == 0.0


def test_strength_factor_basic():
    opponent_ratings = [12.0, 14.0, 10.0]
    sf = calculate_strength_factor(opponent_ratings)
    assert sf == pytest.approx(12.0)


def test_strength_factor_no_opponents():
    sf = calculate_strength_factor([])
    assert sf == 0.0


# --- calculate_all_ratings (iterative convergence) ---

def test_calculate_all_ratings_simple_league():
    """3-team round-robin: A beats B, B beats C, C beats A."""
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
        3: TeamRecord(team_id=3, school_name="Gamma", division="I", classification="5A"),
    }
    games = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=21, away_score=14, status=GameStatus.FINAL),
        GameResult(game_id=2, home_team_id=2, away_team_id=3, home_score=28, away_score=7, status=GameStatus.FINAL),
        GameResult(game_id=3, home_team_id=3, away_team_id=1, home_score=17, away_score=10, status=GameStatus.FINAL),
    ]
    result = calculate_all_ratings(teams, games)
    # All teams 1-1, same classification => equal ratings after convergence
    # Each: 1 win (10) + 1 loss (0) + opponent-wins points converge
    assert len(result) == 3
    for t in result.values():
        assert t.wins == 1
        assert t.losses == 1
        assert t.power_rating > 0


def test_cancelled_games_excluded():
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
    }
    games = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=21, away_score=14, status=GameStatus.FINAL),
        GameResult(game_id=2, home_team_id=2, away_team_id=1, status=GameStatus.CANCELLED),
    ]
    result = calculate_all_ratings(teams, games)
    assert result[1].wins == 1
    assert result[1].losses == 0
    assert result[1].games_played == 1


def test_disputed_games_excluded():
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
    }
    games = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=21, away_score=14, status=GameStatus.DISPUTED),
    ]
    result = calculate_all_ratings(teams, games)
    assert result[1].games_played == 0
    assert result[1].power_rating == 0.0


def test_forfeit_counts_as_win_loss():
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
    }
    games = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=1, away_score=0,
                   status=GameStatus.FORFEIT, is_forfeit=True),
    ]
    result = calculate_all_ratings(teams, games)
    assert result[1].wins == 1
    assert result[2].losses == 1


def test_convergence_changes_opponent_wins():
    """When Team B wins a game, Team A's opponent-wins points should increase."""
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
        3: TeamRecord(team_id=3, school_name="Gamma", division="I", classification="5A"),
    }
    # A beat B, B beat C — B's win helps A's rating (opponent wins)
    games = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=21, away_score=14, status=GameStatus.FINAL),
        GameResult(game_id=2, home_team_id=2, away_team_id=3, home_score=28, away_score=7, status=GameStatus.FINAL),
    ]
    result = calculate_all_ratings(teams, games)
    # A played B. B is 1-1. A gets: 10 (win) + 0 (same class) + (1/2)*10 = 15.0
    assert result[1].wins == 1
    assert result[1].losses == 0
    assert result[1].power_rating == pytest.approx(15.0, abs=0.5)


def test_play_up_in_full_calculation():
    """2A team beating 5A team gets big play-up bonus."""
    teams = {
        1: TeamRecord(team_id=1, school_name="Small School", division="IV", classification="2A"),
        2: TeamRecord(team_id=2, school_name="Big School", division="I", classification="5A"),
    }
    games = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=21, away_score=14, status=GameStatus.FINAL),
    ]
    result = calculate_all_ratings(teams, games)
    # Team 1: 10 (win) + 6 (3 levels up * 2) + 0 (opp 0-1, 0/1*10=0) = 16.0
    assert result[1].power_rating == pytest.approx(16.0, abs=0.5)


def test_large_league_no_errors():
    """298-team league with random games shouldn't error."""
    import random
    random.seed(42)
    teams = {}
    classifications = ["5A", "4A", "3A", "2A", "1A"]
    divisions = ["I", "II", "III", "IV", "V"]
    for i in range(1, 299):
        idx = (i - 1) % 5
        teams[i] = TeamRecord(
            team_id=i, school_name=f"School_{i}",
            division=divisions[idx], classification=classifications[idx],
        )
    games = []
    for gid in range(1, 501):
        h, a = random.sample(range(1, 299), 2)
        games.append(GameResult(
            game_id=gid, home_team_id=h, away_team_id=a,
            home_score=random.randint(0, 50), away_score=random.randint(0, 50),
            status=GameStatus.FINAL,
        ))
    result = calculate_all_ratings(teams, games)
    assert len(result) == 298
    for t in result.values():
        assert t.power_rating >= 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd packages/engine && python -m pytest tests/test_power_rating.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'engine.power_rating'`

- [ ] **Step 3: Implement power_rating.py**

Create `packages/engine/src/power_rating.py`:

```python
"""LHSAA Power Rating Calculator.

Formula per game:
    result_points = 10 if won, 0 if lost
    play_up_points = 2 * max(0, opponent_classification_level - my_classification_level)
    opponent_wins_points = (opponent_wins / opponent_total_games) * 10  (0 if opponent has 0 games)
    game_points = result_points + play_up_points + opponent_wins_points

Season power rating = sum(game_points) / games_played, rounded to 2 decimals.
Strength factor = sum(opponent_power_ratings) / games_played.

Iterative recalculation: opponent_wins change as other results are factored in,
so we iterate until ratings converge (delta < 0.001 across all teams).
"""
from __future__ import annotations

from engine.types import TeamRecord, GameResult, GameStatus, ClassificationLevel


def calculate_game_points(
    won: bool,
    my_classification: str,
    opponent_classification: str,
    opponent_wins: int,
    opponent_total_games: int,
) -> float:
    """Calculate points earned from a single game."""
    result_points = 10.0 if won else 0.0
    play_up_points = 2.0 * ClassificationLevel.play_up_levels(my_classification, opponent_classification)
    if opponent_total_games > 0:
        opponent_wins_points = (opponent_wins / opponent_total_games) * 10.0
    else:
        opponent_wins_points = 0.0
    return result_points + play_up_points + opponent_wins_points


def calculate_power_rating(game_points: list[float]) -> float:
    """Average of all game points, rounded to hundredths. Returns 0.0 if no games."""
    if not game_points:
        return 0.0
    return round(sum(game_points) / len(game_points), 2)


def calculate_strength_factor(opponent_ratings: list[float]) -> float:
    """Average of all opponents' power ratings. Returns 0.0 if no opponents."""
    if not opponent_ratings:
        return 0.0
    return round(sum(opponent_ratings) / len(opponent_ratings), 2)


def _eligible_games(games: list[GameResult]) -> list[GameResult]:
    """Filter to games that count toward ratings (exclude cancelled/disputed)."""
    return [g for g in games if g.status in (GameStatus.FINAL, GameStatus.FORFEIT)]


def _build_team_games(
    games: list[GameResult],
) -> dict[int, list[tuple[bool, int]]]:
    """Map team_id -> list of (won, opponent_team_id) from eligible games."""
    team_games: dict[int, list[tuple[bool, int]]] = {}
    for g in games:
        if g.home_won is None:
            continue
        team_games.setdefault(g.home_team_id, []).append((g.home_won, g.away_team_id))
        team_games.setdefault(g.away_team_id, []).append((not g.home_won, g.home_team_id))
    return team_games


def calculate_all_ratings(
    teams: dict[int, TeamRecord],
    games: list[GameResult],
    max_iterations: int = 50,
    tolerance: float = 0.001,
) -> dict[int, TeamRecord]:
    """Calculate power ratings for all teams with iterative convergence.

    Returns a new dict of TeamRecord with updated wins, losses, power_rating, strength_factor.
    """
    eligible = _eligible_games(games)
    team_games = _build_team_games(eligible)

    # Initialize win/loss records
    updated: dict[int, TeamRecord] = {}
    for tid, t in teams.items():
        wins = sum(1 for won, _ in team_games.get(tid, []) if won)
        losses = sum(1 for won, _ in team_games.get(tid, []) if not won)
        updated[tid] = t.model_copy(update={"wins": wins, "losses": losses, "power_rating": 0.0, "strength_factor": 0.0})

    # Iterative convergence
    for _ in range(max_iterations):
        max_delta = 0.0
        new_ratings: dict[int, float] = {}

        for tid in teams:
            my_games = team_games.get(tid, [])
            if not my_games:
                new_ratings[tid] = 0.0
                continue

            my_class = updated[tid].classification
            game_pts: list[float] = []
            opponent_ratings: list[float] = []

            for won, opp_id in my_games:
                opp = updated.get(opp_id)
                if opp is None:
                    # Out-of-state opponent not in our team dict — use record only
                    opp_wins = 0
                    opp_total = 0
                    opp_class = my_class  # Assume same classification for unknown
                    opp_rating = 0.0
                else:
                    opp_wins = opp.wins
                    opp_total = opp.games_played
                    opp_class = opp.classification
                    opp_rating = opp.power_rating

                pts = calculate_game_points(won, my_class, opp_class, opp_wins, opp_total)
                game_pts.append(pts)
                opponent_ratings.append(opp_rating)

            new_ratings[tid] = calculate_power_rating(game_pts)
            updated[tid] = updated[tid].model_copy(update={
                "power_rating": new_ratings[tid],
                "strength_factor": calculate_strength_factor(opponent_ratings),
            })

        # Check convergence
        for tid in teams:
            old_rating = teams[tid].power_rating if _ == 0 else prev_ratings.get(tid, 0.0)
            delta = abs(new_ratings.get(tid, 0.0) - old_rating)
            max_delta = max(max_delta, delta)

        prev_ratings = dict(new_ratings)
        if _ > 0 and max_delta < tolerance:
            break

    return updated
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd packages/engine && python -m pytest tests/test_power_rating.py -v`
Expected: ALL PASS (20+ tests)

- [ ] **Step 5: Commit**

```bash
git add packages/engine/src/power_rating.py packages/engine/tests/test_power_rating.py
git commit -m "feat(engine): implement LHSAA power rating calculator with iterative convergence"
```

---

### Task 3: Win Probability Model

**Files:**
- Create: `packages/engine/src/win_probability.py`
- Create: `packages/engine/tests/test_win_probability.py`

- [ ] **Step 1: Write tests for win probability**

Create `packages/engine/tests/test_win_probability.py`:

```python
import pytest
import numpy as np
from engine.win_probability import win_probability, win_probability_batch


def test_equal_teams_home_advantage():
    """Equal teams: home team slightly favored due to home advantage."""
    p = win_probability(home_rating=10.0, away_rating=10.0, home_advantage=0.5, k=0.8)
    assert 0.5 < p < 0.7  # slight home edge


def test_equal_teams_no_home_advantage():
    p = win_probability(home_rating=10.0, away_rating=10.0, home_advantage=0.0, k=0.8)
    assert p == pytest.approx(0.5, abs=0.01)


def test_much_better_home_team():
    p = win_probability(home_rating=15.0, away_rating=8.0, home_advantage=0.5, k=0.8)
    assert p > 0.95


def test_much_better_away_team():
    p = win_probability(home_rating=8.0, away_rating=15.0, home_advantage=0.5, k=0.8)
    assert p < 0.05


def test_probability_bounded_0_1():
    p1 = win_probability(home_rating=100.0, away_rating=0.0, home_advantage=0.5, k=0.8)
    p2 = win_probability(home_rating=0.0, away_rating=100.0, home_advantage=0.5, k=0.8)
    assert 0.0 < p1 <= 1.0
    assert 0.0 <= p2 < 1.0


def test_symmetry():
    """P(A beats B at home) + P(B beats A at B's home) should be close to 1 for equal venues."""
    p1 = win_probability(home_rating=12.0, away_rating=10.0, home_advantage=0.0, k=0.8)
    p2 = win_probability(home_rating=10.0, away_rating=12.0, home_advantage=0.0, k=0.8)
    assert p1 + p2 == pytest.approx(1.0, abs=0.01)


def test_batch_matches_scalar():
    home = np.array([10.0, 12.0, 8.0])
    away = np.array([10.0, 10.0, 15.0])
    batch = win_probability_batch(home, away, home_advantage=0.5, k=0.8)
    for i in range(3):
        scalar = win_probability(home[i], away[i], home_advantage=0.5, k=0.8)
        assert batch[i] == pytest.approx(scalar, abs=1e-10)


def test_batch_returns_numpy_array():
    home = np.array([10.0, 12.0])
    away = np.array([10.0, 10.0])
    result = win_probability_batch(home, away, home_advantage=0.5, k=0.8)
    assert isinstance(result, np.ndarray)
    assert result.shape == (2,)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd packages/engine && python -m pytest tests/test_win_probability.py -v`
Expected: FAIL

- [ ] **Step 3: Implement win_probability.py**

Create `packages/engine/src/win_probability.py`:

```python
"""Logistic win probability model.

P(home_win) = 1 / (1 + exp(-k * (home_rating - away_rating + home_advantage)))
"""
from __future__ import annotations

import numpy as np


def win_probability(
    home_rating: float,
    away_rating: float,
    home_advantage: float = 0.5,
    k: float = 0.8,
) -> float:
    """Scalar win probability for home team."""
    exponent = -k * (home_rating - away_rating + home_advantage)
    return 1.0 / (1.0 + np.exp(exponent))


def win_probability_batch(
    home_ratings: np.ndarray,
    away_ratings: np.ndarray,
    home_advantage: float = 0.5,
    k: float = 0.8,
) -> np.ndarray:
    """Vectorized win probability for arrays of matchups."""
    exponent = -k * (home_ratings - away_ratings + home_advantage)
    return 1.0 / (1.0 + np.exp(exponent))
```

- [ ] **Step 4: Run tests**

Run: `cd packages/engine && python -m pytest tests/test_win_probability.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add packages/engine/src/win_probability.py packages/engine/tests/test_win_probability.py
git commit -m "feat(engine): add logistic win probability model with batch support"
```

---

### Task 4: Monte Carlo Simulation Core

**Files:**
- Create: `packages/engine/src/monte_carlo.py`
- Create: `packages/engine/tests/test_monte_carlo.py`

- [ ] **Step 1: Write Monte Carlo tests**

Create `packages/engine/tests/test_monte_carlo.py`:

```python
"""Tests for Monte Carlo simulation with a 4-team mini-league."""
import pytest
import numpy as np
from engine.types import (
    TeamRecord, GameResult, GameStatus,
    ScheduledGame, SimulationConfig, TeamProjection,
)
from engine.monte_carlo import run_simulation


def _make_4_team_league():
    """4 teams in same division, 3 games played, 3 remaining."""
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
        3: TeamRecord(team_id=3, school_name="Gamma", division="I", classification="5A"),
        4: TeamRecord(team_id=4, school_name="Delta", division="I", classification="5A"),
    }
    played = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=28, away_score=14, status=GameStatus.FINAL),
        GameResult(game_id=2, home_team_id=3, away_team_id=4, home_score=21, away_score=7, status=GameStatus.FINAL),
        GameResult(game_id=3, home_team_id=1, away_team_id=3, home_score=17, away_score=10, status=GameStatus.FINAL),
    ]
    remaining = [
        ScheduledGame(game_id=4, home_team_id=2, away_team_id=3),
        ScheduledGame(game_id=5, home_team_id=4, away_team_id=1),
        ScheduledGame(game_id=6, home_team_id=2, away_team_id=4),
    ]
    config = SimulationConfig(
        sport_name="Football", season_year=2025, week_number=3,
        num_runs=1000, playoff_spots=2,
    )
    return teams, played, remaining, config


def test_simulation_returns_projections_for_all_teams():
    teams, played, remaining, config = _make_4_team_league()
    projections = run_simulation(teams, played, remaining, config)
    assert len(projections) == 4
    assert all(isinstance(p, TeamProjection) for p in projections.values())


def test_probabilities_between_0_and_100():
    teams, played, remaining, config = _make_4_team_league()
    projections = run_simulation(teams, played, remaining, config)
    for p in projections.values():
        assert 0.0 <= p.playoff_probability <= 100.0
        assert 0.0 <= p.championship_probability <= 100.0


def test_playoff_probabilities_reasonable():
    """Team 1 (2-0) should have higher playoff prob than Team 4 (0-1)."""
    teams, played, remaining, config = _make_4_team_league()
    projections = run_simulation(teams, played, remaining, config)
    assert projections[1].playoff_probability > projections[4].playoff_probability


def test_projected_wins_plus_losses_equals_total_games():
    teams, played, remaining, config = _make_4_team_league()
    projections = run_simulation(teams, played, remaining, config)
    for tid, p in projections.items():
        # Each team plays some subset of the 6 total games
        total = p.projected_wins_mean + p.projected_losses_mean
        assert total > 0


def test_rating_percentiles_ordered():
    teams, played, remaining, config = _make_4_team_league()
    projections = run_simulation(teams, played, remaining, config)
    for p in projections.values():
        assert p.projected_rating_p10 <= p.projected_rating_median <= p.projected_rating_p90


def test_deterministic_with_seed():
    """Same seed should give same results."""
    teams, played, remaining, config = _make_4_team_league()
    p1 = run_simulation(teams, played, remaining, config, seed=42)
    p2 = run_simulation(teams, played, remaining, config, seed=42)
    for tid in teams:
        assert p1[tid].projected_rating_mean == pytest.approx(p2[tid].projected_rating_mean, abs=0.01)


def test_no_remaining_games():
    """If no games remain, projections should match current ratings."""
    teams, played, _, config = _make_4_team_league()
    projections = run_simulation(teams, played, [], config)
    # With no remaining games, variance should be near zero
    for p in projections.values():
        assert abs(p.projected_rating_p90 - p.projected_rating_p10) < 1.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd packages/engine && python -m pytest tests/test_monte_carlo.py -v`
Expected: FAIL

- [ ] **Step 3: Implement monte_carlo.py**

Create `packages/engine/src/monte_carlo.py`:

```python
"""Monte Carlo simulation engine using NumPy vectorization.

For each simulation run:
1. Flip weighted coins for all remaining games (vectorized)
2. Recalculate power ratings for all teams
3. Rank teams within division
4. Determine playoff qualifiers

Aggregate across all runs for projections.
"""
from __future__ import annotations

import numpy as np

from engine.types import (
    TeamRecord, GameResult, GameStatus,
    ScheduledGame, SimulationConfig, TeamProjection,
)
from engine.power_rating import calculate_all_ratings
from engine.win_probability import win_probability_batch


def run_simulation(
    teams: dict[int, TeamRecord],
    played_games: list[GameResult],
    remaining_games: list[ScheduledGame],
    config: SimulationConfig,
    seed: int | None = None,
) -> dict[int, TeamProjection]:
    """Run Monte Carlo simulation and return projections for all teams."""
    rng = np.random.default_rng(seed)
    num_runs = config.num_runs
    num_remaining = len(remaining_games)
    team_ids = sorted(teams.keys())
    tid_to_idx = {tid: i for i, tid in enumerate(team_ids)}
    num_teams = len(team_ids)

    # Pre-compute current ratings for win probability
    current = calculate_all_ratings(teams, played_games)

    if num_remaining == 0:
        # No remaining games — return current state as projection
        return _projections_from_single_state(current, team_ids, config)

    # Build arrays for remaining games
    home_ids = np.array([g.home_team_id for g in remaining_games])
    away_ids = np.array([g.away_team_id for g in remaining_games])
    home_ratings = np.array([current[g.home_team_id].power_rating for g in remaining_games])
    away_ratings = np.array([current[g.away_team_id].power_rating for g in remaining_games])

    # Win probabilities for all remaining games
    probs = win_probability_batch(home_ratings, away_ratings, config.home_advantage, config.k_factor)

    # Storage for per-run results
    all_ratings = np.zeros((num_runs, num_teams))
    all_wins = np.zeros((num_runs, num_teams))
    all_losses = np.zeros((num_runs, num_teams))
    all_ranks = np.zeros((num_runs, num_teams))

    # Simulate
    # Generate all random outcomes at once: (num_runs, num_remaining)
    random_draws = rng.random((num_runs, num_remaining))
    home_wins_matrix = random_draws < probs  # broadcast probs across runs

    for run_idx in range(num_runs):
        # Build game results for this run
        sim_games = list(played_games)  # start with actual results
        for g_idx, game in enumerate(remaining_games):
            home_won = bool(home_wins_matrix[run_idx, g_idx])
            sim_games.append(GameResult(
                game_id=game.game_id,
                home_team_id=game.home_team_id,
                away_team_id=game.away_team_id,
                home_score=1 if home_won else 0,
                away_score=0 if home_won else 1,
                status=GameStatus.FINAL,
            ))

        # Calculate ratings for this simulated season
        sim_result = calculate_all_ratings(teams, sim_games, max_iterations=10, tolerance=0.01)

        # Extract per-team results
        for tid in team_ids:
            idx = tid_to_idx[tid]
            t = sim_result[tid]
            all_ratings[run_idx, idx] = t.power_rating
            all_wins[run_idx, idx] = t.wins
            all_losses[run_idx, idx] = t.losses

        # Rank within division
        _rank_by_division(sim_result, team_ids, tid_to_idx, all_ranks, run_idx)

    # Aggregate projections
    return _aggregate_projections(
        team_ids, tid_to_idx, all_ratings, all_wins, all_losses, all_ranks,
        config, num_runs, teams,
    )


def _rank_by_division(
    sim_result: dict[int, TeamRecord],
    team_ids: list[int],
    tid_to_idx: dict[int, int],
    all_ranks: np.ndarray,
    run_idx: int,
) -> None:
    """Rank teams within their division by power rating (descending)."""
    divisions: dict[str, list[tuple[int, float]]] = {}
    for tid in team_ids:
        t = sim_result[tid]
        divisions.setdefault(t.division, []).append((tid, t.power_rating))

    for div_teams in divisions.values():
        sorted_teams = sorted(div_teams, key=lambda x: -x[1])
        for rank, (tid, _) in enumerate(sorted_teams, 1):
            all_ranks[run_idx, tid_to_idx[tid]] = rank


def _aggregate_projections(
    team_ids: list[int],
    tid_to_idx: dict[int, int],
    all_ratings: np.ndarray,
    all_wins: np.ndarray,
    all_losses: np.ndarray,
    all_ranks: np.ndarray,
    config: SimulationConfig,
    num_runs: int,
    teams: dict[int, TeamRecord],
) -> dict[int, TeamProjection]:
    """Aggregate simulation runs into TeamProjection objects."""
    projections: dict[int, TeamProjection] = {}

    # Group teams by division for playoff calculation
    div_teams: dict[str, list[int]] = {}
    for tid in team_ids:
        div_teams.setdefault(teams[tid].division, []).append(tid)

    for tid in team_ids:
        idx = tid_to_idx[tid]
        ratings = all_ratings[:, idx]
        wins = all_wins[:, idx]
        losses = all_losses[:, idx]
        ranks = all_ranks[:, idx]

        playoff_count = np.sum(ranks <= config.playoff_spots)
        champ_count = np.sum(ranks == 1)

        projections[tid] = TeamProjection(
            team_id=tid,
            projected_rating_mean=round(float(np.mean(ratings)), 2),
            projected_rating_median=round(float(np.median(ratings)), 2),
            projected_rating_p10=round(float(np.percentile(ratings, 10)), 2),
            projected_rating_p90=round(float(np.percentile(ratings, 90)), 2),
            projected_rank_mean=round(float(np.mean(ranks)), 1),
            playoff_probability=round(float(playoff_count / num_runs * 100), 2),
            championship_probability=round(float(champ_count / num_runs * 100), 2),
            projected_wins_mean=round(float(np.mean(wins)), 1),
            projected_losses_mean=round(float(np.mean(losses)), 1),
        )

    return projections


def _projections_from_single_state(
    current: dict[int, TeamRecord],
    team_ids: list[int],
    config: SimulationConfig,
) -> dict[int, TeamProjection]:
    """When no remaining games, return deterministic projections."""
    # Rank within division
    divisions: dict[str, list[tuple[int, float]]] = {}
    for tid in team_ids:
        t = current[tid]
        divisions.setdefault(t.division, []).append((tid, t.power_rating))

    ranks: dict[int, int] = {}
    for div_teams in divisions.values():
        sorted_teams = sorted(div_teams, key=lambda x: -x[1])
        for rank, (tid, _) in enumerate(sorted_teams, 1):
            ranks[tid] = rank

    projections: dict[int, TeamProjection] = {}
    for tid in team_ids:
        t = current[tid]
        rank = ranks[tid]
        projections[tid] = TeamProjection(
            team_id=tid,
            projected_rating_mean=t.power_rating,
            projected_rating_median=t.power_rating,
            projected_rating_p10=t.power_rating,
            projected_rating_p90=t.power_rating,
            projected_rank_mean=float(rank),
            playoff_probability=100.0 if rank <= config.playoff_spots else 0.0,
            championship_probability=100.0 if rank == 1 else 0.0,
            projected_wins_mean=float(t.wins),
            projected_losses_mean=float(t.losses),
        )
    return projections
```

- [ ] **Step 4: Run tests**

Run: `cd packages/engine && python -m pytest tests/test_monte_carlo.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add packages/engine/src/monte_carlo.py packages/engine/tests/test_monte_carlo.py
git commit -m "feat(engine): add vectorized Monte Carlo simulation engine"
```

---

### Task 5: "What's At Stake" Impact Analysis

**Files:**
- Create: `packages/engine/src/impact.py`
- Create: `packages/engine/tests/test_impact.py`

- [ ] **Step 1: Write impact analysis tests**

Create `packages/engine/tests/test_impact.py`:

```python
"""Tests for game impact analysis."""
import pytest
from engine.types import (
    TeamRecord, GameResult, GameStatus,
    ScheduledGame, SimulationConfig, GameImpact,
)
from engine.impact import analyze_game_impact


def _make_4_team_league():
    teams = {
        1: TeamRecord(team_id=1, school_name="Alpha", division="I", classification="5A"),
        2: TeamRecord(team_id=2, school_name="Beta", division="I", classification="5A"),
        3: TeamRecord(team_id=3, school_name="Gamma", division="I", classification="5A"),
        4: TeamRecord(team_id=4, school_name="Delta", division="I", classification="5A"),
    }
    played = [
        GameResult(game_id=1, home_team_id=1, away_team_id=2, home_score=28, away_score=14, status=GameStatus.FINAL),
        GameResult(game_id=2, home_team_id=3, away_team_id=4, home_score=21, away_score=7, status=GameStatus.FINAL),
    ]
    remaining = [
        ScheduledGame(game_id=3, home_team_id=1, away_team_id=3),
        ScheduledGame(game_id=4, home_team_id=2, away_team_id=4),
    ]
    config = SimulationConfig(
        sport_name="Football", season_year=2025, week_number=2,
        num_runs=500, playoff_spots=2,
    )
    return teams, played, remaining, config


def test_impact_returns_all_division_teams():
    teams, played, remaining, config = _make_4_team_league()
    target_game = remaining[0]  # game_id=3, team 1 vs team 3
    impacts = analyze_game_impact(teams, played, remaining, target_game, config, seed=42)
    # All 4 teams are in division I, so all should have impact entries
    assert len(impacts) == 4
    assert all(isinstance(imp, GameImpact) for imp in impacts)


def test_impact_game_id_matches():
    teams, played, remaining, config = _make_4_team_league()
    target_game = remaining[0]
    impacts = analyze_game_impact(teams, played, remaining, target_game, config, seed=42)
    for imp in impacts:
        assert imp.game_id == target_game.game_id


def test_impact_shows_different_outcomes():
    """The two scenarios (home win vs away win) should produce different ratings."""
    teams, played, remaining, config = _make_4_team_league()
    target_game = remaining[0]  # team 1 (1-0) vs team 3 (1-0)
    impacts = analyze_game_impact(teams, played, remaining, target_game, config, seed=42)
    # For team 1: winning should give higher rating than losing
    team1_impact = next(i for i in impacts if i.affected_team_id == 1)
    assert team1_impact.rating_if_home_wins >= team1_impact.rating_if_away_wins


def test_impact_ripple_effects():
    """Team 2 and 4 should also be affected by Team 1 vs Team 3 outcome."""
    teams, played, remaining, config = _make_4_team_league()
    target_game = remaining[0]
    impacts = analyze_game_impact(teams, played, remaining, target_game, config, seed=42)
    # Team 2 beat Team 1 — if Team 1 wins more, Team 2's opponent-strength improves
    team2_impact = next(i for i in impacts if i.affected_team_id == 2)
    # Both scenarios should have valid values
    assert team2_impact.rating_if_home_wins > 0
    assert team2_impact.rating_if_away_wins > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd packages/engine && python -m pytest tests/test_impact.py -v`
Expected: FAIL

- [ ] **Step 3: Implement impact.py**

Create `packages/engine/src/impact.py`:

```python
"""'What's At Stake' game impact analysis.

For a target game, run two simulation scenarios:
1. Lock home team winning, simulate rest normally
2. Lock away team winning, simulate rest normally

Compare projections across both scenarios for every affected team.
"""
from __future__ import annotations

from engine.types import (
    TeamRecord, GameResult, GameStatus,
    ScheduledGame, SimulationConfig, GameImpact,
)
from engine.monte_carlo import run_simulation


def analyze_game_impact(
    teams: dict[int, TeamRecord],
    played_games: list[GameResult],
    remaining_games: list[ScheduledGame],
    target_game: ScheduledGame,
    config: SimulationConfig,
    seed: int | None = None,
) -> list[GameImpact]:
    """Analyze how a specific game's outcome affects all teams in the same divisions."""
    # Remove target game from remaining
    other_remaining = [g for g in remaining_games if g.game_id != target_game.game_id]

    # Scenario 1: Home team wins
    home_win_result = GameResult(
        game_id=target_game.game_id,
        home_team_id=target_game.home_team_id,
        away_team_id=target_game.away_team_id,
        home_score=1, away_score=0, status=GameStatus.FINAL,
    )
    played_home_wins = played_games + [home_win_result]
    proj_home = run_simulation(teams, played_home_wins, other_remaining, config, seed=seed)

    # Scenario 2: Away team wins
    away_win_result = GameResult(
        game_id=target_game.game_id,
        home_team_id=target_game.home_team_id,
        away_team_id=target_game.away_team_id,
        home_score=0, away_score=1, status=GameStatus.FINAL,
    )
    played_away_wins = played_games + [away_win_result]
    proj_away = run_simulation(teams, played_away_wins, other_remaining, config, seed=seed)

    # Find affected teams (same division as either participant)
    home_div = teams[target_game.home_team_id].division
    away_div = teams[target_game.away_team_id].division
    affected_divs = {home_div, away_div}
    affected_ids = [tid for tid, t in teams.items() if t.division in affected_divs]

    impacts: list[GameImpact] = []
    for tid in affected_ids:
        ph = proj_home[tid]
        pa = proj_away[tid]
        impacts.append(GameImpact(
            game_id=target_game.game_id,
            affected_team_id=tid,
            rating_if_home_wins=ph.projected_rating_mean,
            rating_if_away_wins=pa.projected_rating_mean,
            rank_if_home_wins=round(ph.projected_rank_mean),
            rank_if_away_wins=round(pa.projected_rank_mean),
            playoff_prob_if_home_wins=ph.playoff_probability,
            playoff_prob_if_away_wins=pa.playoff_probability,
        ))

    return impacts
```

- [ ] **Step 4: Run tests**

Run: `cd packages/engine && python -m pytest tests/test_impact.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add packages/engine/src/impact.py packages/engine/tests/test_impact.py
git commit -m "feat(engine): add 'What's At Stake' game impact analysis"
```

---

### Task 6: Performance Test

**Files:**
- Create: `packages/engine/tests/test_performance.py`

- [ ] **Step 1: Write performance benchmark test**

Create `packages/engine/tests/test_performance.py`:

```python
"""Performance tests for the Monte Carlo engine."""
import time
import random
import pytest
from engine.types import (
    TeamRecord, GameResult, GameStatus,
    ScheduledGame, SimulationConfig,
)
from engine.monte_carlo import run_simulation


def _build_298_team_league(num_played=400, num_remaining=400, seed=42):
    """Build a realistic 298-team football league."""
    rng = random.Random(seed)
    classifications = ["5A", "4A", "3A", "2A"]
    divisions = ["I", "II", "III", "IV"]

    teams = {}
    for i in range(1, 299):
        idx = (i - 1) % 4
        teams[i] = TeamRecord(
            team_id=i, school_name=f"School_{i}",
            division=divisions[idx], classification=classifications[idx],
        )

    played = []
    for gid in range(1, num_played + 1):
        h, a = rng.sample(range(1, 299), 2)
        played.append(GameResult(
            game_id=gid, home_team_id=h, away_team_id=a,
            home_score=rng.randint(0, 50), away_score=rng.randint(0, 50),
            status=GameStatus.FINAL,
        ))

    remaining = []
    for gid in range(num_played + 1, num_played + num_remaining + 1):
        h, a = rng.sample(range(1, 299), 2)
        remaining.append(ScheduledGame(game_id=gid, home_team_id=h, away_team_id=a))

    return teams, played, remaining


def test_298_team_simulation_under_60_seconds():
    """Full 298-team football simulation with 10,000 runs must complete in < 60s."""
    teams, played, remaining = _build_298_team_league(num_played=400, num_remaining=400)
    config = SimulationConfig(
        sport_name="Football", season_year=2025, week_number=5,
        num_runs=10000, playoff_spots=8,
    )
    start = time.time()
    projections = run_simulation(teams, played, remaining, config, seed=42)
    elapsed = time.time() - start

    assert len(projections) == 298
    assert elapsed < 60.0, f"Simulation took {elapsed:.1f}s, must be under 60s"


def test_small_simulation_fast():
    """20-team, 1000 runs should be very fast."""
    teams, played, remaining = _build_298_team_league(num_played=30, num_remaining=30)
    # Use only first 20 teams
    small_teams = {k: v for k, v in teams.items() if k <= 20}
    small_played = [g for g in played if g.home_team_id <= 20 and g.away_team_id <= 20]
    small_remaining = [g for g in remaining if g.home_team_id <= 20 and g.away_team_id <= 20]

    config = SimulationConfig(
        sport_name="Football", season_year=2025, week_number=5,
        num_runs=1000, playoff_spots=4,
    )
    start = time.time()
    projections = run_simulation(small_teams, small_played, small_remaining, config, seed=42)
    elapsed = time.time() - start

    assert elapsed < 10.0
```

- [ ] **Step 2: Run performance test**

Run: `cd packages/engine && python -m pytest tests/test_performance.py -v -s`
Expected: PASS (note actual timing in output)

If the 298-team test exceeds 60s, the Monte Carlo loop needs optimization. The most likely bottleneck is `calculate_all_ratings` being called 10,000 times. Reduce `max_iterations` to 5 and `tolerance` to 0.05 in the simulation path, or cache intermediate results.

- [ ] **Step 3: Commit**

```bash
git add packages/engine/tests/test_performance.py
git commit -m "test(engine): add performance benchmarks for 298-team simulation"
```

---

### Task 7: Engine CLI

**Files:**
- Create: `packages/engine/src/cli.py`

- [ ] **Step 1: Implement CLI**

Create `packages/engine/src/cli.py`:

```python
"""CLI for running PrepRank simulations.

Usage:
    python -m engine.cli simulate --sport football --season 2025 --week 5
    python -m engine.cli ratings --sport football --season 2025 --week 11
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import psycopg2
from engine.types import (
    TeamRecord, GameResult, GameStatus,
    ScheduledGame, SimulationConfig,
)
from engine.power_rating import calculate_all_ratings
from engine.monte_carlo import run_simulation

DIVISION_TO_CLASSIFICATION = {"I": "5A", "II": "4A", "III": "3A", "IV": "2A", "V": "1A"}


def get_db_url() -> str:
    return os.environ.get("DATABASE_URL", "postgresql://preprank:preprank@127.0.0.1:5432/preprank")


def load_teams(cur, sport_name: str, season_year: int) -> dict[int, TeamRecord]:
    cur.execute("""
        SELECT t.id, s.name, t.division, s.classification
        FROM teams t JOIN schools s ON t.school_id = s.id
        JOIN sports sp ON t.sport_id = sp.id
        WHERE sp.name = %s AND t.season_year = %s
    """, (sport_name, season_year))
    teams = {}
    for row in cur.fetchall():
        tid, name, div, cls = row
        if cls is None:
            cls = DIVISION_TO_CLASSIFICATION.get(div, "5A")
        teams[tid] = TeamRecord(team_id=tid, school_name=name, division=div, classification=cls)
    return teams


def load_played_games(cur, sport_name: str, season_year: int, up_to_week: int | None = None) -> list[GameResult]:
    sql = """
        SELECT g.id, g.home_team_id, g.away_team_id, g.home_score, g.away_score,
               g.status, g.week_number
        FROM games g JOIN sports sp ON g.sport_id = sp.id
        WHERE sp.name = %s AND g.season_year = %s AND g.status IN ('final', 'forfeit')
    """
    params: list = [sport_name, season_year]
    if up_to_week is not None:
        sql += " AND g.week_number <= %s"
        params.append(up_to_week)
    cur.execute(sql, params)
    games = []
    for row in cur.fetchall():
        gid, h, a, hs, as_, status, wk = row
        games.append(GameResult(
            game_id=gid, home_team_id=h, away_team_id=a,
            home_score=hs, away_score=as_,
            status=GameStatus(status),
            is_forfeit=(status == "forfeit"),
            week_number=wk,
        ))
    return games


def load_remaining_games(cur, sport_name: str, season_year: int, after_week: int) -> list[ScheduledGame]:
    cur.execute("""
        SELECT g.id, g.home_team_id, g.away_team_id, g.week_number
        FROM games g JOIN sports sp ON g.sport_id = sp.id
        WHERE sp.name = %s AND g.season_year = %s AND g.status = 'scheduled'
          AND g.week_number > %s
    """, (sport_name, season_year, after_week))
    return [
        ScheduledGame(game_id=r[0], home_team_id=r[1], away_team_id=r[2], week_number=r[3])
        for r in cur.fetchall()
    ]


def cmd_ratings(args):
    conn = psycopg2.connect(get_db_url())
    cur = conn.cursor()
    try:
        teams = load_teams(cur, args.sport.title(), args.season)
        games = load_played_games(cur, args.sport.title(), args.season, args.week)
        print(f"Loaded {len(teams)} teams, {len(games)} games")

        result = calculate_all_ratings(teams, games)
        # Sort by division then rating
        by_div: dict[str, list] = {}
        for t in result.values():
            by_div.setdefault(t.division, []).append(t)
        for div in sorted(by_div):
            print(f"\n=== Division {div} ===")
            ranked = sorted(by_div[div], key=lambda x: -x.power_rating)
            for i, t in enumerate(ranked, 1):
                print(f"  {i:>3}. {t.school_name:<30} {t.power_rating:>6.2f}  (SoS: {t.strength_factor:.2f})")
    finally:
        conn.close()


def cmd_simulate(args):
    conn = psycopg2.connect(get_db_url())
    cur = conn.cursor()
    try:
        sport = args.sport.title()
        teams = load_teams(cur, sport, args.season)
        played = load_played_games(cur, sport, args.season, args.week)
        remaining = load_remaining_games(cur, sport, args.season, args.week)
        print(f"Loaded {len(teams)} teams, {len(played)} played, {len(remaining)} remaining")

        config = SimulationConfig(
            sport_name=sport, season_year=args.season, week_number=args.week,
            num_runs=args.runs, playoff_spots=args.playoff_spots,
        )
        print(f"Running {config.num_runs} simulations...")
        start = time.time()
        projections = run_simulation(teams, played, remaining, config)
        elapsed = time.time() - start
        print(f"Completed in {elapsed:.1f}s\n")

        # Display by division
        by_div: dict[str, list] = {}
        for tid, proj in projections.items():
            div = teams[tid].division
            by_div.setdefault(div, []).append((teams[tid], proj))
        for div in sorted(by_div):
            print(f"=== Division {div} ===")
            ranked = sorted(by_div[div], key=lambda x: -x[1].projected_rating_mean)
            for i, (t, p) in enumerate(ranked, 1):
                print(f"  {i:>3}. {t.school_name:<25} "
                      f"Rating: {p.projected_rating_mean:>6.2f} "
                      f"[{p.projected_rating_p10:.1f}-{p.projected_rating_p90:.1f}]  "
                      f"Playoff: {p.playoff_probability:>5.1f}%  "
                      f"W-L: {p.projected_wins_mean:.1f}-{p.projected_losses_mean:.1f}")
            print()
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(prog="engine", description="PrepRank Engine CLI")
    sub = parser.add_subparsers(dest="command")

    p_rate = sub.add_parser("ratings", help="Calculate power ratings")
    p_rate.add_argument("--sport", required=True)
    p_rate.add_argument("--season", type=int, required=True)
    p_rate.add_argument("--week", type=int, default=None)

    p_sim = sub.add_parser("simulate", help="Run Monte Carlo simulation")
    p_sim.add_argument("--sport", required=True)
    p_sim.add_argument("--season", type=int, required=True)
    p_sim.add_argument("--week", type=int, required=True)
    p_sim.add_argument("--runs", type=int, default=10000)
    p_sim.add_argument("--playoff-spots", type=int, default=8)

    args = parser.parse_args()
    if args.command == "ratings":
        cmd_ratings(args)
    elif args.command == "simulate":
        cmd_simulate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

Also create `packages/engine/src/__main__.py`:

```python
from engine.cli import main

main()
```

- [ ] **Step 2: Test CLI loads**

Run: `cd packages/engine && python -m engine --help`
Expected: Shows help text with `ratings` and `simulate` subcommands

- [ ] **Step 3: Commit**

```bash
git add packages/engine/src/cli.py packages/engine/src/__main__.py
git commit -m "feat(engine): add CLI for power ratings and Monte Carlo simulation"
```

---

### Task 8: API Models + Schemas for Simulation Tables

**Files:**
- Modify: `apps/api/app/models.py`
- Create: `apps/api/app/schemas/simulations.py`
- Modify: `apps/api/app/schemas/__init__.py`

- [ ] **Step 1: Add ORM models for simulation tables**

Add to the end of `apps/api/app/models.py`:

```python
class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True)
    sport_id = Column(Integer, ForeignKey("sports.id"))
    season_year = Column(Integer, nullable=False)
    week_number = Column(Integer, nullable=False)
    run_count = Column(Integer, default=10000)
    status = Column(String(20), default="pending")
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    sport = relationship("Sport")
    projected_ratings = relationship("ProjectedRating", back_populates="simulation", cascade="all, delete-orphan")
    game_predictions = relationship("GamePrediction", back_populates="simulation", cascade="all, delete-orphan")
    game_impacts = relationship("GameImpactAnalysis", back_populates="simulation", cascade="all, delete-orphan")


class ProjectedRating(Base):
    __tablename__ = "projected_ratings"

    id = Column(Integer, primary_key=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    projected_rating_mean = Column(Numeric(6, 2))
    projected_rating_median = Column(Numeric(6, 2))
    projected_rating_p10 = Column(Numeric(6, 2))
    projected_rating_p90 = Column(Numeric(6, 2))
    projected_rank_mean = Column(Numeric(6, 1))
    playoff_probability = Column(Numeric(5, 2))
    championship_probability = Column(Numeric(5, 2))
    projected_wins_mean = Column(Numeric(4, 1))
    projected_losses_mean = Column(Numeric(4, 1))
    created_at = Column(DateTime, server_default=func.now())

    simulation = relationship("Simulation", back_populates="projected_ratings")
    team = relationship("Team")


class GamePrediction(Base):
    __tablename__ = "game_predictions"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    simulation_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"))
    home_win_probability = Column(Numeric(5, 2))
    predicted_home_score = Column(Numeric(5, 1))
    predicted_away_score = Column(Numeric(5, 1))
    predicted_spread = Column(Numeric(5, 1))
    created_at = Column(DateTime, server_default=func.now())

    simulation = relationship("Simulation", back_populates="game_predictions")
    game = relationship("Game")


class GameImpactAnalysis(Base):
    __tablename__ = "game_impact_analysis"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    simulation_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"))
    affected_team_id = Column(Integer, ForeignKey("teams.id"))
    rating_if_home_wins = Column(Numeric(6, 2))
    rating_if_away_wins = Column(Numeric(6, 2))
    rank_if_home_wins = Column(Integer)
    rank_if_away_wins = Column(Integer)
    playoff_prob_if_home_wins = Column(Numeric(5, 2))
    playoff_prob_if_away_wins = Column(Numeric(5, 2))
    created_at = Column(DateTime, server_default=func.now())

    simulation = relationship("Simulation", back_populates="game_impacts")
    game = relationship("Game")
    affected_team = relationship("Team")
```

- [ ] **Step 2: Create simulation Pydantic schemas**

Create `apps/api/app/schemas/simulations.py`:

```python
from datetime import datetime
from pydantic import BaseModel


class SimulationRunRequest(BaseModel):
    sport: str
    season_year: int
    week_number: int
    num_runs: int = 10000
    playoff_spots: int = 8


class SimulationOut(BaseModel):
    id: int
    sport_id: int
    season_year: int
    week_number: int
    run_count: int
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProjectedRatingOut(BaseModel):
    team_id: int
    school_name: str | None = None
    division: str | None = None
    projected_rating_mean: float
    projected_rating_median: float
    projected_rating_p10: float
    projected_rating_p90: float
    projected_rank_mean: float
    playoff_probability: float
    championship_probability: float
    projected_wins_mean: float
    projected_losses_mean: float

    model_config = {"from_attributes": True}


class GameImpactOut(BaseModel):
    affected_team_id: int
    school_name: str | None = None
    rating_if_home_wins: float
    rating_if_away_wins: float
    rank_if_home_wins: int
    rank_if_away_wins: int
    playoff_prob_if_home_wins: float
    playoff_prob_if_away_wins: float

    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Verify models import**

Run: `cd apps/api && .venv/Scripts/python -c "from app.models import Simulation, ProjectedRating, GamePrediction, GameImpactAnalysis; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add apps/api/app/models.py apps/api/app/schemas/simulations.py
git commit -m "feat(api): add ORM models and schemas for simulation tables"
```

---

### Task 9: API Simulation Routers

**Files:**
- Create: `apps/api/app/routers/simulations.py`
- Modify: `apps/api/app/main.py`

- [ ] **Step 1: Implement simulation router**

Create `apps/api/app/routers/simulations.py`:

```python
"""Simulation endpoints: run simulations, get results, game impact analysis."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import (
    Simulation, ProjectedRating, GamePrediction, GameImpactAnalysis,
    Team, School, Sport, Game,
)
from app.schemas.simulations import (
    SimulationRunRequest, SimulationOut,
    ProjectedRatingOut, GameImpactOut,
)

# Engine imports — engine package must be installed
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "packages", "engine"))
from engine.types import (
    TeamRecord, GameResult, GameStatus as EngineGameStatus,
    ScheduledGame, SimulationConfig, TeamProjection,
)
from engine.power_rating import calculate_all_ratings
from engine.monte_carlo import run_simulation
from engine.impact import analyze_game_impact
from engine.win_probability import win_probability

DIVISION_TO_CLASSIFICATION = {"I": "5A", "II": "4A", "III": "3A", "IV": "2A", "V": "1A"}

router = APIRouter()


def _load_teams(db: Session, sport_name: str, season_year: int) -> dict[int, TeamRecord]:
    rows = (
        db.query(Team, School)
        .join(School, Team.school_id == School.id)
        .join(Sport, Team.sport_id == Sport.id)
        .filter(Sport.name == sport_name, Team.season_year == season_year)
        .all()
    )
    teams = {}
    for team, school in rows:
        cls = school.classification or DIVISION_TO_CLASSIFICATION.get(team.division, "5A")
        teams[team.id] = TeamRecord(
            team_id=team.id, school_name=school.name,
            division=team.division, classification=cls,
        )
    return teams


def _load_played_games(db: Session, sport_name: str, season_year: int, up_to_week: int) -> list[GameResult]:
    rows = (
        db.query(Game)
        .join(Sport, Game.sport_id == Sport.id)
        .filter(
            Sport.name == sport_name,
            Game.season_year == season_year,
            Game.status.in_(["final", "forfeit"]),
            Game.week_number <= up_to_week,
        )
        .all()
    )
    return [
        GameResult(
            game_id=g.id, home_team_id=g.home_team_id, away_team_id=g.away_team_id,
            home_score=g.home_score, away_score=g.away_score,
            status=EngineGameStatus(g.status),
            is_forfeit=(g.status == "forfeit"),
            week_number=g.week_number,
        )
        for g in rows
    ]


def _load_remaining_games(db: Session, sport_name: str, season_year: int, after_week: int) -> list[ScheduledGame]:
    rows = (
        db.query(Game)
        .join(Sport, Game.sport_id == Sport.id)
        .filter(
            Sport.name == sport_name,
            Game.season_year == season_year,
            Game.status == "scheduled",
            Game.week_number > after_week,
        )
        .all()
    )
    return [
        ScheduledGame(game_id=g.id, home_team_id=g.home_team_id, away_team_id=g.away_team_id, week_number=g.week_number)
        for g in rows
    ]


def _run_and_store(sim_id: int, teams, played, remaining, config, db_url: str):
    """Run simulation and store results. Called as background task."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        db.query(Simulation).filter(Simulation.id == sim_id).update({
            "status": "running", "started_at": datetime.now(timezone.utc),
        })
        db.commit()

        projections = run_simulation(teams, played, remaining, config)

        # Store projected ratings
        sport = db.query(Sport).filter(Sport.name == config.sport_name).first()
        for tid, proj in projections.items():
            db.add(ProjectedRating(
                simulation_id=sim_id, team_id=tid,
                projected_rating_mean=proj.projected_rating_mean,
                projected_rating_median=proj.projected_rating_median,
                projected_rating_p10=proj.projected_rating_p10,
                projected_rating_p90=proj.projected_rating_p90,
                projected_rank_mean=proj.projected_rank_mean,
                playoff_probability=proj.playoff_probability,
                championship_probability=proj.championship_probability,
                projected_wins_mean=proj.projected_wins_mean,
                projected_losses_mean=proj.projected_losses_mean,
            ))

        # Store game predictions for remaining games
        for game in remaining:
            h_rating = teams[game.home_team_id].power_rating if game.home_team_id in teams else 0
            a_rating = teams[game.away_team_id].power_rating if game.away_team_id in teams else 0
            # Use current ratings for initial predictions
            current = calculate_all_ratings(teams, played)
            h_r = current.get(game.home_team_id)
            a_r = current.get(game.away_team_id)
            if h_r and a_r:
                prob = win_probability(h_r.power_rating, a_r.power_rating, config.home_advantage, config.k_factor)
                spread = (h_r.power_rating - a_r.power_rating + config.home_advantage)
                db.add(GamePrediction(
                    game_id=game.game_id, simulation_id=sim_id,
                    home_win_probability=round(prob * 100, 2),
                    predicted_spread=round(spread, 1),
                ))

        db.query(Simulation).filter(Simulation.id == sim_id).update({
            "status": "completed", "completed_at": datetime.now(timezone.utc),
        })
        db.commit()
    except Exception as e:
        db.query(Simulation).filter(Simulation.id == sim_id).update({"status": "failed"})
        db.commit()
        raise
    finally:
        db.close()


@router.post("/run", response_model=SimulationOut)
def run_sim(
    req: SimulationRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    sport = db.query(Sport).filter(Sport.name == req.sport).first()
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport '{req.sport}' not found")

    sim = Simulation(
        sport_id=sport.id, season_year=req.season_year,
        week_number=req.week_number, run_count=req.num_runs, status="pending",
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)

    teams = _load_teams(db, req.sport, req.season_year)
    played = _load_played_games(db, req.sport, req.season_year, req.week_number)
    remaining = _load_remaining_games(db, req.sport, req.season_year, req.week_number)
    config = SimulationConfig(
        sport_name=req.sport, season_year=req.season_year,
        week_number=req.week_number, num_runs=req.num_runs,
        playoff_spots=req.playoff_spots,
    )

    from app.config import settings
    background_tasks.add_task(_run_and_store, sim.id, teams, played, remaining, config, settings.DATABASE_URL)

    return sim


@router.get("/{sim_id}/results", response_model=list[ProjectedRatingOut])
def get_simulation_results(
    sim_id: int,
    division: str | None = Query(None),
    db: Session = Depends(get_db),
):
    sim = db.query(Simulation).filter(Simulation.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    query = (
        db.query(ProjectedRating, Team, School)
        .join(Team, ProjectedRating.team_id == Team.id)
        .join(School, Team.school_id == School.id)
        .filter(ProjectedRating.simulation_id == sim_id)
    )
    if division:
        query = query.filter(Team.division == division)
    query = query.order_by(ProjectedRating.projected_rank_mean.asc())
    rows = query.all()

    return [
        ProjectedRatingOut(
            team_id=pr.team_id,
            school_name=school.name,
            division=team.division,
            projected_rating_mean=float(pr.projected_rating_mean),
            projected_rating_median=float(pr.projected_rating_median),
            projected_rating_p10=float(pr.projected_rating_p10),
            projected_rating_p90=float(pr.projected_rating_p90),
            projected_rank_mean=float(pr.projected_rank_mean),
            playoff_probability=float(pr.playoff_probability),
            championship_probability=float(pr.championship_probability),
            projected_wins_mean=float(pr.projected_wins_mean),
            projected_losses_mean=float(pr.projected_losses_mean),
        )
        for pr, team, school in rows
    ]


@router.get("/{sim_id}", response_model=SimulationOut)
def get_simulation(sim_id: int, db: Session = Depends(get_db)):
    sim = db.query(Simulation).filter(Simulation.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim


@router.get("/game/{game_id}/impact", response_model=list[GameImpactOut])
def get_game_impact(
    game_id: int,
    db: Session = Depends(get_db),
):
    """Get stored impact analysis for a game from the most recent simulation."""
    rows = (
        db.query(GameImpactAnalysis, Team, School)
        .join(Team, GameImpactAnalysis.affected_team_id == Team.id)
        .join(School, Team.school_id == School.id)
        .filter(GameImpactAnalysis.game_id == game_id)
        .order_by(GameImpactAnalysis.simulation_id.desc())
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="No impact analysis found for this game")

    # Get latest simulation_id
    latest_sim = rows[0][0].simulation_id
    return [
        GameImpactOut(
            affected_team_id=gia.affected_team_id,
            school_name=school.name,
            rating_if_home_wins=float(gia.rating_if_home_wins),
            rating_if_away_wins=float(gia.rating_if_away_wins),
            rank_if_home_wins=gia.rank_if_home_wins,
            rank_if_away_wins=gia.rank_if_away_wins,
            playoff_prob_if_home_wins=float(gia.playoff_prob_if_home_wins),
            playoff_prob_if_away_wins=float(gia.playoff_prob_if_away_wins),
        )
        for gia, team, school in rows if gia.simulation_id == latest_sim
    ]


@router.get("/team/{team_id}/projections", response_model=ProjectedRatingOut | None)
def get_team_projections(
    team_id: int,
    db: Session = Depends(get_db),
):
    """Get latest projection for a specific team."""
    row = (
        db.query(ProjectedRating, Team, School)
        .join(Team, ProjectedRating.team_id == Team.id)
        .join(School, Team.school_id == School.id)
        .filter(ProjectedRating.team_id == team_id)
        .order_by(ProjectedRating.simulation_id.desc())
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="No projections found for this team")
    pr, team, school = row
    return ProjectedRatingOut(
        team_id=pr.team_id,
        school_name=school.name,
        division=team.division,
        projected_rating_mean=float(pr.projected_rating_mean),
        projected_rating_median=float(pr.projected_rating_median),
        projected_rating_p10=float(pr.projected_rating_p10),
        projected_rating_p90=float(pr.projected_rating_p90),
        projected_rank_mean=float(pr.projected_rank_mean),
        playoff_probability=float(pr.playoff_probability),
        championship_probability=float(pr.championship_probability),
        projected_wins_mean=float(pr.projected_wins_mean),
        projected_losses_mean=float(pr.projected_losses_mean),
    )
```

- [ ] **Step 2: Register simulation router in main.py**

Add to `apps/api/app/main.py` after the existing router imports:

```python
from app.routers import schools, teams, games, ratings, simulations
```

And add after the existing `include_router` calls:

```python
app.include_router(simulations.router, prefix="/api/v1/simulations", tags=["simulations"])
```

- [ ] **Step 3: Install engine package in API venv**

Run:
```bash
cd apps/api
.venv/Scripts/pip install -e ../../packages/engine
.venv/Scripts/python -c "from app.main import app; print(f'Routes: {len(app.routes)}')"
```
Expected: Route count increases (should be ~20+ with new simulation endpoints)

- [ ] **Step 4: Commit**

```bash
git add apps/api/app/routers/simulations.py apps/api/app/main.py
git commit -m "feat(api): add simulation endpoints (run, results, game impact, team projections)"
```

---

### Task 10: Integration Tests

**Files:**
- Create: `apps/api/tests/test_simulations.py`

- [ ] **Step 1: Write integration tests for simulation endpoints**

Create `apps/api/tests/test_simulations.py`:

```python
"""Integration tests for simulation endpoints. Requires live PostgreSQL."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_simulation_run_returns_201_or_200():
    """POST /simulations/run should create a simulation record."""
    resp = client.post("/api/v1/simulations/run", json={
        "sport": "Football",
        "season_year": 2025,
        "week_number": 11,
        "num_runs": 100,
        "playoff_spots": 8,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("pending", "running", "completed")
    assert data["run_count"] == 100
    assert "id" in data


def test_get_simulation_status():
    # First create one
    resp = client.post("/api/v1/simulations/run", json={
        "sport": "Football", "season_year": 2025, "week_number": 11, "num_runs": 10,
    })
    sim_id = resp.json()["id"]
    # Then check status
    resp2 = client.get(f"/api/v1/simulations/{sim_id}")
    assert resp2.status_code == 200
    assert resp2.json()["id"] == sim_id


def test_get_simulation_not_found():
    resp = client.get("/api/v1/simulations/999999")
    assert resp.status_code == 404


def test_get_team_projections_not_found():
    resp = client.get("/api/v1/simulations/team/999999/projections")
    assert resp.status_code == 404
```

- [ ] **Step 2: Run all tests**

Run: `cd apps/api && .venv/Scripts/python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 3: Commit**

```bash
git add apps/api/tests/test_simulations.py
git commit -m "test(api): add integration tests for simulation endpoints"
```

---

## Summary

| Task | What it builds | Key files |
|------|---------------|-----------|
| 1 | Engine data types | `src/types.py` |
| 2 | LHSAA power rating calculator | `src/power_rating.py` (20+ tests) |
| 3 | Win probability model | `src/win_probability.py` |
| 4 | Monte Carlo simulation | `src/monte_carlo.py` |
| 5 | "What's At Stake" impact | `src/impact.py` |
| 6 | Performance benchmarks | `tests/test_performance.py` |
| 7 | Engine CLI | `src/cli.py` |
| 8 | API models + schemas | `models.py`, `schemas/simulations.py` |
| 9 | API simulation routers | `routers/simulations.py` |
| 10 | API integration tests | `tests/test_simulations.py` |

**After all 10 tasks:** The engine can calculate power ratings from game results, run 10,000-run Monte Carlo simulations, analyze game impact scenarios, and expose everything through API endpoints + CLI.
