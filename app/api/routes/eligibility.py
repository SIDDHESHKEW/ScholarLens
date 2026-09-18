from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from app.intelligence.eligibility.engine import evaluate_eligibility
from app.intelligence.eligibility.result import EligibilityEvaluation
from app.schemas.common import StudentProfile
from app.schemas.eligibility import EligibilityRule

router = APIRouter(prefix="/eligibility", tags=["eligibility"])


class EligibilityEvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student: StudentProfile
    rules: list[EligibilityRule | dict[str, Any]] = Field(min_length=1)


@router.post("/evaluate", response_model=EligibilityEvaluation)
def evaluate(request: EligibilityEvaluateRequest) -> EligibilityEvaluation:
    return evaluate_eligibility(request.student, request.rules)