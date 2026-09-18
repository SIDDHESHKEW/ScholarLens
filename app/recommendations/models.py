from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.matching.models import MatchFactor
from app.scoring.models import ScoreBreakdown
from app.student.profile import RawStudentProfile


class RecommendationEligibility(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome: str
    unknown_fields: list[str] = Field(default_factory=list)


class RecommendationVerification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "UNVERIFIED"
    freshness: str = "UNKNOWN"
    warnings: list[str] = Field(default_factory=list)
    verified_at: datetime | None = None
    verifier_method: str | None = None
    notes: str | None = None


class RecommendationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank: int
    scholarship_id: int
    title: str
    provider: str | None = None
    eligibility: RecommendationEligibility
    score: float | None
    score_breakdown: list[ScoreBreakdown]
    matching_factors: list[MatchFactor]
    reasons: list[str]
    warnings: list[str]
    verification: RecommendationVerification
    deadline: date | None = None
    application_url: str | None = None
    official_source_url: str | None = None


class RecommendationExcluded(BaseModel):
    model_config = ConfigDict(extra="forbid")

    not_eligible_count: int
    not_eligible_ids: list[int] = Field(default_factory=list)
    quality_blocked_count: int = 0
    quality_blocked_ids: list[int] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommendation_policy_version: str
    scoring_policy_version: str
    student_profile_status: str
    total_candidates: int
    recommended_count: int
    recommendations: list[RecommendationItem]
    excluded: RecommendationExcluded


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_profile: RawStudentProfile
    limit: int = Field(default=10, ge=1, le=100)
    include_possibly_eligible: bool = True