from dataclasses import dataclass, field
from datetime import date, datetime, timezone
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import RawScholarshipRecord, Scholarship, ScholarshipSource
from app.pipeline.acquisition.base import AcquisitionResult, RawRecord
from app.pipeline.cleaning.cleaner import clean_record
from app.pipeline.deduplication.deduplicator import fingerprint
from app.pipeline.normalization.normalizer import normalize_record
from app.repositories.scholarship_repository import ScholarshipRepository

logger = logging.getLogger(__name__)


@dataclass
class IngestionReport:
    records_seen: int = 0
    records_cleaned: int = 0
    records_normalized: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    duplicates_detected: int = 0
    records_requiring_review: int = 0
    records_failed: int = 0
    records_skipped: int = 0
    legacy_fields_ignored: int = 0
    errors: list[str] = field(default_factory=list)


class ScholarshipIngestionPipeline:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ScholarshipRepository(session)

    def process(self, records: list[RawRecord]) -> IngestionReport:
        report = IngestionReport(records_seen=len(records))
        logger.info("records_fetched=%d", len(records))
        for raw_record in records:
            raw_entry = RawScholarshipRecord(
                source_name=raw_record.source_name,
                source_type=raw_record.source_type,
                source_url=raw_record.source_url,
                retrieved_at=raw_record.retrieved_at,
                raw_payload=raw_record.payload,
                content_hash=raw_record.content_hash,
                ingestion_status="discovered",
            )
            self.session.add(raw_entry)
            try:
                cleaned = clean_record(raw_record.payload)
                report.records_cleaned += 1
                normalized, warnings = normalize_record(cleaned)
                report.records_normalized += 1
                if not normalized.get("name"):
                    raise ValueError("missing name")
                scholarship, inserted = self._upsert(normalized, raw_record, warnings)
                raw_entry.ingestion_status = "stored"
                if inserted:
                    report.records_inserted += 1
                else:
                    report.records_updated += 1
                    report.duplicates_detected += 1
                if scholarship.data_quality == "needs_review":
                    report.records_requiring_review += 1
            except (TypeError, ValueError, KeyError) as error:
                raw_entry.ingestion_status = "failed"
                raw_entry.error_message = str(error)
                report.records_failed += 1
                report.errors.append(str(error))
        self.session.commit()
        logger.info(
            "records_processed=%d records_inserted=%d records_updated=%d duplicates=%d errors=%d",
            report.records_normalized,
            report.records_inserted,
            report.records_updated,
            report.duplicates_detected,
            report.records_failed,
        )
        return report

    def process_acquisition(self, result: AcquisitionResult) -> IngestionReport:
        if result.raw_content is not None:
            self.session.add(
                RawScholarshipRecord(
                    source_name=result.source_name,
                    source_type=result.source_type,
                    source_url=result.source_url,
                    retrieved_at=result.retrieved_at,
                    raw_content=result.raw_content,
                    content_hash=result.content_hash or "",
                    ingestion_status="fetched",
                )
            )
            self.session.commit()
        return self.process(result.records)

    def _upsert(
        self, record: dict[str, Any], raw_record: RawRecord, warnings: list[str]
    ) -> tuple[Scholarship, bool]:
        record_fingerprint = fingerprint(record)
        scholarship = self.repository.find_by_fingerprint(record_fingerprint)
        source_status = record.get("status") if record.get("status") != "unknown" else None
        status = source_status or "unknown"
        status_derived = False
        deadline = record.get("deadline")
        if (
            raw_record.source_type != "dataset"
            and not source_status
            and isinstance(deadline, date)
            and deadline < date.today()
        ):
            status = "expired"
            status_derived = True

        quality_issues = list(warnings)
        for field_name, message in (
            ("provider", "missing provider"),
            ("official_source_url", "missing source URL"),
            ("deadline", "missing deadline"),
            ("application_url", "missing application URL"),
            ("description", "missing description"),
            ("requirements", "missing requirements"),
        ):
            if not record.get(field_name):
                quality_issues.append(message)
        quality = "complete" if not quality_issues else "partial"
        if warnings or not record.get("official_source_url"):
            quality = "needs_review"

        values = {
            "name": record["name"],
            "provider": record.get("provider"),
            "description": record.get("description"),
            "official_source_url": record.get("official_source_url"),
            "application_url": record.get("application_url"),
            "amount": record.get("amount"),
            "currency": record.get("currency"),
            "deadline": deadline,
            "status": status,
            "source_status": source_status,
            "status_derived": status_derived,
            "requirements": record.get("requirements"),
            "eligibility_evidence": record.get("eligibility_evidence"),
            "legacy_metadata": record.get("legacy_metadata"),
            "source_record_id": record.get("source_record_id"),
            "data_quality": quality,
            "quality_issues": quality_issues,
            "fingerprint": record_fingerprint,
        }
        inserted = scholarship is None
        if inserted:
            scholarship = Scholarship(**values)
            self.repository.save(scholarship)
        else:
            for key, value in values.items():
                setattr(scholarship, key, value)
        self.repository.add_source(
            ScholarshipSource(
                scholarship_id=scholarship.id,
                source_name=raw_record.source_name,
                source_type=raw_record.source_type,
                source_url=raw_record.source_url,
                retrieved_at=raw_record.retrieved_at,
                content_hash=raw_record.content_hash,
                verification_status="unverified",
                source_status=source_status,
            )
        )
        return scholarship, inserted


def raw_record_from_mapping(
    payload: dict[str, Any], *, source_name: str, source_type: str,
    source_url: str | None = None,
) -> RawRecord:
    return RawRecord(
        payload=payload,
        source_name=source_name,
        source_type=source_type,
        source_url=source_url,
        retrieved_at=datetime.now(timezone.utc),
    )