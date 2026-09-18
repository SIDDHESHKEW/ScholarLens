from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.repositories.scholarship_repository import ScholarshipRepository
from app.matching.models import SoftMatchResult
from app.matching.service import SoftMatchingService
from app.schemas.common import StudentProfile

router = APIRouter(prefix="/matching", tags=["matching"])


class MatchingEvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student: StudentProfile
    scholarship_id: int


@router.post("/evaluate", response_model=SoftMatchResult)
def evaluate_matching(request: MatchingEvaluateRequest, db: Session = Depends(get_db)) -> SoftMatchResult:
    scholarship = ScholarshipRepository(db).get(request.scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    return SoftMatchingService(db).evaluate(request.student, scholarship)