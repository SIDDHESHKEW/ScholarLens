from typing import Any

from .base import aliased_result, clean_text, missing_result, unresolved_result

ALIASES = {
    "primary": "primary", "secondary": "secondary", "higher secondary": "higher_secondary",
    "higher_secondary": "higher_secondary", "diploma": "diploma", "undergraduate": "undergraduate",
    "b.tech": "bachelor", "b.e.": "bachelor", "bachelor of technology": "bachelor",
    "bachelor's": "bachelor", "bachelor": "bachelor", "postgraduate": "postgraduate",
    "master": "master", "master's": "master", "m.tech": "master", "phd": "doctoral",
    "doctoral": "doctoral", "postdoctoral": "postdoctoral", "vocational": "vocational",
    "certificate": "certificate", "school": "school", "other": "other",
}


def normalize_education(field: str, value: Any):
    cleaned = clean_text(value)
    if cleaned is None:
        return missing_result(field, value)
    normalized = ALIASES.get(cleaned.casefold())
    if normalized is None:
        return unresolved_result(field, value, cleaned, "Education level has no exact canonical alias.")
    return aliased_result(field, value, cleaned, normalized, "alias_exact")