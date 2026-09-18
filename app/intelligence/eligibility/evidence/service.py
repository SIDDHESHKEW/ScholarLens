from typing import Any

from app.intelligence.eligibility.result import EligibilityEvaluation, EligibilityStatus
from app.schemas.common import StudentProfile

from .detector import EvidenceDetector
from .models import (
    DataQualityStatus,
    EligibilityEvidenceItem,
    EvidenceConfidence,
    EvidenceEvaluationResult,
    HardenedEligibilityResult,
)

CANONICAL_LEVELS = {
    "ug": "undergraduate",
    "undergraduate": "undergraduate",
    "bachelor": "undergraduate",
    "bachelors": "undergraduate",
    "bachelor's": "undergraduate",
    "b.tech": "undergraduate",
    "b.e.": "undergraduate",
    "bs": "undergraduate",
    "bsc": "undergraduate",
    "pg": "postgraduate",
    "postgraduate": "postgraduate",
    "master": "postgraduate",
    "masters": "postgraduate",
    "master's": "postgraduate",
    "graduate": "postgraduate",
    "m.tech": "postgraduate",
    "ms": "postgraduate",
    "msc": "postgraduate",
    "phd": "doctoral",
    "doctoral": "doctoral",
    "doctorate": "doctoral",
    "postdoc": "postdoctoral",
    "postdoctoral": "postdoctoral",
    "school": "school",
    "high school": "school",
}


class EligibilityEvidenceService:
    def __init__(self, detector: EvidenceDetector | None = None) -> None:
        self.detector = detector or EvidenceDetector()

    def evaluate_evidence(
        self,
        student: StudentProfile | dict[str, Any],
        scholarship: Any,
    ) -> EvidenceEvaluationResult:
        student_values = student.model_dump() if isinstance(student, StudentProfile) else dict(student)
        signals = self.detector.detect_evidence(scholarship)

        high_signals = [s for s in signals if s.confidence == EvidenceConfidence.HIGH]
        medium_signals = [s for s in signals if s.confidence == EvidenceConfidence.MEDIUM]
        low_signals = [s for s in signals if s.confidence == EvidenceConfidence.LOW]

        warnings: list[str] = []
        for s in medium_signals + low_signals:
            warnings.append(f"Review signal: {s.reason} (excerpt: '{s.text_excerpt}')")

        raw_student_level = student_values.get("education_level")
        student_level = CANONICAL_LEVELS.get(str(raw_student_level).strip().lower()) if raw_student_level else None

        if not high_signals:
            status = DataQualityStatus.PARTIAL if medium_signals else DataQualityStatus.INSUFFICIENT
            return EvidenceEvaluationResult(
                has_contradiction=False,
                detected_signals=signals,
                data_quality_status=status,
                warnings=warnings,
            )

        detected_levels = {s.detected_value for s in high_signals}

        # If student has no education level specified, no contradiction can be verified
        if not student_level:
            return EvidenceEvaluationResult(
                has_contradiction=False,
                detected_signals=signals,
                data_quality_status=DataQualityStatus.PARTIAL,
                warnings=warnings,
            )

        # Multi-level or single-level compatibility check
        if student_level in detected_levels:
            return EvidenceEvaluationResult(
                has_contradiction=False,
                detected_signals=signals,
                data_quality_status=DataQualityStatus.SUFFICIENT,
                warnings=warnings,
            )

        # Check for hard contradictions
        has_contradiction = False
        reason = None

        # Undergraduate student vs higher levels
        if student_level == "undergraduate":
            higher_levels = {"postgraduate", "doctoral", "postdoctoral"}
            # If the scholarship exclusively targets higher levels and does NOT target undergraduate
            if detected_levels.issubset(higher_levels) and "undergraduate" not in detected_levels:
                has_contradiction = True
                target_str = "/".join(sorted(detected_levels))
                reason = (
                    f"The scholarship requires or targets a {target_str} level, "
                    f"which is incompatible with the student's undergraduate education level."
                )

        # Postgraduate student vs undergraduate/school
        elif student_level == "postgraduate":
            lower_levels = {"undergraduate", "school"}
            if detected_levels.issubset(lower_levels) and not (detected_levels & {"postgraduate", "doctoral", "postdoctoral"}):
                has_contradiction = True
                target_str = "/".join(sorted(detected_levels))
                reason = (
                    f"The scholarship explicitly targets {target_str} applicants, "
                    f"which is incompatible with the student's postgraduate education level."
                )

        # Doctoral student vs undergraduate/school
        elif student_level == "doctoral":
            lower_levels = {"undergraduate", "school"}
            if detected_levels.issubset(lower_levels):
                has_contradiction = True
                target_str = "/".join(sorted(detected_levels))
                reason = (
                    f"The scholarship explicitly targets {target_str} applicants, "
                    f"which is incompatible with the student's doctoral education level."
                )

        # Postdoctoral applicant vs lower levels
        elif student_level == "postdoctoral":
            lower_levels = {"undergraduate", "school"}
            if detected_levels.issubset(lower_levels):
                has_contradiction = True
                target_str = "/".join(sorted(detected_levels))
                reason = (
                    f"The scholarship explicitly targets {target_str} applicants, "
                    f"which is incompatible with the student's postdoctoral education level."
                )

        if has_contradiction:
            return EvidenceEvaluationResult(
                has_contradiction=True,
                contradiction_reason=reason,
                contradicted_field="education_level",
                detected_signals=signals,
                data_quality_status=DataQualityStatus.CONTRADICTORY,
                warnings=warnings,
            )

        return EvidenceEvaluationResult(
            has_contradiction=False,
            detected_signals=signals,
            data_quality_status=DataQualityStatus.PARTIAL,
            warnings=warnings,
        )

    def harden_eligibility(
        self,
        structured_evaluation: EligibilityEvaluation,
        student: StudentProfile | dict[str, Any],
        scholarship: Any,
    ) -> HardenedEligibilityResult:
        evidence_result = self.evaluate_evidence(student, scholarship)

        # Hard failure in structured rules always takes precedence as NOT_ELIGIBLE
        if structured_evaluation.status == EligibilityStatus.NOT_ELIGIBLE:
            return HardenedEligibilityResult(
                status=EligibilityStatus.NOT_ELIGIBLE,
                explanation=structured_evaluation.explanation,
                structured_evaluation=structured_evaluation,
                evidence_evaluation=evidence_result,
            )

        # If structured rules passed or are possible, check for strong evidence contradiction
        if evidence_result.has_contradiction:
            explanation = (
                f"The student fails an evidence-based mandatory requirement: "
                f"{evidence_result.contradiction_reason}"
            )
            return HardenedEligibilityResult(
                status=EligibilityStatus.NOT_ELIGIBLE,
                explanation=explanation,
                structured_evaluation=structured_evaluation,
                evidence_evaluation=evidence_result,
            )

        # Otherwise preserve structured evaluation status
        return HardenedEligibilityResult(
            status=structured_evaluation.status,
            explanation=structured_evaluation.explanation,
            structured_evaluation=structured_evaluation,
            evidence_evaluation=evidence_result,
        )
