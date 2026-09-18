import logging
from typing import Any, Callable

from app.student.normalizers.base import aliased_result, clean_text, missing_result, unresolved_result, value_state
from app.student.normalizers.category import normalize_category
from app.student.normalizers.country import normalize_country
from app.student.normalizers.degree import normalize_degree
from app.student.normalizers.education import normalize_education
from app.student.normalizers.field_of_study import normalize_field
from app.student.normalizers.income import normalize_currency, normalize_income
from app.student.normalizers.institution import normalize_institution, normalize_institution_type
from app.student.normalizers.language import normalize_language
from app.student.profile import CanonicalStudentProfile, RawStudentProfile
from app.student.result import (
    NormalizationResult,
    NormalizationStatus,
    ProfileNormalizationResponse,
    ProfileNormalizationStatus,
    ValueState,
)

logger = logging.getLogger(__name__)


def _missing_or(value: Any, field: str) -> NormalizationResult | None:
    if value is None:
        return missing_result(field, value)
    return None


def _text(field: str, value: Any) -> NormalizationResult:
    missing = _missing_or(value, field)
    if missing:
        return missing
    cleaned = clean_text(value)
    if cleaned is None:
        return unresolved_result(field, value, None, "Value must be text.")
    return aliased_result(field, value, cleaned, cleaned, "safe_cleanup")


def _number(field: str, value: Any, *, minimum: float | None = None, maximum: float | None = None) -> NormalizationResult:
    missing = _missing_or(value, field)
    if missing:
        return missing
    if isinstance(value, bool):
        return unresolved_result(field, value, None, "Value must be numeric.")
    try:
        numeric = float(str(value).strip())
    except (TypeError, ValueError):
        return unresolved_result(field, value, clean_text(value), "Value must be numeric.")
    if minimum is not None and numeric < minimum or maximum is not None and numeric > maximum:
        return NormalizationResult(
            field=field, original=value, cleaned=str(value).strip(), status=NormalizationStatus.INVALID,
            method="range_validation", value_state=value_state(value), issue="Value is outside the valid range.",
        )
    normalized: int | float = int(numeric) if numeric.is_integer() else numeric
    return aliased_result(field, value, str(value).strip(), normalized, "numeric_parse")


def _boolean(field: str, value: Any) -> NormalizationResult:
    missing = _missing_or(value, field)
    if missing:
        return missing
    if isinstance(value, bool):
        return aliased_result(field, value, value, value, "boolean_unchanged")
    cleaned = clean_text(value)
    if cleaned and cleaned.casefold() in {"true", "yes", "y", "1"}:
        return aliased_result(field, value, cleaned, True, "boolean_alias")
    if cleaned and cleaned.casefold() in {"false", "no", "n", "0"}:
        result = aliased_result(field, value, cleaned, False, "boolean_alias")
        result.value_state = ValueState.EXPLICIT_NEGATIVE
        return result
    return unresolved_result(field, value, cleaned, "Boolean value is unresolved.")


FUNDING_ALIASES = {
    "full": "full",
    "fully funded": "full",
    "fully_funded": "full",
    "full funding": "full",
    "full_funding": "full",
    "partial": "partial",
    "partially funded": "partial",
    "partially_funded": "partial",
    "partial funding": "partial",
    "partial_funding": "partial",
    "tuition": "tuition",
    "tuition only": "tuition",
    "tuition_only": "tuition",
    "tuition and living": "tuition_and_living",
    "tuition_and_living": "tuition_and_living",
    "tuition & living": "tuition_and_living",
    "stipend": "stipend",
    "grant": "grant",
    "fellowship": "fellowship",
}


def normalize_funding(field: str, value: Any) -> NormalizationResult:
    missing = _missing_or(value, field)
    if missing:
        return missing
    cleaned = clean_text(value)
    if cleaned is None:
        return unresolved_result(field, value, None, "Value must be text.")
    lower = cleaned.casefold().replace("-", " ").strip()
    canonical = FUNDING_ALIASES.get(lower, cleaned.casefold().replace(" ", "_"))
    return aliased_result(field, value, cleaned, canonical, "funding_alias")


