from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    TypeDecorator,
)
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import func as sql_func

from core.database import Base
import enum


class PointColumn(TypeDecorator):
    """Custom type for MySQL POINT geometry type"""
    impl = LargeBinary
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if hasattr(value, 'wkb'):
            return value.wkb
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value


@compiles(PointColumn, "mysql")
def compile_point_column_mysql(type_, compiler, **kw):
    return "POINT"


class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)


class IncidenceType(Base):
    __tablename__ = "incidence_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(100), nullable=False)


class IncidenceSubType(Base):
    __tablename__ = "incidence_sub_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey("incidence_types.id"), nullable=False)
    slug = Column(String(100), nullable=False)
    description = Column(String(100), nullable=False)


class Incidence(Base):
    __tablename__ = "incidences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type_id = Column(Integer, ForeignKey("incidence_types.id"), nullable=False)
    sub_type_id = Column(Integer, ForeignKey("incidence_sub_types.id"), nullable=True)
    coordinate = Column(PointColumn, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=sql_func.now(), nullable=False)
    updated_at = Column(DateTime, default=sql_func.now(), onupdate=sql_func.now(), nullable=False)
