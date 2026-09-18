import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Scholarship, VerificationClaim, VerificationEvidence, VerificationRecord
from app.verification.fetcher import FetchResult, fetch_source
from app.verification.schemas import ClaimStatus, FreshnessStatus, VerificationStatus


AUTHORITY = {"government": "government", "official": "provider", "institutional": "institution", "dataset": "historical", "secondary": "secondary", "unknown": "unknown"}


def freshness(verified_at: datetime | None, max_age_days: int = 30) -> FreshnessStatus:
    if verified_at is None:
        return FreshnessStatus.UNKNOWN
    age_days = (datetime.now(timezone.utc) - verified_at.replace(tzinfo=timezone.utc)).days
    return FreshnessStatus.STALE if age_days > max_age_days else FreshnessStatus.FRESH


def _page_matches_scholarship(scholarship: Scholarship, content: str) -> bool:
    visible = re.sub(r"<[^>]+>", " ", content).casefold()
    return scholarship.name.casefold() in visible or (scholarship.provider and scholarship.provider.casefold() in visible)


class ScholarshipVerificationService:
    def __init__(self, session: Session, *, max_age_days: int | None = None) -> None:
        self.session = session
        self.max_age_days = max_age_days if max_age_days is not None else settings.verification_max_age_days

    def verify(self, scholarship: Scholarship, *, url: str | None = None, fetcher=fetch_source) -> VerificationRecord:
        source_url = url or scholarship.official_source_url or scholarship.application_url
        now = datetime.now(timezone.utc)
        if not source_url:
            record = VerificationRecord(scholarship_id=scholarship.id, verification_status=VerificationStatus.SOURCE_UNAVAILABLE.value, freshness_status=FreshnessStatus.UNKNOWN.value, verifier_method="controlled_url_fetch", verified_at=now, notes="No stored source URL.")
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
            return record
        result: FetchResult = fetcher(source_url)
        if not result.success:
            record = VerificationRecord(scholarship_id=scholarship.id, verification_status=VerificationStatus.SOURCE_UNAVAILABLE.value, freshness_status=FreshnessStatus.UNKNOWN.value, verifier_method="controlled_url_fetch", verified_at=now, notes=result.error)
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
            return record
        matches = _page_matches_scholarship(scholarship, result.content)
        overall = VerificationStatus.PARTIALLY_VERIFIED if matches else VerificationStatus.NEEDS_REVIEW
        record = VerificationRecord(scholarship_id=scholarship.id, verification_status=overall.value, freshness_status=FreshnessStatus.FRESH.value, verifier_method="controlled_url_fetch", verified_at=now, notes="Page fetched; claim values require claim-level evidence." if matches else "Fetched page did not clearly identify this scholarship.")
        self.session.add(record)
        self.session.flush()
        evidence = VerificationEvidence(verification_id=record.id, source_url=result.url, source_type="web", authority_level="unknown", retrieved_at=now, content_hash=result.content_hash, relevant_excerpt=None, accessibility_status="accessible")
        self.session.add(evidence)
        self.session.flush()
        fields = {"name": scholarship.name, "provider": scholarship.provider, "amount": scholarship.amount, "deadline": scholarship.deadline.isoformat() if scholarship.deadline else None, "application_url": scholarship.application_url}
        for field_name, claimed in fields.items():
            status = ClaimStatus.VERIFIED.value if matches and field_name in {"name", "provider"} else ClaimStatus.NEEDS_REVIEW.value
            self.session.add(VerificationClaim(verification_id=record.id, scholarship_id=scholarship.id, field_name=field_name, claimed_value=claimed, verified_value=claimed if status == ClaimStatus.VERIFIED.value else None, status=status, evidence_id=evidence.id, notes="Identity matched on fetched page." if status == ClaimStatus.VERIFIED.value else "No deterministic claim comparison performed."))
        self.session.commit()
        self.session.refresh(record)
        return record

    def history(self, scholarship_id: int) -> list[VerificationRecord]:
        return list(self.session.scalars(select(VerificationRecord).where(VerificationRecord.scholarship_id == scholarship_id).order_by(VerificationRecord.verified_at.desc())))