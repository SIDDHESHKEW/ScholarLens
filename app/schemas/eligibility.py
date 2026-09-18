
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RequirementType(str, Enum):
    HARD = "hard"
    SOFT = "soft"


class RuleOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    IN = "in"
    NOT_IN = "not_in"
    MIN = "min"
    MAX = "max"
    CONTAINS = "contains"
    UNKNOWN = "unknown"


class EligibilityRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(min_length=1)
    operator: RuleOperator
    value: Any = None
    requirement_type: RequirementType
    source_reference: str | None = None

    @field_validator("field")
    @classmethod
    def field_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be blank")
        return value