from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.schools import School
from app.schemas.schemas import SchoolOut, SchoolDetailOut

router = APIRouter(prefix="/schools", tags=["schools"])


@router.get("/", response_model=list[SchoolOut])
async def list_schools(
    classification: str | None = None,
    division: str | None = None,
    select_status: str | None = None,
    parish: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(School).order_by(School.name)
    if classification:
        query = query.where(School.classification == classification)
    if division:
        query = query.where(School.division == division)
    if select_status:
        query = query.where(School.select_status == select_status)
    if parish:
        query = query.where(School.parish == parish)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{school_id}", response_model=SchoolDetailOut)
async def get_school(school_id: int, db: AsyncSession = Depends(get_db)):
    """Get school detail including all teams across sports and seasons."""
    result = await db.execute(
        select(School)
        .where(School.id == school_id)
        .options(selectinload(School.teams))
    )
    school = result.scalar_one_or_none()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school
