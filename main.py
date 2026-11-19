from fastapi import FastAPI

from api.v1.router import router as api_v1_router
from core.database import Base, engine
from core.models import User

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Management API",
    version="1.0.0",
    description="API RESTful para gestión de usuarios con autenticación JWT"
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "API de Gestión de Usuarios", "version": "v1", "docs": "/docs"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
