from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Scholarship, VerificationRecord
from app.intelligence.eligibility.engine import evaluate_eligibility
from app.intelligence.eligibility.evidence.service import EligibilityEvidenceService
from app.intelligence.eligibility.result import EligibilityStatus
from app.matching.dimensions import country_dimension, exact_dimension, field_of_study_dimension, funding_dimension
from app.matching.models import MatchStatus, MatchSummary, SoftMatchResult
from app.schemas.common import StudentProfile


def _values(value: StudentProfile | dict[str, Any]) -> dict[str, Any]:
    return value.model_dump() if isinstance(value, StudentProfile) else dict(value)


def _scholarship_values(scholarship: Scholarship | dict[str, Any]) -> dict[str, Any]:
    if isinstance(scholarship, dict):
        result = dict(scholarship)
    else:
        result = {key: getattr(scholarship, key) for key in ("id", "requirements", "legacy_metadata")}
    metadata = result.get("legacy_metadata") or {}
    result.update({
        "study_country": metadata.get("study_country"),
        "field_of_study": metadata.get("field_of_study"),
        "education_level": metadata.get("education_level"),
        "study_mode": metadata.get("study_mode"),
        "funding_type": metadata.get("funding_type"),
        "institution_type": metadata.get("institution_type"),
        "degree": metadata.get("degree"),
        "language": metadata.get("language"),
    })
    return result


class SoftMatchingService:
    def __init__(
        self,
        session: Session | None = None,
        evidence_service: EligibilityEvidenceService | None = None,
    ) -> None:
        self.session = session
        self.evidence_service = evidence_service or EligibilityEvidenceService()

    def evaluate(self, student: StudentProfile | dict[str, Any], scholarship: Scholarship | dict[str, Any]) -> SoftMatchResult:
        student_values = _values(student)
        scholarship_values = _scholarship_values(scholarship)
        structured_eligibility = evaluate_eligibility(student_values, scholarship_values.get("requirements") or [])
        hardened = self.evidence_service.harden_eligibility(structured_eligibility, student_values, scholarship)
        if hardened.status == EligibilityStatus.NOT_ELIGIBLE:
            summary = MatchSummary(matches=0, partial_matches=0, mismatches=0, unknown=0)
            return SoftMatchResult(
                scholarship_id=scholarship_values.get("id"),
                hard_eligibility_status=hardened.status.value,
                matching_allowed=False,
                exclusion_reason=hardened.explanation,
                match_factors=[], matched_dimensions=[], partially_matched_dimensions=[], mismatched_dimensions=[], unknown_dimensions=[], summary=summary,
                evidence_warnings=hardened.evidence_evaluation.warnings,
            )

        verification = self._verification_status(scholarship_values.get("id"))
        extra = student_values.get("extra_attributes") or {}
        factors = [
            field_of_study_dimension(student_values.get("field_of_study"), scholarship_values.get("field_of_study"), verification),
            country_dimension("study_country", student_values.get("preferred_study_country") or student_values.get("study_country"), scholarship_values.get("study_country"), "preferred study country", verification),
            exact_dimension("education_level", student_values.get("education_level"), scholarship_values.get("education_level"), "education level", verification),
            exact_dimension("study_mode", student_values.get("study_mode") or extra.get("preferred_study_mode"), scholarship_values.get("study_mode"), "study mode", verification),
            funding_dimension(
                student_values.get("funding_preference")
                or student_values.get("preferred_funding_type")
                or extra.get("preferred_funding_type")
                or extra.get("funding_preference"),
                scholarship_values.get("funding_type"),
                verification,
            ),
            exact_dimension("institution_type", student_values.get("institution_type") or extra.get("preferred_institution_type"), scholarship_values.get("institution_type"), "institution type", verification),
            exact_dimension("language", student_values.get("language") or extra.get("preferred_language"), scholarship_values.get("language"), "language preference", verification),
        ]
        return self._result(
            scholarship_values.get("id"),
            hardened.status.value,
            factors,
            evidence_warnings=hardened.evidence_evaluation.warnings,
        )

    def _verification_status(self, scholarship_id: int | None) -> str | None:
        if self.session is None or scholarship_id is None:
            return None
        record = self.session.scalar(select(VerificationRecord).where(VerificationRecord.scholarship_id == scholarship_id).order_by(VerificationRecord.verified_at.desc()))
        return record.verification_status if record else "UNVERIFIED"

    @staticmethod
    def _result(
        scholarship_id: int | None,
        status: str,
        factors: list[Any],
        evidence_warnings: list[str] | None = None,
    ) -> SoftMatchResult:
        matches = [factor.dimension for factor in factors if factor.status == MatchStatus.MATCH]
        partial = [factor.dimension for factor in factors if factor.status == MatchStatus.PARTIAL_MATCH]
        mismatches = [factor.dimension for factor in factors if factor.status == MatchStatus.MISMATCH]
        unknown = [factor.dimension for factor in factors if factor.status == MatchStatus.UNKNOWN]
        return SoftMatchResult(
            scholarship_id=scholarship_id, hard_eligibility_status=status, matching_allowed=True, exclusion_reason=None,
            match_factors=factors, matched_dimensions=matches, partially_matched_dimensions=partial,
            mismatched_dimensions=mismatches, unknown_dimensions=unknown,
            summary=MatchSummary(matches=len(matches), partial_matches=len(partial), mismatches=len(mismatches), unknown=len(unknown)),
            evidence_warnings=evidence_warnings or [],
        )



def evaluate_soft_match(student: StudentProfile | dict[str, Any], scholarship: Scholarship | dict[str, Any], session: Session | None = None) -> SoftMatchResult:
    return SoftMatchingService(session).evaluate(student, scholarship)