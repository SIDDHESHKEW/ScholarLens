from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.matching.service import SoftMatchingService
from app.repositories.scholarship_repository import ScholarshipRepository
from app.schemas.common import StudentProfile
from app.scoring.models import RankingResult, ScoringResult
from app.scoring.service import ScoringService

router = APIRouter(prefix="/scoring", tags=["scoring"])


class ScoringEvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student: StudentProfile
    scholarship_id: int


class ScoringRankRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student: StudentProfile
    scholarship_ids: list[int] = Field(min_length=1)


@router.post("/evaluate", response_model=ScoringResult)
def evaluate_scoring(request: ScoringEvaluateRequest, db: Session = Depends(get_db)) -> ScoringResult:
    scholarship = ScholarshipRepository(db).get(request.scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    match_result = SoftMatchingService(db).evaluate(request.student, scholarship)
    return ScoringService().score(match_result)


@router.post("/rank", response_model=RankingResult)
def rank_scoring(request: ScoringRankRequest, db: Session = Depends(get_db)) -> RankingResult:
    repository = ScholarshipRepository(db)
    scholarships = []
    missing_ids: list[int] = []
    for scholarship_id in request.scholarship_ids:
        scholarship = repository.get(scholarship_id)
        if scholarship is None:
            missing_ids.append(scholarship_id)
        else:
            scholarships.append(scholarship)
    if missing_ids:
        raise HTTPException(status_code=404, detail=f"Scholarships not found: {missing_ids}")
    matcher = SoftMatchingService(db)
    matches = [matcher.evaluate(request.student, scholarship) for scholarship in scholarships]
    return ScoringService().rank(matches)