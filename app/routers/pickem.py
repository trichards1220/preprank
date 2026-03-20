from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.pickem import PickemContest, PickemSlate, PickemPick, PickemLeaderboard
from app.models.schools import School
from app.models.users import User
from app.auth import get_current_user
from app.schemas.schemas import (
    PickemContestOut,
    PickemSlateOut,
    PickemPickCreate,
    PickemPickOut,
    PickemLeaderboardEntry,
    SchoolLeaderboardEntry,
)

router = APIRouter(prefix="/pickem", tags=["pickem"])


@router.get("/", response_model=list[PickemContestOut])
async def list_active_contests(db: AsyncSession = Depends(get_db)):
    """Get current week's active contests."""
    result = await db.execute(
        select(PickemContest)
        .where(PickemContest.status == "active")
        .order_by(PickemContest.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{contest_id}/slate", response_model=list[PickemSlateOut])
async def get_contest_slate(contest_id: int, db: AsyncSession = Depends(get_db)):
    """Get all games in a contest's slate."""
    result = await db.execute(
        select(PickemContest).where(PickemContest.id == contest_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Contest not found")

    result = await db.execute(
        select(PickemSlate).where(PickemSlate.contest_id == contest_id)
    )
    return result.scalars().all()


@router.post("/picks", response_model=list[PickemPickOut], status_code=201)
async def submit_picks(
    picks: list[PickemPickCreate],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit picks for games in a contest. Contest must be active."""
    if not picks:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No picks provided",
        )

    # Validate all slates belong to active contests
    slate_ids = {p.slate_id for p in picks}
    for slate_id in slate_ids:
        slate_result = await db.execute(
            select(PickemSlate).where(PickemSlate.id == slate_id)
        )
        slate = slate_result.scalar_one_or_none()
        if not slate:
            raise HTTPException(status_code=404, detail=f"Slate {slate_id} not found")

        contest_result = await db.execute(
            select(PickemContest).where(PickemContest.id == slate.contest_id)
        )
        contest = contest_result.scalar_one_or_none()
        if not contest or contest.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contest for slate {slate_id} is not active",
            )

    # Check for duplicate picks
    for pick in picks:
        existing = await db.execute(
            select(PickemPick).where(
                PickemPick.user_id == user.id,
                PickemPick.slate_id == pick.slate_id,
                PickemPick.game_id == pick.game_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Pick already exists for game {pick.game_id} in slate {pick.slate_id}",
            )

    # Insert picks
    created_picks = []
    for pick in picks:
        new_pick = PickemPick(
            user_id=user.id,
            slate_id=pick.slate_id,
            game_id=pick.game_id,
            picked_winner_team_id=pick.picked_winner_team_id,
        )
        db.add(new_pick)
        created_picks.append(new_pick)

    await db.commit()
    for p in created_picks:
        await db.refresh(p)
    return created_picks


@router.get("/leaderboard", response_model=list[PickemLeaderboardEntry])
async def get_leaderboard(
    contest_id: int | None = None,
    school_id: int | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Global pick'em leaderboard, optionally filtered by contest or school."""
    query = select(
        PickemLeaderboard.user_id,
        School.name.label("school_name"),
        PickemLeaderboard.total_points,
        PickemLeaderboard.correct_picks,
        PickemLeaderboard.upset_picks,
        PickemLeaderboard.rank,
        PickemLeaderboard.streak,
    ).outerjoin(School, PickemLeaderboard.school_id == School.id)

    if contest_id:
        query = query.where(PickemLeaderboard.contest_id == contest_id)
    if school_id:
        query = query.where(PickemLeaderboard.school_id == school_id)

    query = query.order_by(PickemLeaderboard.total_points.desc()).limit(limit)
    result = await db.execute(query)
    rows = result.all()
    return [
        PickemLeaderboardEntry(
            user_id=r.user_id,
            school_name=r.school_name,
            total_points=r.total_points,
            correct_picks=r.correct_picks,
            upset_picks=r.upset_picks,
            rank=r.rank,
            streak=r.streak,
        )
        for r in rows
    ]


@router.get("/leaderboard/schools", response_model=list[SchoolLeaderboardEntry])
async def get_school_leaderboard(
    contest_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """School vs school leaderboard aggregated from individual entries."""
    from sqlalchemy import func as sa_func

    query = select(
        PickemLeaderboard.school_id,
        School.name.label("school_name"),
        sa_func.sum(PickemLeaderboard.total_points).label("total_points"),
        sa_func.avg(
            sa_func.cast(PickemLeaderboard.correct_picks, sa_func.numeric)
            / sa_func.nullif(
                sa_func.cast(PickemLeaderboard.correct_picks + PickemLeaderboard.upset_picks, sa_func.numeric),
                0,
            )
        ).label("avg_accuracy"),
        sa_func.count(PickemLeaderboard.user_id).label("participant_count"),
    ).join(School, PickemLeaderboard.school_id == School.id).where(
        PickemLeaderboard.school_id.is_not(None)
    )

    if contest_id:
        query = query.where(PickemLeaderboard.contest_id == contest_id)

    query = query.group_by(
        PickemLeaderboard.school_id, School.name
    ).order_by(sa_func.sum(PickemLeaderboard.total_points).desc())

    result = await db.execute(query)
    rows = result.all()
    return [
        SchoolLeaderboardEntry(
            school_id=r.school_id,
            school_name=r.school_name,
            total_points=r.total_points,
            avg_accuracy=float(r.avg_accuracy) if r.avg_accuracy else None,
            participant_count=r.participant_count,
        )
        for r in rows
    ]


@router.get("/my-picks", response_model=list[PickemPickOut])
async def get_my_picks(
    contest_id: int | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's pick history."""
    query = select(PickemPick).where(PickemPick.user_id == user.id)

    if contest_id:
        # Filter picks to slates belonging to the given contest
        query = query.join(PickemSlate, PickemPick.slate_id == PickemSlate.id).where(
            PickemSlate.contest_id == contest_id
        )

    query = query.order_by(PickemPick.picked_at.desc())
    result = await db.execute(query)
    return result.scalars().all()
