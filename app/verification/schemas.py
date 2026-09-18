from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class VerificationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    CONTRADICTED = "CONTRADICTED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    STALE = "STALE"


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class ClaimStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    CONTRADICTED = "CONTRADICTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class VerificationEvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_url: str
    source_type: str
    authority_level: str
    retrieved_at: datetime
    content_hash: str | None
    relevant_excerpt: str | None
    accessibility_status: str


class VerificationClaimRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    field_name: str
    claimed_value: Any = None
    verified_value: Any = None
    status: ClaimStatus
    evidence_id: int | None
    notes: str | None


class VerificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scholarship_id: int
    verification_status: VerificationStatus
    freshness_status: FreshnessStatus
    verifier_method: str
    verified_at: datetime
    notes: str | None
    claims: list[VerificationClaimRead]
    evidence: list[VerificationEvidenceRead]