from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.eligibility import RequirementType, RuleOperator


class RuleResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class EligibilityStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    POSSIBLY_ELIGIBLE = "POSSIBLY_ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class RuleEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    operator: RuleOperator
    required_value: Any = None
    actual_value: Any = None
    requirement_type: RequirementType
    result: RuleResult
    reason: str
    source_reference: str | None = None
    issue: str | None = None


class EligibilityEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: EligibilityStatus
    evaluated_rules: list[RuleEvaluation]
    passed_rules: list[RuleEvaluation]
    failed_rules: list[RuleEvaluation]
    unknown_rules: list[RuleEvaluation]
    explanation: str