class StudentProfileNormalizationService:
    def normalize(self, raw_profile: RawStudentProfile | dict[str, Any]) -> ProfileNormalizationResponse:
        raw = raw_profile if isinstance(raw_profile, RawStudentProfile) else RawStudentProfile.model_validate(raw_profile)
        source = raw.model_dump()
        supplied = raw.model_fields_set
        results: dict[str, NormalizationResult] = {}
        canonical: dict[str, Any] = {}

        def run(field: str, normalizer: Callable[[str, Any], NormalizationResult], source_field: str | None = None) -> None:
            key = source_field or field
            value = source.get(key) if key in supplied else None
            result = normalizer(field, value)
            results[field] = result
            if result.normalized is not None:
                canonical[field] = result.normalized

        for field in ("country", "nationality", "residence_country", "study_country", "preferred_study_country", "current_study_country", "country_of_residence"):
            run(field, normalize_country)
        run("education_level", normalize_education)
        run("degree", normalize_degree)
        run("degree_or_program", normalize_degree)
        run("field_of_study", normalize_field)
        run("category", normalize_category)
        run("student_category", normalize_category)
        run("institution", normalize_institution)
        run("institution_type", normalize_institution_type)
        run("language", normalize_language)
        run("study_mode", _text)
        run("program", _text)
        run("gender", _text)
        run("age", lambda field, value: _number(field, value, minimum=0))
        run("year_of_study", lambda field, value: _number(field, value, minimum=0))
        run("academic_percentage", lambda field, value: _number(field, value, minimum=0, maximum=100))
        run("gpa", lambda field, value: _number(field, value, minimum=0))
        run("disability_status", _boolean)

        funding_source = next((name for name in ("funding_preference", "preferred_funding_type") if name in supplied), None)
        funding_result = normalize_funding("funding_preference", source.get(funding_source) if funding_source else None)
        results["funding_preference"] = funding_result
        if funding_result.normalized is not None:
            canonical["funding_preference"] = funding_result.normalized
            canonical["preferred_funding_type"] = funding_result.normalized

        income_source = next((name for name in ("annual_family_income", "family_income", "income") if name in supplied), None)
        income_result = normalize_income("annual_family_income", source.get(income_source) if income_source else None)
        results["annual_family_income"] = income_result
        if income_result.normalized is not None:
            canonical["annual_family_income"] = income_result.normalized
            canonical["family_income"] = income_result.normalized
        currency_source = next((name for name in ("income_currency", "family_income_currency", "currency") if name in supplied), None)
        currency_result = normalize_currency("income_currency", source.get(currency_source) if currency_source else None)
        results["income_currency"] = currency_result
        if currency_result.normalized is not None:
            canonical["income_currency"] = currency_result.normalized
            canonical["family_income_currency"] = currency_result.normalized

        language_proficiency = source.get("language_proficiency") if "language_proficiency" in supplied else None
        if language_proficiency is None:
            results["language_proficiency"] = missing_result("language_proficiency")
        elif not isinstance(language_proficiency, dict):
            results["language_proficiency"] = unresolved_result(
                "language_proficiency", language_proficiency, None, "Language proficiency must be an object."
            )
        else:
            normalized_languages = {}
            for language, proficiency in language_proficiency.items():
                language_result = normalize_language("language", language)
                normalized_languages[language_result.normalized or str(language)] = str(proficiency).strip()
            results["language_proficiency"] = aliased_result(
                "language_proficiency", language_proficiency, language_proficiency, normalized_languages, "nested_language_normalization"
            )
            canonical["language_proficiency"] = normalized_languages

        if "extra_attributes" in supplied and source["extra_attributes"] is not None:
            if isinstance(source["extra_attributes"], dict):
                canonical["extra_attributes"] = source["extra_attributes"]
                results["extra_attributes"] = aliased_result(
                    "extra_attributes", source["extra_attributes"], source["extra_attributes"], source["extra_attributes"], "preserved"
                )
            else:
                results["extra_attributes"] = unresolved_result(
                    "extra_attributes", source["extra_attributes"], None, "Extra attributes must be an object."
                )
        else:
            results["extra_attributes"] = missing_result("extra_attributes")

        issues = [f"{field}: {result.issue}" for field, result in results.items() if result.issue]
        invalid = any(result.status == NormalizationStatus.INVALID for result in results.values())
        partial = any(result.status in {NormalizationStatus.UNRESOLVED, NormalizationStatus.AMBIGUOUS, NormalizationStatus.INVALID} for result in results.values())
        overall = ProfileNormalizationStatus.INVALID if invalid else (
            ProfileNormalizationStatus.PARTIALLY_NORMALIZED if partial else ProfileNormalizationStatus.NORMALIZED
        )
        profile = CanonicalStudentProfile.model_validate(canonical)
        logger.info("student profile normalized fields=%d issues=%d status=%s", len(results), len(issues), overall.value)
        return ProfileNormalizationResponse(profile=profile, normalization=results, issues=issues, status=overall)


def normalize_student_profile(raw_profile: RawStudentProfile | dict[str, Any]) -> ProfileNormalizationResponse:
    return StudentProfileNormalizationService().normalize(raw_profile)