from typing import Any

from .base import aliased_result, clean_text, missing_result, unresolved_result

ALIASES = {
    "general": "general", "reserved": "reserved", "minority": "minority",
    "economically disadvantaged": "economically_disadvantaged",
    "economically_disadvantaged": "economically_disadvantaged", "first generation": "first_generation",
    "first_generation": "first_generation", "international student": "international_student",
    "international_student": "international_student", "domestic student": "domestic_student",
    "domestic_student": "domestic_student",
}


def normalize_category(field: str, value: Any):
    cleaned = clean_text(value)
    if cleaned is None:
        return missing_result(field, value)
    normalized = ALIASES.get(cleaned.casefold())
    if normalized is None:
        return unresolved_result(field, value, cleaned, "Student category has no exact canonical alias.")
    return aliased_result(field, value, cleaned, normalized, "alias_exact")