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
