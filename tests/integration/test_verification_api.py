from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.dependencies import get_db
from app.db.models import Scholarship
from app.main import app
from app.verification.fetcher import FetchResult
from app.verification.service import ScholarshipVerificationService


def test_verification_persists_claims_evidence_and_history() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        scholarship = Scholarship(name="Synthetic Verification Scholarship", provider="Synthetic Provider", official_source_url="https://example.com/source", status="unknown", data_quality="needs_review", fingerprint="verification-test")
        session.add(scholarship)
        session.commit()

        def fake_fetch(url: str) -> FetchResult:
            return FetchResult(url=url, success=True, status_code=200, content="Synthetic Verification Scholarship Synthetic Provider", content_hash="hash")

        service = ScholarshipVerificationService(session)
        record = service.verify(scholarship, fetcher=fake_fetch)
        assert record.verification_status == "PARTIALLY_VERIFIED"
        assert len(service.history(scholarship.id)) == 1

        def override_db():
            yield session

        app.dependency_overrides[get_db] = override_db
        try:
            with TestClient(app) as client:
                detail = client.get(f"/api/v1/scholarships/{scholarship.id}/verification")
                history = client.get(f"/api/v1/scholarships/{scholarship.id}/verification/history")
                queue = client.get("/api/v1/scholarships/verification/queue?limit=1")
        finally:
            app.dependency_overrides.clear()

    assert detail.status_code == 200
    assert detail.json()["claims"]
    assert detail.json()["evidence"][0]["content_hash"] == "hash"
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert queue.status_code == 200
    assert len(queue.json()) == 1


def test_source_unavailable_is_not_promoted() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        scholarship = Scholarship(name="Unavailable Scholarship", provider="Provider", official_source_url="https://example.com/unavailable", status="unknown", data_quality="needs_review", fingerprint="unavailable-test")
        session.add(scholarship)
        session.commit()
        result = ScholarshipVerificationService(session).verify(
            scholarship, fetcher=lambda url: FetchResult(url=url, success=False, error="timeout")
        )
    assert result.verification_status == "SOURCE_UNAVAILABLE"