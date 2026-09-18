from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Scholarship, VerificationRecord
from app.matching.models import MatchFactor, MatchStatus, SoftMatchResult
from app.matching.service import SoftMatchingService
from app.repositories.scholarship_repository import ScholarshipRepository
from app.scoring.models import ScoringResult
from app.scoring.service import ScoringService
from app.student.service import normalize_student_profile
from app.student.profile import RawStudentProfile
from app.intelligence.taxonomy import AcademicRelevanceTier
from app.recommendations.quality import RecommendationQualityGate
from app.recommendations.models import (
    RecommendationEligibility,
    RecommendationExcluded,
    RecommendationItem,
    RecommendationResponse,
    RecommendationVerification,
)
from app.verification.schemas import FreshnessStatus, VerificationStatus
from app.verification.service import freshness


class RecommendationService:
    policy_version = "v1"

    def __init__(
        self,
        session: Session,
        *,
        include_synthetic: bool = False,
        max_age_days: int | None = None,
    ) -> None:
        self.session = session
        self.repository = ScholarshipRepository(session)
        self.matcher = SoftMatchingService(session)
        self.scorer = ScoringService()
        self.quality_gate = RecommendationQualityGate()
        self.include_synthetic = include_synthetic
        self.max_age_days = (
            max_age_days if max_age_days is not None else settings.verification_max_age_days
        )

    def generate(
        self,
        raw_student_profile: RawStudentProfile | dict,
        *,
        limit: int = 10,
        include_possibly_eligible: bool = True,
    ) -> RecommendationResponse:
        normalized = normalize_student_profile(raw_student_profile)
        student_dict = normalized.profile.model_dump()
        scholarships = self._candidate_scholarships()
        scholarships_by_id = {scholarship.id: scholarship for scholarship in scholarships}

        match_results = [
            self.matcher.evaluate(student_dict, scholarship)
            for scholarship in scholarships
        ]
        matches_by_id = {result.scholarship_id: result for result in match_results}
        ranked = self.scorer.rank(match_results)

        # 1. Eligibility gate
        eligible_results = [
            scored
            for scored in ranked.results
            if not (
                scored.eligibility_status == "POSSIBLY_ELIGIBLE"
                and not include_possibly_eligible
            )
        ]

        # 2. Recommendation Quality Gate (filter out specific field mismatches)
        quality_allowed = []
        quality_blocked_ids = []
        candidate_tiers: dict[int, AcademicRelevanceTier] = {}

        for scored in eligible_results:
            scholarship = scholarships_by_id[scored.scholarship_id]
            match = matches_by_id[scored.scholarship_id]
            meta = scholarship.legacy_metadata or {}
            decision = self.quality_gate.evaluate(student_dict, meta, match)
            if decision.allowed:
                quality_allowed.append(scored)
                candidate_tiers[scored.scholarship_id] = decision.academic_tier
            else:
                quality_blocked_ids.append(scored.scholarship_id)

        # 3. Deterministic ranking hierarchy:
        # 1. Scored before unscored
        # 2. Eligible before possibly eligible
        # 3. Academic relevance tier (Strong -> Partial -> Broad -> Unknown)
        # 4. Higher score first
        # 5. Higher evaluated dimensions count
        # 6. Lower scholarship_id (deterministic tie-breaker)
        eligibility_priority = {"ELIGIBLE": 0, "POSSIBLY_ELIGIBLE": 1}

        quality_allowed.sort(
            key=lambda scored: (
                0 if scored.score is not None else 1,
                eligibility_priority.get(scored.eligibility_status, 2),
                candidate_tiers.get(scored.scholarship_id, AcademicRelevanceTier.TIER_4_UNKNOWN).value,
                -(scored.score if scored.score is not None else -1),
                -scored.evaluated_dimensions,
                scored.scholarship_id if scored.scholarship_id is not None else 2**31,
            )
        )

        recommendations: list[RecommendationItem] = []
        for scored in quality_allowed[:limit]:
            rank = len(recommendations) + 1
            scholarship = scholarships_by_id[scored.scholarship_id]
            match = matches_by_id[scored.scholarship_id]
            recommendations.append(self._build_item(rank, scholarship, match, scored))

        excluded_ids = ranked.excluded_ids
        return RecommendationResponse(
            recommendation_policy_version=self.policy_version,
            scoring_policy_version=ranked.scoring_policy_version,
            student_profile_status=normalized.status.value,
            total_candidates=len(scholarships),
            recommended_count=len(recommendations),
            recommendations=recommendations,
            excluded=RecommendationExcluded(
                not_eligible_count=len(excluded_ids),
                not_eligible_ids=excluded_ids,
                quality_blocked_count=len(quality_blocked_ids),
                quality_blocked_ids=quality_blocked_ids,
            ),
        )

    def _candidate_scholarships(self) -> list[Scholarship]:
        return list(self.repository.list_candidates(include_synthetic=self.include_synthetic))

    def _build_item(
        self,
        rank: int,
        scholarship: Scholarship,
        match: SoftMatchResult,
        scored: ScoringResult,
    ) -> RecommendationItem:
        verification = self._verification(scholarship.id)
        warnings = list(verification.warnings)
        if match.hard_eligibility_status == "POSSIBLY_ELIGIBLE":
            warnings.append("Eligibility remains uncertain because mandatory information is unresolved.")
        if scored.score is None:
            warnings.append("Scholarship is unscored because matching criteria could not be evaluated against the student profile.")
        if match.evidence_warnings:
            warnings.extend(match.evidence_warnings)
        reasons = self._reasons(match)

        return RecommendationItem(
            rank=rank,
            scholarship_id=scholarship.id,
            title=scholarship.name,
            provider=scholarship.provider,
            eligibility=RecommendationEligibility(
                outcome=match.hard_eligibility_status,
                unknown_fields=self._unknown_fields(match),
            ),
            score=scored.score,
            score_breakdown=scored.score_breakdown,
            matching_factors=match.match_factors,
            reasons=reasons,
            warnings=warnings,
            verification=verification,
            deadline=scholarship.deadline,
            application_url=scholarship.application_url,
            official_source_url=scholarship.official_source_url,
        )


    def _verification(self, scholarship_id: int) -> RecommendationVerification:
        record = self.session.scalar(
            select(VerificationRecord)
            .where(VerificationRecord.scholarship_id == scholarship_id)
            .order_by(VerificationRecord.verified_at.desc())
        )
        if record is None:
            return RecommendationVerification(
                status=VerificationStatus.UNVERIFIED.value,
                freshness=FreshnessStatus.UNKNOWN.value,
                warnings=["This scholarship has not yet been independently verified."],
                verified_at=None,
                verifier_method=None,
                notes="No independent verification has been performed for this scholarship record.",
            )

        current_freshness = freshness(record.verified_at, max_age_days=self.max_age_days)
        is_stale = (
            current_freshness == FreshnessStatus.STALE
            or record.freshness_status == FreshnessStatus.STALE.value
            or record.verification_status == VerificationStatus.STALE.value
        )
        effective_status = VerificationStatus.STALE.value if is_stale else record.verification_status
        freshness_label = FreshnessStatus.STALE.value if is_stale else record.freshness_status

        warnings_map = {
            VerificationStatus.UNVERIFIED.value: "This scholarship has not yet been independently verified.",
            VerificationStatus.NEEDS_REVIEW.value: "Some scholarship information requires review.",
            VerificationStatus.SOURCE_UNAVAILABLE.value: "The scholarship source could not be reached during verification.",
            VerificationStatus.STALE.value: "Verification information may be outdated.",
            VerificationStatus.CONTRADICTED.value: "Available source information conflicts with this record.",
        }
        warning = warnings_map.get(effective_status)
        return RecommendationVerification(
            status=effective_status,
            freshness=freshness_label,
            warnings=[warning] if warning else [],
            verified_at=record.verified_at,
            verifier_method=record.verifier_method,
            notes=record.notes,
        )

    @staticmethod
    def _unknown_fields(match: SoftMatchResult) -> list[str]:
        return [factor.dimension for factor in match.match_factors if factor.status == MatchStatus.UNKNOWN]

    @staticmethod
    def _reasons(match: SoftMatchResult) -> list[str]:
        return [
            factor.explanation
            for factor in match.match_factors
            if factor.status in {MatchStatus.MATCH, MatchStatus.PARTIAL_MATCH}
        ]