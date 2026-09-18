from typing import Any

from pydantic import BaseModel, ConfigDict

from app.matching.models import MatchStatus


class ScoreBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension: str
    status: MatchStatus
    weight: float
    contribution: float | None
    explanation: str
    data_verification_status: str | None = None


class ScoringSummary(BaseModel):
    evaluated_dimensions: int
    unknown_dimensions: int
    matches: int
    partial_matches: int
    mismatches: int
    denominator_weight: float


class ScoringResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scholarship_id: int | None = None
    eligibility_status: str
    ranking_allowed: bool
    score: float | None
    score_scale: str = "0-100"
    scoring_policy_version: str
    excluded_reason: str | None = None
    evaluated_dimensions: int
    unknown_dimensions: int
    score_breakdown: list[ScoreBreakdown]
    summary: ScoringSummary


class RankingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scoring_policy_version: str
    results: list[ScoringResult]
    excluded_count: int
    excluded_ids: list[int]