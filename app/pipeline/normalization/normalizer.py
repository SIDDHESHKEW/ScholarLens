import re
from datetime import date, datetime
from typing import Any


COUNTRY_ALIASES = {"india": "India", "indian": "India", "ind": "India"}
EDUCATION_ALIASES = {
    "ug": "undergraduate",
    "under graduate": "undergraduate",
    "undergraduate": "undergraduate",
    "school": "school",
    "post graduate": "postgraduate",
    "postgraduate": "postgraduate",
    "phd": "phd",
}
CURRENCY_ALIASES = {"rs": "INR", "rs.": "INR", "inr": "INR", "₹": "INR"}
STATUS_ALIASES = {
    "open": "active",
    "active": "active",
    "closed": "closed",
    "expired": "expired",
    "upcoming": "upcoming",
    "unknown": "unknown",
}


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None


def normalize_country(value: Any) -> str | None:
    text = normalize_text(value)
    return COUNTRY_ALIASES.get(text.casefold(), text) if text else None


def normalize_education_level(value: Any) -> str | None:
    text = normalize_text(value)
    return EDUCATION_ALIASES.get(text.casefold(), "unknown") if text else None


def normalize_provider(value: Any) -> str | None:
    return normalize_text(value)


def normalize_status(value: Any) -> str:
    text = normalize_text(value)
    return STATUS_ALIASES.get(text.casefold(), "unknown") if text else "unknown"


def normalize_date(value: Any) -> tuple[date | None, str | None]:
    if value in (None, ""):
        return None, None
    if isinstance(value, datetime):
        return value.date(), None
    if isinstance(value, date):
        return value, None
    text = normalize_text(value)
    if not text:
        return None, None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date(), None
        except ValueError:
            continue
    if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", text):
        return None, "ambiguous deadline format"
    return None, "invalid deadline"


def normalize_currency(value: Any) -> str | None:
    text = normalize_text(value)
    if not text:
        return None
    return CURRENCY_ALIASES.get(text.casefold(), text.upper())


def normalize_percentage(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        numeric = float(str(value).replace("%", "").strip())
    except (TypeError, ValueError):
        return None
    return numeric if 0 <= numeric <= 100 else None


def normalize_record(record: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    normalized = dict(record)
    warnings: list[str] = []
    normalized["name"] = normalize_text(record.get("name"))
    normalized["provider"] = normalize_provider(record.get("provider"))
    normalized["description"] = normalize_text(record.get("description"))
    normalized["official_source_url"] = normalize_text(record.get("official_source_url"))
    normalized["application_url"] = normalize_text(record.get("application_url"))
    normalized["country"] = normalize_country(record.get("country"))
    normalized["education_level"] = normalize_education_level(record.get("education_level"))
    normalized["currency"] = normalize_currency(record.get("currency"))
    normalized["status"] = normalize_status(record.get("status"))
    normalized["academic_percentage"] = normalize_percentage(record.get("academic_percentage"))
    deadline, warning = normalize_date(record.get("deadline"))
    normalized["deadline"] = deadline
    if warning:
        warnings.append(warning)
    return normalized, warnings