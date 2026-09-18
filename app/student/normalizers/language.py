from typing import Any

from .base import aliased_result, clean_text, missing_result, unresolved_result

ALIASES = {"english": "English", "en": "English", "hindi": "Hindi", "हिंदी": "Hindi", "french": "French", "fr": "French", "spanish": "Spanish", "es": "Spanish"}


def normalize_language(field: str, value: Any):
    cleaned = clean_text(value)
    if cleaned is None:
        return missing_result(field, value)
    normalized = ALIASES.get(cleaned.casefold())
    if normalized is None:
        return unresolved_result(field, value, cleaned, "Language has no exact canonical alias.")
    return aliased_result(field, value, cleaned, normalized, "alias_exact")