from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schools import School
from app.schemas.schemas import SchoolOut

router = APIRouter(prefix="/schools", tags=["schools"])


@router.get("/", response_model=list[SchoolOut])
async def list_schools(
    classification: str | None = None,
    parish: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(School)
    if classification:
        query = query.where(School.classification == classification)
    if parish:
        query = query.where(School.parish == parish)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{school_id}", response_model=SchoolOut)
async def get_school(school_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(School).where(School.id == school_id))
    school = result.scalar_one_or_none()
    if not school:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="School not found")
    return school
