from typing import Any

from .base import aliased_result, clean_text, missing_result, unresolved_result

ALIASES = {
    "b.tech": "B.Tech", "btech": "B.Tech", "b.e.": "B.E.", "be": "B.E.",
    "bachelor of technology": "B.Tech", "m.tech": "M.Tech", "mtech": "M.Tech",
    "bachelor of arts": "B.A.", "bachelor of science": "B.Sc.", "master of arts": "M.A.",
    "master of science": "M.Sc.", "ph.d.": "Ph.D.", "phd": "Ph.D.",
}


def normalize_degree(field: str, value: Any):
    cleaned = clean_text(value)
    if cleaned is None:
        return missing_result(field, value)
    normalized = ALIASES.get(cleaned.casefold())
    if normalized is None:
        return unresolved_result(field, value, cleaned, "Degree has no exact canonical alias.")
    return aliased_result(field, value, cleaned, normalized, "alias_exact")