import re
from html import unescape
from typing import Any


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = unescape(re.sub(r"<[^>]+>", " ", str(value)))
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def clean_record(record: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in record.items():
        if isinstance(value, str):
            cleaned[key] = clean_text(value)
        elif isinstance(value, dict):
            cleaned[key] = {
                nested_key: clean_text(nested_value)
                if isinstance(nested_value, str)
                else nested_value
                for nested_key, nested_value in value.items()
            }
        else:
            cleaned[key] = value
    return {key: value for key, value in cleaned.items() if value not in (None, "", [])}