from app.intelligence.eligibility.engine import evaluate_eligibility
from app.student.normalizers.country import normalize_country
from app.student.normalizers.education import normalize_education
from app.student.normalizers.field_of_study import normalize_field
from app.student.normalizers.income import normalize_income
from app.student.result import NormalizationStatus, ProfileNormalizationStatus, ValueState
from app.student.service import normalize_student_profile


def test_country_aliases_and_unknown_values_are_deterministic() -> None:
    assert normalize_country("country", "  INDIA ").normalized == "India"
    assert normalize_country("country", "USA").normalized == "United States"
    assert normalize_country("country", "MP").status == NormalizationStatus.AMBIGUOUS
    assert normalize_country("country", "Atlantis").status == NormalizationStatus.UNRESOLVED


def test_education_and_field_aliases() -> None:
    assert normalize_education("education_level", "B.Tech").normalized == "bachelor"
    assert normalize_education("education_level", "undergraduate").status == NormalizationStatus.UNCHANGED
    assert normalize_field("field_of_study", " Computer Science & Engineering ").normalized == "computer_science"
    assert normalize_field("field_of_study", "Quantum Textile Design").status == NormalizationStatus.UNRESOLVED


def test_income_formats_and_invalid_values() -> None:
    assert normalize_income("income", 300000).normalized == 300000
    assert normalize_income("income", "₹ 3,00,000").normalized == 300000
    assert normalize_income("income", "not money").status == NormalizationStatus.INVALID
    assert normalize_income("income", None).status == NormalizationStatus.MISSING


def test_missing_unknown_and_explicit_negative_remain_distinct() -> None:
    missing = normalize_student_profile({})
    unknown = normalize_student_profile({"country": "unknown"})
    negative = normalize_student_profile({"disability_status": False})
    assert missing.normalization["country"].status == NormalizationStatus.MISSING
    assert unknown.normalization["country"].value_state == ValueState.UNKNOWN
    assert negative.normalization["disability_status"].value_state == ValueState.EXPLICIT_NEGATIVE
    assert negative.profile.disability_status is False


def test_complete_profile_is_canonical_and_unresolved_values_are_preserved() -> None:
    result = normalize_student_profile(
        {
            "country": " india ",
            "education_level": "B.Tech",
            "degree": "Bachelor of Technology",
            "field_of_study": "CSE",
            "income": "₹ 3,00,000",
            "currency": "INR",
            "institution": "  Example College  ",
            "language": "EN",
        }
    )
    assert result.status == ProfileNormalizationStatus.NORMALIZED
    assert result.profile.country == "India"
    assert result.profile.education_level == "bachelor"
    assert result.profile.degree == "B.Tech"
    assert result.profile.field_of_study == "computer_science"
    assert result.profile.annual_family_income == 300000
    assert result.profile.income_currency == "INR"
    assert result.profile.institution == "Example College"

    unresolved = normalize_student_profile({"field_of_study": "Quantum Textile Design"})
    assert unresolved.profile.field_of_study is None
    assert unresolved.normalization["field_of_study"].cleaned == "Quantum Textile Design"
    assert unresolved.status == ProfileNormalizationStatus.PARTIALLY_NORMALIZED


def test_normalized_profile_preserves_phase_3_unknown_semantics() -> None:
    normalized = normalize_student_profile({"country": "India"})
    result = evaluate_eligibility(
        normalized.profile.model_dump(),
        [
            {"field": "country", "operator": "equals", "value": "India", "requirement_type": "hard"},
            {"field": "annual_family_income", "operator": "max", "value": 500000, "requirement_type": "hard"},
        ],
    )
    assert result.status.value == "POSSIBLY_ELIGIBLE"
