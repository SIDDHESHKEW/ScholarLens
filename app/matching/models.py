from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MatchStatus(str, Enum):
    MATCH = "MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"


class MatchFactor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension: str
    student_value: Any = None
    scholarship_value: Any = None
    status: MatchStatus
    explanation: str
    data_verification_status: str | None = None
    metadata: dict[str, Any] | None = None


class MatchSummary(BaseModel):
    matches: int
    partial_matches: int
    mismatches: int
    unknown: int


class SoftMatchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scholarship_id: int | None = None
    hard_eligibility_status: str
    matching_allowed: bool
    exclusion_reason: str | None = None
    match_factors: list[MatchFactor]
    matched_dimensions: list[str]
    partially_matched_dimensions: list[str]
    mismatched_dimensions: list[str]
    unknown_dimensions: list[str]
    summary: MatchSummary
    evidence_warnings: list[str] = Field(default_factory=list)