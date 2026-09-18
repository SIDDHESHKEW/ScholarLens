from datetime import date

from app.pipeline.normalization.normalizer import (
    normalize_country,
    normalize_date,
    normalize_education_level,
    normalize_percentage,
)


def test_normalize_canonical_values() -> None:
    assert normalize_country("IND") == "India"
    assert normalize_education_level("Under Graduate") == "undergraduate"
    assert normalize_percentage("87.5%") == 87.5


def test_normalize_dates_without_guessing() -> None:
    assert normalize_date("2026-08-31") == (date(2026, 8, 31), None)
    assert normalize_date("31/08/2026") == (None, "ambiguous deadline format")
    assert normalize_date(None) == (None, None)
