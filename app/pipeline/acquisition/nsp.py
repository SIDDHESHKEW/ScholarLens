from datetime import datetime, timezone
from hashlib import sha256
import logging

import httpx

from app.pipeline.acquisition.base import AcquisitionResult, ScholarshipSourceAdapter

logger = logging.getLogger(__name__)


class NSPAdapter(ScholarshipSourceAdapter):
    source_name = "National Scholarship Portal"
    source_type = "government"
    source_url = "https://scholarships.gov.in/"

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    def fetch(self) -> AcquisitionResult:
        logger.info("source=%s retrieval_start", self.source_name)
        retrieved_at = datetime.now(timezone.utc)
        response = httpx.get(self.source_url, timeout=self.timeout, follow_redirects=True)
        response.raise_for_status()
        content = response.text
        content_hash = sha256(content.encode("utf-8")).hexdigest()
        logger.info("source=%s retrieval_complete bytes=%d records=0", self.source_name, len(content))

        # The public landing page is retained for audit. No scholarship record is
        # inferred from HTML because NSP does not expose a stable public listing here.
        return AcquisitionResult(
            records=[],
            source_name=self.source_name,
            source_type=self.source_type,
            source_url=str(response.url),
            retrieved_at=retrieved_at,
            raw_content=content,
            content_hash=content_hash,
        )