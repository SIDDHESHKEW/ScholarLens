import csv
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.pipeline.acquisition.base import RawRecord

SOURCE_COLUMNS = {
    "scholarship_id", "scholarship_name", "provider", "provider_type", "source",
    "official_source_url", "application_url", "country_of_provider", "study_country",
    "eligible_nationalities", "education_level", "study_mode", "field_of_study",
    "age_min", "age_max", "academic_requirement", "minimum_percentage_or_gpa",
    "family_income_limit", "gender_eligibility", "category_eligibility",
    "disability_eligibility", "residency_requirement", "scholarship_amount", "currency",
    "funding_type", "tuition_coverage", "living_expense_coverage", "travel_coverage",
    "accommodation_coverage", "application_fee", "application_deadline",
    "scholarship_duration", "number_of_awards", "documents_required", "eligibility_criteria",
    "selection_criteria", "description", "renewable", "last_verified",
}

SENTINELS = {"", "not specified", "n/a", "na", "none", "not applicable", "unknown", "-"}


@dataclass
class CSVReadReport:
    records_seen: int = 0
    records_skipped: int = 0
    errors: list[str] = field(default_factory=list)
    headers: list[str] = field(default_factory=list)


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", str(value)).strip()
    return None if cleaned.casefold() in SENTINELS else cleaned


def _number(value: str | None) -> int | float | None:
    cleaned = _clean(value)
    if cleaned is None:
        return None
    match = re.fullmatch(r"\d+(?:\.\d+)?", cleaned.replace(",", ""))
    if not match:
        return None
    numeric = float(match.group())
    return int(numeric) if numeric.is_integer() else numeric


def _numeric_rule(field: str, operator: str, value: str | None) -> dict[str, Any] | None:
    numeric = _number(value)
    if numeric is None:
        return None
    return {
        "field": field,
        "operator": operator,
        "value": numeric,
        "requirement_type": "hard",
        "source_reference": "clean_scholarships.csv",
    }


def _equality_rule(field: str, value: str | None) -> dict[str, Any] | None:
    cleaned = _clean(value)
    if cleaned is None or cleaned.casefold() in {"any", "all", "international"}:
        return None
    return {
        "field": field,
        "operator": "equals",
        "value": cleaned,
        "requirement_type": "hard",
        "source_reference": "clean_scholarships.csv",
    }


def map_csv_row(row: dict[str, str]) -> dict[str, Any]:
    cleaned = {key: _clean(value) for key, value in row.items()}
    requirements = [
        rule for rule in (
            _numeric_rule("age", "min", cleaned.get("age_min")),
            _numeric_rule("age", "max", cleaned.get("age_max")),
            _numeric_rule("academic_percentage", "min", cleaned.get("minimum_percentage_or_gpa")),
            _numeric_rule("family_income", "max", cleaned.get("family_income_limit")),
            _equality_rule("education_level", cleaned.get("education_level")),
            _equality_rule("gender", cleaned.get("gender_eligibility")),
        ) if rule is not None
    ]
    evidence = {
        field: {"raw_text": cleaned.get(field), "parsing_status": "UNPARSED"}
        for field in ("academic_requirement", "eligibility_criteria", "selection_criteria", "documents_required")
        if cleaned.get(field) is not None
    }
    return {
        "source_record_id": cleaned.get("scholarship_id"),
        "name": cleaned.get("scholarship_name"),
        "provider": cleaned.get("provider"),
        "description": cleaned.get("description"),
        "official_source_url": cleaned.get("official_source_url"),
        "application_url": cleaned.get("application_url"),
        "amount": _number(cleaned.get("scholarship_amount")),
        "currency": cleaned.get("currency"),
        "deadline": cleaned.get("application_deadline"),
        "status": "unknown",
        "requirements": requirements or None,
        "eligibility_evidence": evidence or None,
        "legacy_metadata": {
            "source_dataset": "clean_scholarships.csv",
            "source_value": cleaned.get("source"),
            "provider_type": cleaned.get("provider_type"),
            "study_country": cleaned.get("study_country"),
            "eligible_nationalities": cleaned.get("eligible_nationalities"),
            "education_level": cleaned.get("education_level"),
            "study_mode": cleaned.get("study_mode"),
            "field_of_study": cleaned.get("field_of_study"),
            "institution_type": cleaned.get("provider_type"),
            "funding_type": cleaned.get("funding_type"),
            "last_verified_source_value": cleaned.get("last_verified"),
            "raw_fields": cleaned,
        },
    }


class ScholarshipCSVAdapter:
    source_name = "clean_scholarships.csv"
    source_type = "dataset"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def read(self) -> tuple[list[RawRecord], CSVReadReport]:
        report = CSVReadReport()
        records: list[RawRecord] = []
        retrieved_at = datetime.now(timezone.utc)
        with self.path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            report.headers = reader.fieldnames or []
            missing = SOURCE_COLUMNS - set(report.headers)
            if missing:
                raise ValueError(f"CSV is missing required headers: {sorted(missing)}")
            for row_number, row in enumerate(reader, start=2):
                report.records_seen += 1
                if not row.get("scholarship_name") or not _clean(row.get("scholarship_name")):
                    report.records_skipped += 1
                    report.errors.append(f"row {row_number}: missing scholarship_name")
                    continue
                payload = map_csv_row(row)
                payload["legacy_metadata"]["raw_fields"] = dict(row)
                records.append(
                    RawRecord(
                        payload=payload,
                        source_name=self.source_name,
                        source_type=self.source_type,
                        source_url=payload.get("official_source_url"),
                        retrieved_at=retrieved_at,
                    )
                )
        return records, report