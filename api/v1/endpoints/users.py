from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.auth import (
    get_password_hash,
    get_current_active_user,
    get_current_admin_user,
)
from core.database import get_db
from core.models import User
from core.schemas import UserResponse, UserUpdate

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_admin_user)):
    users = db.query(User).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_active_user)):
    if current_user.role.value != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_active_user)):
    if current_user.role.value != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.username:
        existing = db.query(User).filter(User.username == user_update.username, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = user_update.username

    if user_update.email:
        existing = db.query(User).filter(User.email == user_update.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        user.email = user_update.email

    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)

    if user_update.is_active is not None and current_user.role.value == "admin":
        user.is_active = user_update.is_active

    if user_update.role is not None and current_user.role.value == "admin":
        user.role = user_update.role

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return None


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
