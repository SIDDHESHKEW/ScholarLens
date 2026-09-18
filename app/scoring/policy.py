from math import isfinite
from types import MappingProxyType
from typing import Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.matching.models import MatchStatus


class ScoringPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str = Field(min_length=1)
    weights: dict[str, float]
    contributions: dict[MatchStatus, float]

    @field_validator("weights")
    @classmethod
    def validate_weights(cls, value: dict[str, float]) -> dict[str, float]:
        known = {
            "field_of_study", "study_country", "education_level", "study_mode",
            "funding_preference", "institution_type", "language",
        }
        if not value or set(value) - known:
            raise ValueError("weights must contain only supported matching dimensions")
        if any(not isfinite(weight) or weight < 0 for weight in value.values()):
            raise ValueError("weights must be finite and non-negative")
        if round(sum(value.values()), 10) != 100:
            raise ValueError("weights must sum to 100")
        return value

    @field_validator("contributions")
    @classmethod
    def validate_contributions(cls, value: dict[MatchStatus, float]) -> dict[MatchStatus, float]:
        if set(value) != set(MatchStatus):
            raise ValueError("contributions must define every match status")
        if any(not isfinite(item) or item < 0 or item > 1 for item in value.values()):
            raise ValueError("contributions must be between 0 and 1")
        return value

    @model_validator(mode="after")
    def validate_version(self) -> "ScoringPolicy":
        if not self.version.strip():
            raise ValueError("scoring policy version is required")
        return self


DEFAULT_POLICY = ScoringPolicy(
    version="v1",
    weights={
        "field_of_study": 30,
        "study_country": 20,
        "education_level": 15,
        "funding_preference": 15,
        "study_mode": 10,
        "institution_type": 5,
        "language": 5,
    },
    contributions={
        MatchStatus.MATCH: 1.0,
        MatchStatus.PARTIAL_MATCH: 0.5,
        MatchStatus.MISMATCH: 0.0,
        MatchStatus.UNKNOWN: 0.0,
    },
)


def policy_weights() -> Mapping[str, float]:
    return MappingProxyType(DEFAULT_POLICY.weights)