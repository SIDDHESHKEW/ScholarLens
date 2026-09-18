from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.recommendations.models import RecommendationRequest, RecommendationResponse
from app.recommendations.service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
def create_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    return RecommendationService(db).generate(
        request.student_profile,
        limit=request.limit,
        include_possibly_eligible=request.include_possibly_eligible,
    )