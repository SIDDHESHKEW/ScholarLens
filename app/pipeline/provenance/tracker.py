from datetime import datetime, timezone
from typing import Any


def provenance_payload(
    *, source_name: str, source_type: str, source_url: str | None,
    content_hash: str | None, source_status: str | None = None,
) -> dict[str, Any]:
    return {
        "source_name": source_name,
        "source_type": source_type,
        "source_url": source_url,
        "retrieved_at": datetime.now(timezone.utc),
        "content_hash": content_hash,
        "verification_status": "unverified",
        "source_status": source_status,
    }