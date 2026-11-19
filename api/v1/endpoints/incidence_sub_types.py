from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.auth import get_current_admin_user
from core.database import get_db
from core.models import User, IncidenceType, IncidenceSubType
from core.schemas import IncidenceSubTypeCreate, IncidenceSubTypeUpdate, IncidenceSubTypeResponse

router = APIRouter()


@router.post("/", response_model=IncidenceSubTypeResponse, status_code=status.HTTP_201_CREATED)
def create_incidence_sub_type(
    sub_type: IncidenceSubTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    type_exists = db.query(IncidenceType).filter(IncidenceType.id == sub_type.type_id).first()
    if not type_exists:
        raise HTTPException(status_code=400, detail="Incidence type not found")

    db_sub_type = IncidenceSubType(
        type_id=sub_type.type_id,
        slug=sub_type.slug,
        description=sub_type.description
    )
    db.add(db_sub_type)
    db.commit()
    db.refresh(db_sub_type)
    return db_sub_type


@router.get("/", response_model=List[IncidenceSubTypeResponse])
def get_all_incidence_sub_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    return db.query(IncidenceSubType).all()


@router.get("/{sub_type_id}", response_model=IncidenceSubTypeResponse)
def get_incidence_sub_type(
    sub_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    sub_type = db.query(IncidenceSubType).filter(IncidenceSubType.id == sub_type_id).first()
    if not sub_type:
        raise HTTPException(status_code=404, detail="Incidence sub type not found")
    return sub_type


@router.put("/{sub_type_id}", response_model=IncidenceSubTypeResponse)
def update_incidence_sub_type(
    sub_type_id: int,
    sub_type_update: IncidenceSubTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    sub_type = db.query(IncidenceSubType).filter(IncidenceSubType.id == sub_type_id).first()
    if not sub_type:
        raise HTTPException(status_code=404, detail="Incidence sub type not found")

    if sub_type_update.type_id:
        type_exists = db.query(IncidenceType).filter(IncidenceType.id == sub_type_update.type_id).first()
        if not type_exists:
            raise HTTPException(status_code=400, detail="Incidence type not found")
        sub_type.type_id = sub_type_update.type_id

    if sub_type_update.slug:
        sub_type.slug = sub_type_update.slug

    if sub_type_update.description:
        sub_type.description = sub_type_update.description

    db.commit()
    db.refresh(sub_type)
    return sub_type


@router.delete("/{sub_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incidence_sub_type(
    sub_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    sub_type = db.query(IncidenceSubType).filter(IncidenceSubType.id == sub_type_id).first()
    if not sub_type:
        raise HTTPException(status_code=404, detail="Incidence sub type not found")

    db.delete(sub_type)
    db.commit()
    return None