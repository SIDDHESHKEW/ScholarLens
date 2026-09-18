from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.student.profile import CanonicalStudentProfile


class NormalizationStatus(str, Enum):
    NORMALIZED = "NORMALIZED"
    UNCHANGED = "UNCHANGED"
    UNRESOLVED = "UNRESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    INVALID = "INVALID"
    MISSING = "MISSING"


class ValueState(str, Enum):
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"
    EXPLICIT_NEGATIVE = "EXPLICIT_NEGATIVE"
    PRESENT = "PRESENT"


class NormalizationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    original: Any = None
    cleaned: Any = None
    normalized: Any = None
    status: NormalizationStatus
    method: str | None = None
    value_state: ValueState = ValueState.PRESENT
    issue: str | None = None


class ProfileNormalizationStatus(str, Enum):
    NORMALIZED = "NORMALIZED"
    PARTIALLY_NORMALIZED = "PARTIALLY_NORMALIZED"
    INVALID = "INVALID"


class ProfileNormalizationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: CanonicalStudentProfile
    normalization: dict[str, NormalizationResult]
    issues: list[str]
    status: ProfileNormalizationStatus