
from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.schemas.eligibility import EligibilityRule


class EducationLevel(str, Enum):
    SCHOOL = "school"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    HIGHER_SECONDARY = "higher_secondary"
    DIPLOMA = "diploma"
    BACHELOR = "bachelor"
    UNDERGRADUATE = "undergraduate"
    MASTER = "master"
    POSTGRADUATE = "postgraduate"
    PHD = "phd"
    DOCTORAL = "doctoral"
    POSTDOCTORAL = "postdoctoral"
    VOCATIONAL = "vocational"
    CERTIFICATE = "certificate"
    OTHER = "other"


class ScholarshipStatus(str, Enum):
    UNKNOWN = "unknown"
    ACTIVE = "active"
    EXPIRED = "expired"
    UPCOMING = "upcoming"
    CLOSED = "closed"


class SourceType(str, Enum):
    OFFICIAL = "official"
    GOVERNMENT = "government"
    INSTITUTIONAL = "institutional"
    SECONDARY = "secondary"
    DATASET = "dataset"
    UNKNOWN = "unknown"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    NEEDS_REVIEW = "needs_review"


class DataQualityStatus(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    NEEDS_REVIEW = "needs_review"


class StudentProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age: int | None = Field(default=None, ge=0)
    country: str | None = None
    nationality: str | None = None
    residence_country: str | None = None
    study_country: str | None = None
    country_of_residence: str | None = None
    education_level: EducationLevel | None = None
    academic_percentage: float | None = Field(default=None, ge=0, le=100)
    gpa: float | None = Field(default=None, ge=0)
    field_of_study: str | None = None
    degree: str | None = None
    program: str | None = None
    institution: str | None = None
    study_mode: str | None = None
    year_of_study: int | None = Field(default=None, ge=0)
    family_income: float | None = Field(default=None, ge=0)
    family_income_currency: str | None = None
    annual_family_income: float | None = Field(default=None, ge=0)
    income_currency: str | None = None
    gender: str | None = None
    category: str | None = None
    student_category: str | None = None
    disability_status: bool | None = None
    preferred_study_country: str | None = None
    current_study_country: str | None = None
    degree_or_program: str | None = None
    institution_type: str | None = None
    language: str | None = None
    language_proficiency: dict[str, str] | None = None
    funding_preference: str | None = None
    preferred_funding_type: str | None = None
    extra_attributes: dict[str, Any] | None = None


class ScholarshipCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    provider: str | None = None
    description: str | None = None
    official_source_url: HttpUrl | None = None
    application_url: HttpUrl | None = None
    amount: float | None = Field(default=None, ge=0)
    currency: str | None = None
    deadline: date | None = None
    status: ScholarshipStatus = ScholarshipStatus.UNKNOWN
    requirements: list[EligibilityRule] | None = None
    eligibility_evidence: dict[str, Any] | None = None
    legacy_metadata: dict[str, Any] | None = None
    source_record_id: str | None = None


class ScholarshipRead(ScholarshipCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    source_status: ScholarshipStatus | None = None
    status_derived: bool = False
    data_quality: DataQualityStatus
    quality_issues: list[str] = Field(default_factory=list)
    provenance: list["ScholarshipSourceRead"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ScholarshipSourceRead(BaseModel):
    id: int
    source_name: str
    source_type: SourceType
    source_url: HttpUrl | None = None
    retrieved_at: datetime
    verified_at: datetime | None = None
    content_hash: str | None = None
    verification_status: VerificationStatus
    source_status: ScholarshipStatus | None = None

    model_config = ConfigDict(from_attributes=True)