from dataclasses import dataclass
from typing import Any

from app.intelligence.taxonomy import AcademicRelevanceTier, FieldClassification, classify_scholarship_field
from app.matching.models import MatchFactor, MatchStatus, SoftMatchResult


@dataclass
class QualityGateDecision:
    allowed: bool
    rejection_reason: str | None = None
    academic_tier: AcademicRelevanceTier = AcademicRelevanceTier.TIER_4_UNKNOWN


class RecommendationQualityGate:
    """
    Deterministic quality gate that prevents scholarships with specific incompatible
    academic disciplines from being recommended to students with specified fields of study.
    """

    def evaluate(
        self,
        student_profile: dict[str, Any],
        scholarship_metadata: dict[str, Any],
        match_result: SoftMatchResult,
    ) -> QualityGateDecision:
        student_field = student_profile.get("field_of_study")
        scholarship_field_raw = scholarship_metadata.get("field_of_study")
        classification = classify_scholarship_field(scholarship_field_raw)

        # Find the field_of_study match factor
        field_factor: MatchFactor | None = next(
            (f for f in match_result.match_factors if f.dimension == "field_of_study"),
            None,
        )
        field_status = field_factor.status if field_factor else MatchStatus.UNKNOWN

        # 1. If student did not specify a field_of_study, no field contradiction exists
        if not student_field:
            return QualityGateDecision(
                allowed=True,
                academic_tier=AcademicRelevanceTier.TIER_4_UNKNOWN,
            )

        # 2. If scholarship is genuinely broad / unrestricted to all disciplines
        if classification == FieldClassification.BROAD:
            return QualityGateDecision(
                allowed=True,
                academic_tier=AcademicRelevanceTier.TIER_3_BROAD,
            )

        # 3. If scholarship field is unknown / not specified
        if classification == FieldClassification.UNKNOWN or field_status == MatchStatus.UNKNOWN:
            return QualityGateDecision(
                allowed=True,
                academic_tier=AcademicRelevanceTier.TIER_4_UNKNOWN,
            )

        # 4. If exact / direct discipline match
        if field_status == MatchStatus.MATCH:
            return QualityGateDecision(
                allowed=True,
                academic_tier=AcademicRelevanceTier.TIER_1_STRONG,
            )

        # 5. If broader / adjacent taxonomy match (e.g. CS -> Engineering)
        if field_status == MatchStatus.PARTIAL_MATCH:
            return QualityGateDecision(
                allowed=True,
                academic_tier=AcademicRelevanceTier.TIER_2_PARTIAL,
            )

        # 6. Specific field mismatch: Student field conflicts with specific scholarship discipline
        if field_status == MatchStatus.MISMATCH and classification == FieldClassification.SPECIFIC:
            return QualityGateDecision(
                allowed=False,
                rejection_reason=(
                    f"Scholarship requires specific discipline '{scholarship_field_raw}' "
                    f"which conflicts with student's field '{student_field}'."
                ),
                academic_tier=AcademicRelevanceTier.TIER_5_BLOCKED,
            )

        return QualityGateDecision(
            allowed=True,
            academic_tier=AcademicRelevanceTier.TIER_4_UNKNOWN,
        )
