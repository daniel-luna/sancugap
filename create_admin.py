from core.database import SessionLocal
from core.models import User, RoleEnum
from core.auth import get_password_hash


def create_admin_user():
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.role == RoleEnum.admin).first()
        if existing_admin:
            print(f"Ya existe un admin: {existing_admin.username}")
            return

        admin = User(
            username="admin",
            email="admin@sancugap.com",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            role=RoleEnum.admin
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin creado exitosamente!")
        print(f"  Username: admin")
        print(f"  Password: admin123")
        print(f"  Email: admin@sancugap.com")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
