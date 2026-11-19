from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from shapely.geometry import Point
from shapely.wkb import loads

from core.auth import get_current_active_user
from core.database import get_db
from core.models import User, Incidence, IncidenceType, IncidenceSubType
from core.schemas import IncidenceCreate, IncidenceUpdate, IncidenceResponse

router = APIRouter()


def get_incidence_or_404(db: Session, incidence_id: int) -> Incidence:
    incidence = db.query(Incidence).filter(Incidence.id == incidence_id).first()
    if not incidence:
        raise HTTPException(status_code=404, detail="Incidence not found")
    return incidence


def check_incidence_permission(incidence: Incidence, current_user: User) -> bool:
    return current_user.role.value == "admin" or incidence.user_id == current_user.id


def point_to_lat_lon(wkb_bytes: bytes) -> tuple:
    point = loads(wkb_bytes)
    return point.x, point.y


def lat_lon_to_point(latitude: float, longitude: float) -> bytes:
    point = Point(longitude, latitude)
    return point.wkb


@router.post("/", response_model=IncidenceResponse, status_code=status.HTTP_201_CREATED)
def create_incidence(
    incidence: IncidenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    type_exists = db.query(IncidenceType).filter(IncidenceType.id == incidence.type_id).first()
    if not type_exists:
        raise HTTPException(status_code=400, detail="Incidence type not found")

    if incidence.sub_type_id:
        sub_type_exists = db.query(IncidenceSubType).filter(
            IncidenceSubType.id == incidence.sub_type_id
        ).first()
        if not sub_type_exists:
            raise HTTPException(status_code=400, detail="Incidence sub type not found")

    coordinate_wkb = lat_lon_to_point(incidence.latitude, incidence.longitude)

    db_incidence = Incidence(
        user_id=current_user.id,
        type_id=incidence.type_id,
        sub_type_id=incidence.sub_type_id,
        coordinate=coordinate_wkb,
        active=incidence.active
    )
    db.add(db_incidence)
    db.commit()
    db.refresh(db_incidence)

    longitude, latitude = point_to_lat_lon(db_incidence.coordinate)
    return IncidenceResponse(
        id=db_incidence.id,
        user_id=db_incidence.user_id,
        type_id=db_incidence.type_id,
        sub_type_id=db_incidence.sub_type_id,
        latitude=latitude,
        longitude=longitude,
        active=db_incidence.active,
        created_at=db_incidence.created_at,
        updated_at=db_incidence.updated_at
    )


@router.get("/", response_model=List[IncidenceResponse])
def get_all_incidences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role.value == "admin":
        incidences = db.query(Incidence).all()
    else:
        incidences = db.query(Incidence).filter(Incidence.user_id == current_user.id).all()

    result = []
    for inc in incidences:
        longitude, latitude = point_to_lat_lon(inc.coordinate)
        result.append(IncidenceResponse(
            id=inc.id,
            user_id=inc.user_id,
            type_id=inc.type_id,
            sub_type_id=inc.sub_type_id,
            latitude=latitude,
            longitude=longitude,
            active=inc.active,
            created_at=inc.created_at,
            updated_at=inc.updated_at
        ))
    return result


@router.get("/{incidence_id}", response_model=IncidenceResponse)
def get_incidence(
    incidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    incidence = get_incidence_or_404(db, incidence_id)
    if not check_incidence_permission(incidence, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    longitude, latitude = point_to_lat_lon(incidence.coordinate)
    return IncidenceResponse(
        id=incidence.id,
        user_id=incidence.user_id,
        type_id=incidence.type_id,
        sub_type_id=incidence.sub_type_id,
        latitude=latitude,
        longitude=longitude,
        active=incidence.active,
        created_at=incidence.created_at,
        updated_at=incidence.updated_at
    )


@router.put("/{incidence_id}", response_model=IncidenceResponse)
def update_incidence(
    incidence_id: int,
    incidence_update: IncidenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    incidence = get_incidence_or_404(db, incidence_id)
    if not check_incidence_permission(incidence, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if incidence_update.type_id:
        type_exists = db.query(IncidenceType).filter(IncidenceType.id == incidence_update.type_id).first()
        if not type_exists:
            raise HTTPException(status_code=400, detail="Incidence type not found")
        incidence.type_id = incidence_update.type_id

    if incidence_update.sub_type_id:
        sub_type_exists = db.query(IncidenceSubType).filter(
            IncidenceSubType.id == incidence_update.sub_type_id
        ).first()
        if not sub_type_exists:
            raise HTTPException(status_code=400, detail="Incidence sub type not found")
        incidence.sub_type_id = incidence_update.sub_type_id
    elif incidence_update.sub_type_id is None:
        incidence.sub_type_id = None

    if incidence_update.latitude is not None and incidence_update.longitude is not None:
        incidence.coordinate = lat_lon_to_point(incidence_update.latitude, incidence_update.longitude)

    if incidence_update.active is not None:
        incidence.active = incidence_update.active

    db.commit()
    db.refresh(incidence)

    longitude, latitude = point_to_lat_lon(incidence.coordinate)
    return IncidenceResponse(
        id=incidence.id,
        user_id=incidence.user_id,
        type_id=incidence.type_id,
        sub_type_id=incidence.sub_type_id,
        latitude=latitude,
        longitude=longitude,
        active=incidence.active,
        created_at=incidence.created_at,
        updated_at=incidence.updated_at
    )


@router.delete("/{incidence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incidence(
    incidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    incidence = get_incidence_or_404(db, incidence_id)
    if not check_incidence_permission(incidence, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(incidence)
    db.commit()
    return None