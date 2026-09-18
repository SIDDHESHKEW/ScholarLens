from enum import Enum
from typing import Any


class FieldClassification(str, Enum):
    BROAD = "BROAD"
    SPECIFIC = "SPECIFIC"
    UNKNOWN = "UNKNOWN"


class AcademicRelevanceTier(int, Enum):
    TIER_1_STRONG = 1
    TIER_2_PARTIAL = 2
    TIER_3_BROAD = 3
    TIER_4_UNKNOWN = 4
    TIER_5_BLOCKED = 5


BROAD_FIELD_KEYWORDS = {
    "unrestricted",
    "all",
    "all disciplines",
    "all research areas",
    "all subjects",
    "any",
    "any field",
    "general",
    "open to all fields",
    "all fields",
    "other",
    "unspecified",
}


def classify_scholarship_field(field_text: Any) -> FieldClassification:
    if field_text is None:
        return FieldClassification.UNKNOWN
    cleaned = str(field_text).strip().casefold()
    if not cleaned or cleaned in {"none", "unknown", "not specified", "null"}:
        return FieldClassification.UNKNOWN
    if (
        cleaned in BROAD_FIELD_KEYWORDS
        or cleaned.startswith("all (")
        or cleaned.startswith("all:")
        or cleaned == "all disciplines"
        or "unrestricted" in cleaned
    ):
        return FieldClassification.BROAD
    return FieldClassification.SPECIFIC
