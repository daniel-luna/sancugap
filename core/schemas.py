from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional
from datetime import datetime


class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.user


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[RoleEnum] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: RoleEnum

    class Config:
        from_attributes = True


class IncidenceTypeCreate(BaseModel):
    slug: str
    description: str


class IncidenceTypeUpdate(BaseModel):
    slug: Optional[str] = None
    description: Optional[str] = None


class IncidenceTypeResponse(BaseModel):
    id: int
    slug: str
    description: str

    class Config:
        from_attributes = True


class IncidenceSubTypeCreate(BaseModel):
    type_id: int
    slug: str
    description: str


class IncidenceSubTypeUpdate(BaseModel):
    type_id: Optional[int] = None
    slug: Optional[str] = None
    description: Optional[str] = None


class IncidenceSubTypeResponse(BaseModel):
    id: int
    type_id: int
    slug: str
    description: str

    class Config:
        from_attributes = True


class IncidenceCreate(BaseModel):
    type_id: int
    sub_type_id: Optional[int] = None
    latitude: float
    longitude: float
    active: bool = True


class IncidenceUpdate(BaseModel):
    type_id: Optional[int] = None
    sub_type_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    active: Optional[bool] = None


class IncidenceResponse(BaseModel):
    id: int
    user_id: int
    type_id: int
    sub_type_id: Optional[int]
    latitude: float
    longitude: float
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
