from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RawStudentProfile(BaseModel):
    """Validated transport shape for user-provided, not-yet-canonical values."""

    model_config = ConfigDict(extra="forbid")

    age: Any = None
    country: Any = None
    nationality: Any = None
    residence_country: Any = None
    country_of_residence: Any = None
    study_country: Any = None
    preferred_study_country: Any = None
    current_study_country: Any = None
    education_level: Any = None
    degree: Any = None
    degree_or_program: Any = None
    program: Any = None
    field_of_study: Any = None
    institution: Any = None
    institution_type: Any = None
    study_mode: Any = None
    year_of_study: Any = None
    academic_percentage: Any = None
    gpa: Any = None
    family_income: Any = None
    annual_family_income: Any = None
    income: Any = None
    family_income_currency: Any = None
    income_currency: Any = None
    currency: Any = None
    gender: Any = None
    category: Any = None
    student_category: Any = None
    disability_status: Any = None
    disability: Any = None
    language: Any = None
    language_proficiency: Any = None
    funding_preference: Any = None
    preferred_funding_type: Any = None
    extra_attributes: dict[str, Any] | None = None


class CanonicalStudentProfile(BaseModel):
    """Canonical values consumed by the Phase 3 eligibility engine."""

    model_config = ConfigDict(extra="forbid")

    age: int | None = Field(default=None, ge=0)
    country: str | None = None
    nationality: str | None = None
    residence_country: str | None = None
    study_country: str | None = None
    preferred_study_country: str | None = None
    current_study_country: str | None = None
    country_of_residence: str | None = None
    education_level: str | None = None
    degree: str | None = None
    degree_or_program: str | None = None
    program: str | None = None
    field_of_study: str | None = None
    institution: str | None = None
    institution_type: str | None = None
    study_mode: str | None = None
    year_of_study: int | None = Field(default=None, ge=0)
    academic_percentage: float | None = Field(default=None, ge=0, le=100)
    gpa: float | None = Field(default=None, ge=0)
    family_income: float | None = Field(default=None, ge=0)
    family_income_currency: str | None = None
    annual_family_income: float | None = Field(default=None, ge=0)
    income_currency: str | None = None
    gender: str | None = None
    category: str | None = None
    student_category: str | None = None
    disability_status: bool | None = None
    language: str | None = None
    language_proficiency: dict[str, str] | None = None
    funding_preference: str | None = None
    preferred_funding_type: str | None = None
    extra_attributes: dict[str, Any] | None = None