import re
from decimal import Decimal, InvalidOperation
from typing import Any

from .base import aliased_result, clean_text, invalid_result, missing_result, unresolved_result

CURRENCY_ALIASES = {"inr": "INR", "rs": "INR", "rs.": "INR", "₹": "INR", "usd": "USD", "$": "USD", "gbp": "GBP", "£": "GBP"}


def normalize_income(field: str, value: Any):
    if value is None:
        return missing_result(field, value)
    if isinstance(value, bool):
        return invalid_result(field, value, None, "Income must be numeric.")
    raw = str(value).strip()
    cleaned = raw.replace("₹", "").replace("$", "").replace("£", "").strip()
    if re.fullmatch(r"[0-9]+(?:,[0-9]{2,3})+", cleaned):
        cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        return unresolved_result(field, value, cleaned, "Income format is invalid or ambiguous.")
    try:
        amount = Decimal(cleaned)
    except InvalidOperation:
        return invalid_result(field, value, cleaned, "Income must be numeric.")
    if amount < 0:
        return invalid_result(field, value, cleaned, "Income cannot be negative.")
    if amount != amount.to_integral_value():
        return aliased_result(field, value, cleaned, float(amount), "numeric_parse")
    return aliased_result(field, value, cleaned, int(amount), "numeric_parse")


def normalize_currency(field: str, value: Any):
    cleaned = clean_text(value)
    if cleaned is None:
        return missing_result(field, value)
    normalized = CURRENCY_ALIASES.get(cleaned.casefold())
    if normalized is None:
        return unresolved_result(field, value, cleaned, "Currency has no exact canonical alias.")
    return aliased_result(field, value, cleaned, normalized, "alias_exact")