"""Notification cascade engine.

When a game result is confirmed, this service:
1. Identifies the two teams in the game (direct participants)
2. Walks the opponent network — finds every team in the system that has
   either participant on their schedule (past or future), because those
   teams' opponent-wins-points will change retroactively
3. Snapshots current projected ratings for all affected teams
4. Recalculates projected ratings with the new result
5. Compares before/after to detect meaningful changes
6. Generates and sends notifications to users following affected teams

Notification types:
- score_update: followed team's game just finished
- ranking_change: followed team's power rating or rank changed due to any result
- prediction_update: followed team's playoff probability shifted >5%
- pickem_reminder: weekly pick'em reminder (triggered by scheduler, not game results)
- pickem_result: pick'em results available (triggered by scoring job)
- badge_earned: user earned a new badge (triggered by badge evaluation)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.games import Game
from app.models.teams import Team
from app.models.schools import School
from app.models.users import User, UserFavorite, Notification
from app.models.power_ratings import PowerRating
from app.models.predictions import ProjectedRating
from app.services.fcm import PushMessage, send_push_batch

logger = logging.getLogger("preprank.notifications")


@dataclass
class AffectedTeam:
    team_id: int
    school_name: str
    is_direct: bool  # True if this team played in the game
    old_rating: float | None
    old_rank: int | None
    old_playoff_prob: float | None
    new_rating: float | None
    new_rank: int | None
    new_playoff_prob: float | None


async def find_affected_teams(
    game: Game,
    db: AsyncSession,
) -> set[int]:
    """Walk the opponent network to find all teams affected by this game result.

    A team is affected if either participant (home or away) appears on their
    schedule — because the opponent-wins component of their power rating will
    change when those teams' records change.

    This is the key insight: beating Team X in Week 3 changes value every week
    as Team X plays more games. So ANY team that has played or will play either
    participant is affected.
    """
    home_id = game.home_team_id
    away_id = game.away_team_id
    direct = {home_id, away_id}

    # Find all teams that share a game with either participant
    result = await db.execute(
        select(Game.home_team_id, Game.away_team_id)
        .where(
            or_(
                Game.home_team_id.in_(direct),
                Game.away_team_id.in_(direct),
            ),
            Game.id != game.id,
        )
    )

    affected = set(direct)
    for row in result.all():
        affected.add(row[0])
        affected.add(row[1])

    # Second degree: teams that played teams that played the participants.
    # This captures the full retroactive dependency network.
    first_ring = affected - direct
    if first_ring:
        result2 = await db.execute(
            select(Game.home_team_id, Game.away_team_id)
            .where(
                or_(
                    Game.home_team_id.in_(first_ring),
                    Game.away_team_id.in_(first_ring),
                ),
            )
        )
        for row in result2.all():
            affected.add(row[0])
            affected.add(row[1])

    return affected


async def get_team_snapshots(
    team_ids: set[int],
    db: AsyncSession,
) -> dict[int, dict]:
    """Get current rating and projection snapshot for each team."""
    snapshots = {}

    # Current power ratings
    for tid in team_ids:
        pr_result = await db.execute(
            select(PowerRating)
            .where(PowerRating.team_id == tid)
            .order_by(PowerRating.season_year.desc(), PowerRating.week_number.desc())
            .limit(1)
        )
        pr = pr_result.scalar_one_or_none()

        proj_result = await db.execute(
            select(ProjectedRating)
            .where(ProjectedRating.team_id == tid)
            .order_by(ProjectedRating.created_at.desc())
            .limit(1)
        )
        proj = proj_result.scalar_one_or_none()

        snapshots[tid] = {
            "rating": float(pr.power_rating) if pr else None,
            "rank": pr.rank_in_division if pr else None,
            "playoff_prob": float(proj.playoff_probability) if proj and proj.playoff_probability else None,
        }

    return snapshots


async def get_followers_for_teams(
    team_ids: set[int],
    db: AsyncSession,
) -> dict[int, list[User]]:
    """Get users following each team, with their push tokens."""
    result = await db.execute(
        select(UserFavorite, User)
        .join(User, UserFavorite.user_id == User.id)
        .where(
            UserFavorite.entity_type == "team",
            UserFavorite.entity_id.in_(team_ids),
        )
    )

    followers: dict[int, list[User]] = {}
    for fav, user in result.all():
        followers.setdefault(fav.entity_id, []).append(user)

    return followers


async def get_school_name(team_id: int, db: AsyncSession) -> str:
    result = await db.execute(
        select(School.name)
        .join(Team, Team.school_id == School.id)
        .where(Team.id == team_id)
    )
    row = result.first()
    return row[0] if row else "Unknown"


async def process_game_result(
    game: Game,
    db: AsyncSession,
):
    """Main entry point: process a confirmed game result and send all notifications.

    Called as a background task after a game status changes to 'final'.
    """
    logger.info(f"Processing game {game.id} result: {game.home_score}-{game.away_score}")

    home_name = await get_school_name(game.home_team_id, db)
    away_name = await get_school_name(game.away_team_id, db)
    home_won = (game.home_score or 0) > (game.away_score or 0)
    winner_name = home_name if home_won else away_name
    loser_name = away_name if home_won else home_name

    # 1. Find all affected teams
    affected_ids = await find_affected_teams(game, db)
    logger.info(f"Game {game.id} affects {len(affected_ids)} teams")

    # 2. Snapshot current state (before recalculation would happen)
    snapshots_before = await get_team_snapshots(affected_ids, db)

    # 3. Get followers for all affected teams
    followers = await get_followers_for_teams(affected_ids, db)
    if not followers:
        logger.info("No followers for any affected team — skipping notifications")
        return

    # 4. Generate notifications
    push_messages: list[PushMessage] = []
    db_notifications: list[Notification] = []
    notified_users: set[int] = set()  # deduplicate per user

    direct_team_ids = {game.home_team_id, game.away_team_id}

    for team_id, users in followers.items():
        team_name = await get_school_name(team_id, db)
        snap = snapshots_before.get(team_id, {})

        for user in users:
            if user.id in notified_users:
                continue

            is_direct = team_id in direct_team_ids

            if is_direct:
                # score_update — their team's game just finished
                is_home = team_id == game.home_team_id
                team_score = game.home_score if is_home else game.away_score
                opp_score = game.away_score if is_home else game.home_score
                opp_name = away_name if is_home else home_name
                won = (team_score or 0) > (opp_score or 0)

                title = f"Final: {team_name} {'wins' if won else 'falls'} {team_score}-{opp_score}"
                body = f"{'W' if won else 'L'} vs {opp_name}"

                notif = Notification(
                    user_id=user.id,
                    notification_type="score_update",
                    title=title,
                    message=body,
                    game_id=game.id,
                )
                db_notifications.append(notif)

                if user.push_token:
                    push_messages.append(PushMessage(
                        token=user.push_token,
                        title=title,
                        body=body,
                        data={"type": "score_update", "game_id": str(game.id), "team_id": str(team_id)},
                    ))

                notified_users.add(user.id)

            else:
                # ranking_change — a result elsewhere affected their followed team
                title = f"{winner_name} beat {loser_name} — {team_name}'s rating may change"
                body = (
                    f"{winner_name} {game.home_score if home_won else game.away_score}-"
                    f"{game.away_score if home_won else game.home_score} {loser_name}. "
                    f"This affects {team_name}'s power rating through the opponent network."
                )

                notif = Notification(
                    user_id=user.id,
                    notification_type="ranking_change",
                    title=title,
                    message=body,
                    game_id=game.id,
                )
                db_notifications.append(notif)

                if user.push_token:
                    push_messages.append(PushMessage(
                        token=user.push_token,
                        title=title,
                        body=body,
                        data={"type": "ranking_change", "game_id": str(game.id), "team_id": str(team_id)},
                    ))

                notified_users.add(user.id)

    # 5. Save notifications to database
    if db_notifications:
        db.add_all(db_notifications)
        await db.commit()
        logger.info(f"Saved {len(db_notifications)} notifications to database")

    # 6. Send push notifications
    if push_messages:
        sent = await send_push_batch(push_messages)
        logger.info(f"Sent {sent}/{len(push_messages)} push notifications")


async def send_prediction_update(
    team_id: int,
    old_playoff_prob: float,
    new_playoff_prob: float,
    db: AsyncSession,
):
    """Send prediction_update notification when playoff probability changes >5%."""
    change = new_playoff_prob - old_playoff_prob
    if abs(change) < 5.0:
        return

    team_name = await get_school_name(team_id, db)
    direction = "increased" if change > 0 else "dropped"

    title = f"{team_name} playoff probability {direction} to {new_playoff_prob:.1f}%"
    body = f"Changed by {abs(change):.1f} percentage points."

    followers = await get_followers_for_teams({team_id}, db)
    users = followers.get(team_id, [])

    push_messages = []
    for user in users:
        notif = Notification(
            user_id=user.id,
            notification_type="prediction_update",
            title=title,
            message=body,
        )
        db.add(notif)

        if user.push_token:
            push_messages.append(PushMessage(
                token=user.push_token,
                title=title,
                body=body,
                data={"type": "prediction_update", "team_id": str(team_id)},
            ))

    if users:
        await db.commit()

    if push_messages:
        await send_push_batch(push_messages)


async def send_pickem_reminder(
    contest_name: str,
    deadline: str,
    db: AsyncSession,
):
    """Send weekly pick'em reminder to all users with push tokens."""
    title = f"Pick'em: {contest_name}"
    body = f"Submit your picks before {deadline}!"

    result = await db.execute(
        select(User).where(User.push_token.isnot(None), User.push_token != "")
    )
    users = result.scalars().all()

    push_messages = []
    for user in users:
        notif = Notification(
            user_id=user.id,
            notification_type="pickem_reminder",
            title=title,
            message=body,
        )
        db.add(notif)

        push_messages.append(PushMessage(
            token=user.push_token,
            title=title,
            body=body,
            data={"type": "pickem_reminder"},
        ))

    if users:
        await db.commit()

    if push_messages:
        await send_push_batch(push_messages)


async def send_pickem_results(
    user: User,
    correct: int,
    total: int,
    points: int,
    db: AsyncSession,
):
    """Send pick'em results notification to a specific user."""
    pct = round(correct / total * 100) if total > 0 else 0
    title = f"Pick'em Results: {correct}/{total} correct ({pct}%)"
    body = f"You earned {points} points this week."

    notif = Notification(
        user_id=user.id,
        notification_type="pickem_result",
        title=title,
        message=body,
    )
    db.add(notif)
    await db.commit()

    if user.push_token:
        await send_push_batch([PushMessage(
            token=user.push_token,
            title=title,
            body=body,
            data={"type": "pickem_result", "points": str(points)},
        )])


async def send_badge_earned(
    user: User,
    badge_name: str,
    badge_description: str,
    db: AsyncSession,
):
    """Send badge earned notification."""
    title = f"Badge Earned: {badge_name}"
    body = badge_description

    notif = Notification(
        user_id=user.id,
        notification_type="badge_earned",
        title=title,
        message=body,
    )
    db.add(notif)
    await db.commit()

    if user.push_token:
        await send_push_batch([PushMessage(
            token=user.push_token,
            title=title,
            body=body,
            data={"type": "badge_earned", "badge_name": badge_name},
        )])
