from typing import Any

from .base import aliased_result, clean_text, missing_result, unresolved_result

ALIASES = {
    "computer science": "computer_science", "computer_science": "computer_science", "computer science engineering": "computer_science",
    "computer science & engineering": "computer_science", "cse": "computer_science",
    "information technology": "information_technology", "information_technology": "information_technology", "information technology engineering": "information_technology",
    "it": "information_technology", "artificial intelligence": "artificial_intelligence", "artificial_intelligence": "artificial_intelligence",
    "ai": "artificial_intelligence", "data science": "data_science", "data_science": "data_science", "engineering": "engineering",
    "medicine": "medicine", "nursing": "nursing", "business": "business", "economics": "economics",
    "finance": "finance", "law": "law", "education": "education", "humanities": "humanities",
    "social sciences": "social_sciences", "natural sciences": "natural_sciences", "mathematics": "mathematics",
    "physics": "physics", "chemistry": "chemistry", "agriculture": "agriculture",
    "environmental science": "environmental_science", "arts": "arts", "design": "design",
    "architecture": "architecture", "other": "other",
}


def normalize_field(field: str, value: Any):
    cleaned = clean_text(value)
    if cleaned is None:
        return missing_result(field, value)
    normalized = ALIASES.get(cleaned.casefold())
    if normalized is None:
        return unresolved_result(field, value, cleaned, "Field of study has no exact canonical alias.")
    return aliased_result(field, value, cleaned, normalized, "alias_exact")