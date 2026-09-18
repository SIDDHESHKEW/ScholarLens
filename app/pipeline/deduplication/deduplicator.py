import hashlib
import re
from typing import Any


def comparable_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value or "").casefold())


def fingerprint(record: dict[str, Any]) -> str:
    parts = (
        comparable_text(record.get("name")),
        comparable_text(record.get("provider")),
        comparable_text(record.get("official_source_url")),
        comparable_text(record.get("application_url")),
    )
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def is_duplicate(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if fingerprint(left) == fingerprint(right):
        return True
    left_name = comparable_text(left.get("name"))
    right_name = comparable_text(right.get("name"))
    left_provider = comparable_text(left.get("provider"))
    right_provider = comparable_text(right.get("provider"))
    return bool(left_name and left_name == right_name and left_provider and left_provider == right_provider)