from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


@dataclass(frozen=True)
class RawRecord:
    payload: dict[str, Any]
    source_name: str
    source_type: str
    source_url: str | None
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def content_hash(self) -> str:
        content = repr(sorted(self.payload.items())).encode("utf-8")
        return sha256(content).hexdigest()


@dataclass(frozen=True)
class AcquisitionResult:
    records: list[RawRecord]
    source_name: str
    source_type: str
    source_url: str | None
    retrieved_at: datetime
    raw_content: str | None = None
    content_hash: str | None = None


class ScholarshipSourceAdapter(ABC):
    source_name: str
    source_type: str
    source_url: str | None

    @abstractmethod
    def fetch(self) -> AcquisitionResult:
        """Acquire publicly available source data without transforming it."""