from datetime import datetime, timedelta, timezone

from app.verification.fetcher import validate_source_url
from app.verification.schemas import FreshnessStatus
from app.verification.service import freshness


def test_safe_url_validation_rejects_dangerous_targets() -> None:
    assert validate_source_url("file:///etc/passwd")[0] is False
    assert validate_source_url("http://localhost/private")[0] is False
    assert validate_source_url("http://127.0.0.1/private")[0] is False
    assert validate_source_url("https://example.com")[0] is True


def test_freshness_is_configurable_and_deterministic() -> None:
    recent = datetime.now(timezone.utc) - timedelta(days=2)
    old = datetime.now(timezone.utc) - timedelta(days=31)
    assert freshness(recent, max_age_days=30) == FreshnessStatus.FRESH
    assert freshness(old, max_age_days=30) == FreshnessStatus.STALE
    assert freshness(None) == FreshnessStatus.UNKNOWN