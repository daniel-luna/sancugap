import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.models import PointColumn


@compiles(PointColumn, "sqlite")
def compile_point_column_sqlite(type_, compiler, **kw):
    return "BLOB"


from core import database
from core.database import Base

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

database.engine = test_engine
database.SessionLocal = TestSessionLocal

Base.metadata.create_all(bind=test_engine)

from main import app
from core.auth import create_access_token, get_password_hash, get_current_active_user, get_current_admin_user
from core.database import get_db
from core.models import User, IncidenceType, IncidenceSubType, Incidence
from core.schemas import RoleEnum


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def admin_user(db_session):
    hashed = get_password_hash("admin123")
    user = User(
        username="admin",
        email="admin@test.com",
        hashed_password=hashed,
        role=RoleEnum.admin,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session):
    hashed = get_password_hash("user123")
    user = User(
        username="regularuser",
        email="user@test.com",
        hashed_password=hashed,
        role=RoleEnum.user,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def inactive_user(db_session):
    hashed = get_password_hash("inactive123")
    user = User(
        username="inactive",
        email="inactive@test.com",
        hashed_password=hashed,
        role=RoleEnum.user,
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def another_user(db_session):
    hashed = get_password_hash("another123")
    user = User(
        username="another",
        email="another@test.com",
        hashed_password=hashed,
        role=RoleEnum.user,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    return create_access_token(
        data={"sub": admin_user.username, "role": admin_user.role.value}
    )


@pytest.fixture
def user_token(regular_user):
    return create_access_token(
        data={"sub": regular_user.username, "role": regular_user.role.value}
    )


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def client(db_session):
    def _get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def incidence_type(db_session):
    it = IncidenceType(slug="accident", description="Accident")
    db_session.add(it)
    db_session.commit()
    db_session.refresh(it)
    return it


@pytest.fixture
def incidence_sub_type(db_session, incidence_type):
    ist = IncidenceSubType(
        type_id=incidence_type.id,
        slug="car-crash",
        description="Car crash",
    )
    db_session.add(ist)
    db_session.commit()
    db_session.refresh(ist)
    return ist
