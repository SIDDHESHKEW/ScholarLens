from collections.abc import Iterable
from datetime import date, datetime
from typing import Any


def _same_value(actual: Any, required: Any) -> bool | None:
    if actual is None or required is None:
        return None
    if isinstance(actual, str) and isinstance(required, str):
        return actual.casefold() == required.casefold()
    if type(actual) is not type(required) and not (
        isinstance(actual, (int, float)) and not isinstance(actual, bool)
        and isinstance(required, (int, float)) and not isinstance(required, bool)
    ):
        return None
    return actual == required


def equals(actual: Any, required: Any) -> bool | None:
    return _same_value(actual, required)


def not_equals(actual: Any, required: Any) -> bool | None:
    comparison = _same_value(actual, required)
    return None if comparison is None else not comparison


def membership(actual: Any, required: Any, *, invert: bool = False) -> bool | None:
    if actual is None or not isinstance(required, (list, tuple, set, frozenset)):
        return None
    comparisons = [_same_value(actual, candidate) for candidate in required]
    if any(comparison is None for comparison in comparisons):
        return None
    result = any(comparisons)
    return not result if invert else result


def minimum(actual: Any, required: Any) -> bool | None:
    return _ordered_compare(actual, required, lambda left, right: left >= right)


def maximum(actual: Any, required: Any) -> bool | None:
    return _ordered_compare(actual, required, lambda left, right: left <= right)


def _ordered_compare(actual: Any, required: Any, comparator: Any) -> bool | None:
    if actual is None or required is None:
        return None
    numeric_types = (int, float)
    both_numeric = (
        isinstance(actual, numeric_types)
        and not isinstance(actual, bool)
        and isinstance(required, numeric_types)
        and not isinstance(required, bool)
    )
    same_temporal = isinstance(actual, (date, datetime)) and isinstance(
        required, (date, datetime)
    )
    if not both_numeric and not same_temporal:
        return None
    try:
        return comparator(actual, required)
    except TypeError:
        return None


def contains(actual: Any, required: Any) -> bool | None:
    if not isinstance(actual, str) or not isinstance(required, str) or not required.strip():
        return None
    return required.casefold() in actual.casefold()