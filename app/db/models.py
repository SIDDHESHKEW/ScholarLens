
from datetime import date, datetime
from typing import Any

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Scholarship(Base):
    __tablename__ = "scholarships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    official_source_url: Mapped[str | None] = mapped_column(String(2048))
    application_url: Mapped[str | None] = mapped_column(String(2048))
    amount: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str | None] = mapped_column(String(16))
    deadline: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    source_status: Mapped[str | None] = mapped_column(String(32))
    status_derived: Mapped[bool] = mapped_column(nullable=False, default=False)
    requirements: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON)
    eligibility_evidence: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    legacy_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    source_record_id: Mapped[str | None] = mapped_column(String(255))
    data_quality: Mapped[str] = mapped_column(String(32), nullable=False, default="needs_review")
    quality_issues: Mapped[list[str] | None] = mapped_column(JSON)
    fingerprint: Mapped[str | None] = mapped_column(String(128), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class RawScholarshipRecord(Base):
    __tablename__ = "raw_scholarship_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048))
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    raw_content: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    ingestion_status: Mapped[str] = mapped_column(String(32), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)


class ScholarshipSource(Base):
    __tablename__ = "scholarship_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scholarship_id: Mapped[int] = mapped_column(
        ForeignKey("scholarships.id", ondelete="CASCADE"), nullable=False
    )
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048))
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[str | None] = mapped_column(String(128))
    verification_status: Mapped[str] = mapped_column(String(32), nullable=False)
    source_status: Mapped[str | None] = mapped_column(String(32))


class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scholarship_id: Mapped[int] = mapped_column(ForeignKey("scholarships.id", ondelete="CASCADE"), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(32), nullable=False)
    freshness_status: Mapped[str] = mapped_column(String(16), nullable=False, default="UNKNOWN")
    verifier_method: Mapped[str] = mapped_column(String(64), nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class VerificationEvidence(Base):
    __tablename__ = "verification_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    verification_id: Mapped[int] = mapped_column(ForeignKey("verification_records.id", ondelete="CASCADE"), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    authority_level: Mapped[str] = mapped_column(String(32), nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    content_hash: Mapped[str | None] = mapped_column(String(128))
    relevant_excerpt: Mapped[str | None] = mapped_column(Text)
    accessibility_status: Mapped[str] = mapped_column(String(32), nullable=False)


class VerificationClaim(Base):
    __tablename__ = "verification_claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    verification_id: Mapped[int] = mapped_column(ForeignKey("verification_records.id", ondelete="CASCADE"), nullable=False)
    scholarship_id: Mapped[int] = mapped_column(ForeignKey("scholarships.id", ondelete="CASCADE"), nullable=False)
    field_name: Mapped[str] = mapped_column(String(128), nullable=False)
    claimed_value: Mapped[Any | None] = mapped_column(JSON)
    verified_value: Mapped[Any | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    evidence_id: Mapped[int | None] = mapped_column(ForeignKey("verification_evidence.id"))
    notes: Mapped[str | None] = mapped_column(Text)