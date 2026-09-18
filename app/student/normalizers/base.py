import re
from typing import Any

from app.student.result import NormalizationResult, NormalizationStatus, ValueState


UNKNOWN_VALUES = {"unknown", "not known", "i don't know", "dont know", "n/a", "na"}


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned or None


def value_state(value: Any) -> ValueState:
    if value is None:
        return ValueState.MISSING
    if isinstance(value, bool):
        return ValueState.EXPLICIT_NEGATIVE if not value else ValueState.PRESENT
    cleaned = clean_text(value)
    if cleaned and cleaned.casefold() in UNKNOWN_VALUES:
        return ValueState.UNKNOWN
    return ValueState.PRESENT


def missing_result(field: str, original: Any = None) -> NormalizationResult:
    return NormalizationResult(
        field=field,
        original=original,
        status=NormalizationStatus.MISSING,
        method=None,
        value_state=ValueState.MISSING,
    )


def unresolved_result(field: str, original: Any, cleaned: Any, issue: str) -> NormalizationResult:
    return NormalizationResult(
        field=field,
        original=original,
        cleaned=cleaned,
        normalized=None,
        status=NormalizationStatus.UNRESOLVED,
        method="no_exact_alias",
        value_state=value_state(original),
        issue=issue,
    )


def aliased_result(field: str, original: Any, cleaned: str, normalized: str, method: str) -> NormalizationResult:
    return NormalizationResult(
        field=field,
        original=original,
        cleaned=cleaned,
        normalized=normalized,
        status=(NormalizationStatus.UNCHANGED if cleaned == normalized else NormalizationStatus.NORMALIZED),
        method=method,
        value_state=value_state(original),
    )


def invalid_result(field: str, original: Any, cleaned: Any, issue: str) -> NormalizationResult:
    return NormalizationResult(
        field=field,
        original=original,
        cleaned=cleaned,
        normalized=None,
        status=NormalizationStatus.INVALID,
        method="validation",
        value_state=value_state(original),
        issue=issue,
    )


def ambiguous_result(field: str, original: Any, cleaned: Any, issue: str) -> NormalizationResult:
    return NormalizationResult(
        field=field,
        original=original,
        cleaned=cleaned,
        normalized=None,
        status=NormalizationStatus.AMBIGUOUS,
        method="ambiguous_alias",
        value_state=value_state(original),
        issue=issue,
    )