from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Team, School
from app.auth.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()


class FavoriteRequest(BaseModel):
    entity_type: str = "team"  # team, athlete, school
    entity_id: int


class FavoriteOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    school_name: str | None = None
    division: str | None = None
    classification: str | None = None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[FavoriteOut])
def list_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models import UserFavorite
    favs = db.query(UserFavorite).filter(UserFavorite.user_id == current_user.id).all()
    result = []
    for f in favs:
        out = FavoriteOut(id=f.id, entity_type=f.entity_type, entity_id=f.entity_id)
        if f.entity_type == "team":
            team = db.query(Team).filter(Team.id == f.entity_id).first()
            if team:
                school = db.query(School).filter(School.id == team.school_id).first()
                if school:
                    out.school_name = school.name
                    out.division = team.division
                    out.classification = school.classification
        result.append(out)
    return result


@router.post("/", response_model=FavoriteOut, status_code=201)
def add_favorite(
    req: FavoriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models import UserFavorite
    # Check duplicate
    existing = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.entity_type == req.entity_type,
        UserFavorite.entity_id == req.entity_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already favorited")

    fav = UserFavorite(
        user_id=current_user.id,
        entity_type=req.entity_type,
        entity_id=req.entity_id,
    )
    db.add(fav)
    db.commit()
    db.refresh(fav)

    out = FavoriteOut(id=fav.id, entity_type=fav.entity_type, entity_id=fav.entity_id)
    if req.entity_type == "team":
        team = db.query(Team).filter(Team.id == req.entity_id).first()
        if team:
            school = db.query(School).filter(School.id == team.school_id).first()
            if school:
                out.school_name = school.name
                out.division = team.division
                out.classification = school.classification
    return out


@router.delete("/{favorite_id}", status_code=204)
def remove_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models import UserFavorite
    fav = db.query(UserFavorite).filter(
        UserFavorite.id == favorite_id,
        UserFavorite.user_id == current_user.id,
    ).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(fav)
    db.commit()
