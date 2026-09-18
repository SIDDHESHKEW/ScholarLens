from typing import Any

from .base import aliased_result, clean_text, missing_result

ALIASES = {"university": "university", "college": "college", "school": "school", "institute": "institute", "research institute": "research_institute", "vocational institute": "vocational_institute", "other": "other"}


def normalize_institution(field: str, value: Any):
    cleaned = clean_text(value)
    if cleaned is None:
        return missing_result(field, value)
    return aliased_result(field, value, cleaned, cleaned, "safe_cleanup")


def normalize_institution_type(field: str, value: Any):
    cleaned = clean_text(value)
    if cleaned is None:
        return missing_result(field, value)
    normalized = ALIASES.get(cleaned.casefold())
    if normalized is None:
        from .base import unresolved_result
        return unresolved_result(field, value, cleaned, "Institution type has no exact canonical alias.")
    return aliased_result(field, value, cleaned, normalized, "alias_exact")