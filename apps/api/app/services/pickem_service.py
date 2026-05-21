"""Pick'em contest lifecycle: create -> open -> lock -> score -> close."""
from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_

from app.models import (
    PickemContest, PickemEntry, PickemBadge,
    Game, Team, School, Sport, User, UserFavorite, PowerRating,
)


def create_contest(db, sport_name, season_year, week_number, title=None, opens_at=None, locks_at=None):
    sport = db.query(Sport).filter(Sport.name == sport_name).first()
    if not sport:
        raise ValueError(f"Sport '{sport_name}' not found")
    if title is None:
        title = f"{sport_name} Week {week_number} Pick'em"
    contest = PickemContest(
        sport_id=sport.id, season_year=season_year, week_number=week_number,
        title=title, status="open",
        opens_at=opens_at or datetime.now(timezone.utc), locks_at=locks_at,
    )
    db.add(contest)
    db.commit()
    db.refresh(contest)
    return contest


def get_contest_games(db, contest):
    return (
        db.query(Game)
        .filter(Game.sport_id == contest.sport_id, Game.season_year == contest.season_year, Game.week_number == contest.week_number)
        .order_by(Game.game_date.asc(), Game.id.asc())
        .all()
    )


def submit_picks(db, contest_id, user_id, picks):
    contest = db.query(PickemContest).filter(PickemContest.id == contest_id).first()
    if not contest:
        raise ValueError("Contest not found")
    if contest.status != "open":
        raise ValueError(f"Contest is {contest.status}, not open for picks")
    if contest.locks_at and datetime.now(timezone.utc) > contest.locks_at.replace(tzinfo=timezone.utc):
        raise ValueError("Contest is locked")
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
                contest_id=contest_id, user_id=user_id,
                game_id=pick["game_id"], picked_team_id=pick["picked_team_id"],
            )
            db.add(entry)
            entries.append(entry)
    db.commit()
    for e in entries:
        db.refresh(e)
    return entries


def score_contest(db, contest_id):
    contest = db.query(PickemContest).filter(PickemContest.id == contest_id).first()
    if not contest:
        raise ValueError("Contest not found")
    final_games = db.query(Game).filter(
        Game.sport_id == contest.sport_id, Game.season_year == contest.season_year,
        Game.week_number == contest.week_number, Game.status == "final",
    ).all()
    winners = {}
    for g in final_games:
        if g.home_score is not None and g.away_score is not None:
            if g.home_score > g.away_score:
                winners[g.id] = g.home_team_id
            elif g.away_score > g.home_score:
                winners[g.id] = g.away_team_id
            else:
                winners[g.id] = None
    entries = db.query(PickemEntry).filter(PickemEntry.contest_id == contest_id).all()
    scored = 0
    for entry in entries:
        if entry.game_id in winners:
            winner = winners[entry.game_id]
            entry.is_correct = (winner is not None and entry.picked_team_id == winner)
            entry.points_earned = 1 if entry.is_correct else 0
            scored += 1
    contest.status = "scored"
    contest.scored_at = datetime.now(timezone.utc)
    db.commit()
    badges_awarded = _award_badges(db, contest_id)
    return {"scored": scored, "games_final": len(final_games), "badges_awarded": badges_awarded}


def _award_badges(db, contest_id):
    awarded = 0
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
        if correct == total and total >= 5:
            _give_badge(db, user_id, "perfect_week", "Perfect Week",
                        f"Predicted all {total} games correctly", contest_id)
            awarded += 1
        if total >= 5 and (correct / total) >= 0.8:
            _give_badge(db, user_id, "sharp_eye", "Sharp Eye",
                        f"80%+ accuracy ({correct}/{total})", contest_id)
            awarded += 1
    db.commit()
    return awarded


def _give_badge(db, user_id, badge_type, badge_name, description, contest_id):
    existing = db.query(PickemBadge).filter(
        PickemBadge.user_id == user_id, PickemBadge.badge_type == badge_type,
        PickemBadge.contest_id == contest_id,
    ).first()
    if not existing:
        db.add(PickemBadge(
            user_id=user_id, badge_type=badge_type, badge_name=badge_name,
            description=description, contest_id=contest_id,
        ))


def get_individual_leaderboard(db, contest_id=None, season_year=None):
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
        name = f"{user.first_name} {user.last_name[0]}." if user and user.first_name and user.last_name else f"User #{user_id}"
        leaderboard.append({
            "rank": rank, "user_id": user_id, "display_name": name,
            "total_correct": int(correct), "total_picks": int(total),
            "accuracy_pct": round(float(correct) / float(total) * 100, 1) if total > 0 else 0.0,
            "total_points": int(points or 0),
        })
    return leaderboard


def get_school_leaderboard(db, contest_id=None, season_year=None):
    fav_query = (
        db.query(UserFavorite.user_id, Team.school_id)
        .join(Team, and_(UserFavorite.entity_id == Team.id, UserFavorite.entity_type == "team"))
    )
    user_school = {row.user_id: row.school_id for row in fav_query.all()}
    if not user_school:
        return []
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
    school_stats = {}
    school_users = {}
    for entry in entries:
        sid = user_school.get(entry.user_id)
        if sid is None:
            continue
        if sid not in school_stats:
            school_stats[sid] = {"correct": 0, "total": 0}
            school_users[sid] = set()
        school_stats[sid]["total"] += 1
        if entry.is_correct:
            school_stats[sid]["correct"] += 1
        school_users[sid].add(entry.user_id)
    result = []
    for sid, stats in school_stats.items():
        school = db.query(School).filter(School.id == sid).first()
        if not school:
            continue
        result.append({
            "school_id": sid, "school_name": school.name,
            "total_correct": stats["correct"], "total_picks": stats["total"],
            "accuracy_pct": round(stats["correct"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0.0,
            "participant_count": len(school_users[sid]),
        })
    result.sort(key=lambda x: (-x["total_correct"], -x["accuracy_pct"]))
    for i, s in enumerate(result, 1):
        s["rank"] = i
    return result
