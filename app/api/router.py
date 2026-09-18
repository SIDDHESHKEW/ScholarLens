
from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.eligibility import router as eligibility_router
from app.api.routes.scholarships import router as scholarships_router
from app.api.routes.students import router as students_router
from app.api.routes.verification import router as verification_router
from app.api.routes.matching import router as matching_router
from app.api.routes.scoring import router as scoring_router
from app.api.routes.recommendations import router as recommendations_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(scholarships_router)
api_router.include_router(eligibility_router)
api_router.include_router(students_router)
api_router.include_router(verification_router)
api_router.include_router(matching_router)
api_router.include_router(scoring_router)
api_router.include_router(recommendations_router)