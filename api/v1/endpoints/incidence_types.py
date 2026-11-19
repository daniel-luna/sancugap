from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.auth import get_current_admin_user
from core.database import get_db
from core.models import User, IncidenceType
from core.schemas import IncidenceTypeCreate, IncidenceTypeUpdate, IncidenceTypeResponse

router = APIRouter()


@router.post("/", response_model=IncidenceTypeResponse, status_code=status.HTTP_201_CREATED)
def create_incidence_type(
    incidence_type: IncidenceTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    existing = db.query(IncidenceType).filter(IncidenceType.slug == incidence_type.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    db_incidence_type = IncidenceType(
        slug=incidence_type.slug,
        description=incidence_type.description
    )
    db.add(db_incidence_type)
    db.commit()
    db.refresh(db_incidence_type)
    return db_incidence_type


@router.get("/", response_model=List[IncidenceTypeResponse])
def get_all_incidence_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    return db.query(IncidenceType).all()


@router.get("/{incidence_type_id}", response_model=IncidenceTypeResponse)
def get_incidence_type(
    incidence_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    incidence_type = db.query(IncidenceType).filter(IncidenceType.id == incidence_type_id).first()
    if not incidence_type:
        raise HTTPException(status_code=404, detail="Incidence type not found")
    return incidence_type


@router.put("/{incidence_type_id}", response_model=IncidenceTypeResponse)
def update_incidence_type(
    incidence_type_id: int,
    incidence_type_update: IncidenceTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    incidence_type = db.query(IncidenceType).filter(IncidenceType.id == incidence_type_id).first()
    if not incidence_type:
        raise HTTPException(status_code=404, detail="Incidence type not found")

    if incidence_type_update.slug:
        existing = db.query(IncidenceType).filter(
            IncidenceType.slug == incidence_type_update.slug,
            IncidenceType.id != incidence_type_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Slug already exists")
        incidence_type.slug = incidence_type_update.slug

    if incidence_type_update.description:
        incidence_type.description = incidence_type_update.description

    db.commit()
    db.refresh(incidence_type)
    return incidence_type


@router.delete("/{incidence_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incidence_type(
    incidence_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    incidence_type = db.query(IncidenceType).filter(IncidenceType.id == incidence_type_id).first()
    if not incidence_type:
        raise HTTPException(status_code=404, detail="Incidence type not found")

    db.delete(incidence_type)
    db.commit()
    return None
