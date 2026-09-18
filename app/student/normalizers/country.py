from typing import Any

from .base import aliased_result, ambiguous_result, clean_text, missing_result, unresolved_result

ALIASES = {
    "india": "India", "republic of india": "India", "ind": "India",
    "usa": "United States", "u.s.a.": "United States", "united states": "United States",
    "united states of america": "United States", "uk": "United Kingdom",
    "u.k.": "United Kingdom", "united kingdom": "United Kingdom",
    "nepal": "Nepal", "bhutan": "Bhutan",
}


def normalize_country(field: str, value: Any):
    cleaned = clean_text(value)
    if cleaned is None:
        return missing_result(field, value)
    if cleaned.casefold() in {"mp", "ga"}:
        return ambiguous_result(field, value, cleaned, "Location code has multiple possible interpretations.")
    normalized = ALIASES.get(cleaned.casefold())
    if normalized is None:
        return unresolved_result(field, value, cleaned, "Country is not in the explicit canonical alias set.")
    return aliased_result(field, value, cleaned, normalized, "alias_exact")