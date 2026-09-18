from fastapi import APIRouter

from app.student.profile import RawStudentProfile
from app.student.result import ProfileNormalizationResponse
from app.student.service import normalize_student_profile

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/normalize", response_model=ProfileNormalizationResponse)
def normalize_student(request: RawStudentProfile) -> ProfileNormalizationResponse:
    return normalize_student_profile(request)