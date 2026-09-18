from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

from app.intelligence.eligibility.result import EligibilityEvaluation, EligibilityStatus


class EvidenceType(str, Enum):
    EDUCATION_LEVEL_SIGNAL = "EDUCATION_LEVEL_SIGNAL"
    PROGRAM_LEVEL_SIGNAL = "PROGRAM_LEVEL_SIGNAL"
    AGE_SIGNAL = "AGE_SIGNAL"
    FIELD_OF_STUDY_SIGNAL = "FIELD_OF_STUDY_SIGNAL"
    OTHER_HARD_REQUIREMENT_SIGNAL = "OTHER_HARD_REQUIREMENT_SIGNAL"


class EvidenceConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DataQualityStatus(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    CONTRADICTORY = "CONTRADICTORY"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class EligibilityEvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_type: EvidenceType
    detected_value: str
    confidence: EvidenceConfidence
    source_field: str
    text_excerpt: str
    reason: str


class EvidenceEvaluationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    has_contradiction: bool
    contradiction_reason: str | None = None
    contradicted_field: str | None = None
    detected_signals: list[EligibilityEvidenceItem] = Field(default_factory=list)
    data_quality_status: DataQualityStatus
    warnings: list[str] = Field(default_factory=list)


class HardenedEligibilityResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: EligibilityStatus
    explanation: str
    structured_evaluation: EligibilityEvaluation
    evidence_evaluation: EvidenceEvaluationResult
