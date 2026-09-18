import csv

import pytest

from app.pipeline.acquisition.csv_adapter import ScholarshipCSVAdapter, map_csv_row


def test_real_csv_is_readable_and_headers_are_valid() -> None:
    records, report = ScholarshipCSVAdapter("data/clean_scholarships.csv").read()
    assert report.records_seen == 811
    assert len(report.headers) == 39
    assert len(records) == 811


def test_not_specified_is_missing_and_free_text_is_not_a_rule() -> None:
    mapped = map_csv_row(
        {
            "scholarship_id": "TEST-1",
            "scholarship_name": "Synthetic Scholarship",
            "provider": "Synthetic Provider",
            "age_min": "21",
            "age_max": "Not specified",
            "minimum_percentage_or_gpa": "Passing marks",
            "family_income_limit": "Not specified",
            "education_level": "Any",
            "gender_eligibility": "Any",
            "eligibility_criteria": "Preference may be given to rural students.",
        }
    )
    assert {rule["field"] for rule in mapped["requirements"]} == {"age"}
    assert mapped["eligibility_evidence"]["eligibility_criteria"]["parsing_status"] == "UNPARSED"
    assert mapped["legacy_metadata"]["source_dataset"] == "clean_scholarships.csv"


def test_numeric_amount_and_identifier_are_mapped_without_guessing() -> None:
    mapped = map_csv_row(
        {
            "scholarship_id": "TEST-2",
            "scholarship_name": "Synthetic Scholarship",
            "scholarship_amount": "10000",
            "currency": " inr ",
        }
    )
    assert mapped["source_record_id"] == "TEST-2"
    assert mapped["amount"] == 10000
    assert mapped["currency"] == "inr"


def test_missing_required_header_is_rejected(tmp_path) -> None:
    path = tmp_path / "invalid.csv"
    path.write_text("scholarship_name\nExample\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required headers"):
        ScholarshipCSVAdapter(path).read()