from fastapi import APIRouter

from api.v1.endpoints import auth, users, incidence_types, incidence_sub_types, incidences

router = APIRouter()

router.include_router(auth.router, tags=["Authentication"])
router.include_router(users.router, tags=["Users"])
router.include_router(incidence_types.router, prefix="/incidence-types", tags=["Incidence Types"])
router.include_router(incidence_sub_types.router, prefix="/incidence-sub-types", tags=["Incidence Sub Types"])
router.include_router(incidences.router, prefix="/incidences", tags=["Incidences"])
