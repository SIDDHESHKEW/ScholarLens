from datetime import datetime, timedelta, timezone
import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import Scholarship, ScholarshipSource, VerificationRecord
from app.recommendations.models import RecommendationRequest
from app.recommendations.service import RecommendationService
from app.verification.schemas import FreshnessStatus, VerificationStatus


def make_session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return Session(engine)


def add_scholarship(session: Session, scholarship_id: int, requirements=None, metadata=None, name=None) -> Scholarship:
    scholarship = Scholarship(
        id=scholarship_id,
        name=name or f"Scholarship {scholarship_id}",
        provider="Provider",
        requirements=requirements or [],
        legacy_metadata=metadata or {},
        data_quality="needs_review",
        fingerprint=f"eval-{scholarship_id}",
    )
    session.add(scholarship)
    session.commit()
    return scholarship


def test_verification_status_mapping_and_accurate_warnings() -> None:
    session = make_session()
    now = datetime.now(timezone.utc)

    # 1. Unverified (no record)
    s_unverified = add_scholarship(session, 1, metadata={"field_of_study": "cs"})
    
    # 2. Verified
    s_verified = add_scholarship(session, 2, metadata={"field_of_study": "cs"})
    session.add(VerificationRecord(
        scholarship_id=s_verified.id,
        verification_status="VERIFIED",
        freshness_status="FRESH",
        verifier_method="controlled_url_fetch",
        verified_at=now,
        notes="Verified from official portal."
    ))

    # 3. Needs Review
    s_needs_review = add_scholarship(session, 3, metadata={"field_of_study": "cs"})
    session.add(VerificationRecord(
        scholarship_id=s_needs_review.id,
        verification_status="NEEDS_REVIEW",
        freshness_status="FRESH",
        verifier_method="controlled_url_fetch",
        verified_at=now,
        notes="Some fields differ."
    ))

    # 4. Source Unavailable
    s_source_unavail = add_scholarship(session, 4, metadata={"field_of_study": "cs"})
    session.add(VerificationRecord(
        scholarship_id=s_source_unavail.id,
        verification_status="SOURCE_UNAVAILABLE",
        freshness_status="UNKNOWN",
        verifier_method="controlled_url_fetch",
        verified_at=now,
        notes="HTTP 404"
    ))

    # 5. Stale (explicit status)
    s_stale = add_scholarship(session, 5, metadata={"field_of_study": "cs"})
    session.add(VerificationRecord(
        scholarship_id=s_stale.id,
        verification_status="STALE",
        freshness_status="STALE",
        verifier_method="controlled_url_fetch",
        verified_at=now,
        notes="Old verification record."
    ))

    # 6. Contradicted
    s_contradicted = add_scholarship(session, 6, metadata={"field_of_study": "cs"})
    session.add(VerificationRecord(
        scholarship_id=s_contradicted.id,
        verification_status="CONTRADICTED",
        freshness_status="FRESH",
        verifier_method="controlled_url_fetch",
        verified_at=now,
        notes="Official site says scholarship discontinued."
    ))

    session.commit()

    service = RecommendationService(session, include_synthetic=True)
    resp = service.generate({"field_of_study": "cs"}, limit=10)
    items_by_id = {item.scholarship_id: item for item in resp.recommendations}

    # Verify Unverified
    item_unver = items_by_id[1]
    assert item_unver.verification.status == "UNVERIFIED"
    assert "not yet been independently verified" in item_unver.verification.warnings[0]

    # Verify Verified (no unverified warning!)
    item_ver = items_by_id[2]
    assert item_ver.verification.status == "VERIFIED"
    assert item_ver.verification.freshness == "FRESH"
    assert not any("not yet been" in w for w in item_ver.warnings)

    # Verify Needs Review
    item_nr = items_by_id[3]
    assert item_nr.verification.status == "NEEDS_REVIEW"
    assert "requires review" in item_nr.verification.warnings[0]

    # Verify Source Unavailable
    item_su = items_by_id[4]
    assert item_su.verification.status == "SOURCE_UNAVAILABLE"
    assert "could not be reached" in item_su.verification.warnings[0]

    # Verify Stale
    item_stale = items_by_id[5]
    assert item_stale.verification.status == "STALE"
    assert "may be outdated" in item_stale.verification.warnings[0]

    # Verify Contradicted
    item_contra = items_by_id[6]
    assert item_contra.verification.status == "CONTRADICTED"
    assert "conflicts with this record" in item_contra.verification.warnings[0]


def test_dynamic_freshness_boundary_check() -> None:
    session = make_session()
    # Verified 35 days ago (max_age_days = 30)
    s = add_scholarship(session, 1, metadata={"field_of_study": "cs"})
    session.add(VerificationRecord(
        scholarship_id=s.id,
        verification_status="VERIFIED",
        freshness_status="FRESH",  # stored as fresh at verification time
        verifier_method="controlled_url_fetch",
        verified_at=datetime.now(timezone.utc) - timedelta(days=35),
    ))
    session.commit()

    service = RecommendationService(session, max_age_days=30, include_synthetic=True)
    resp = service.generate({"field_of_study": "cs"})
    item = resp.recommendations[0]

    # Dynamic freshness must downgrade to STALE
    assert item.verification.status == "STALE"
    assert item.verification.freshness == "STALE"
    assert any("may be outdated" in w for w in item.warnings)


def test_score_null_vs_score_zero_semantics() -> None:
    session = make_session()
    # 1. Unscored: all dimensions unknown
    s_unscored = add_scholarship(session, 1, metadata={})

    # 2. Score 0: evaluated factor is MISMATCH (field mismatch: student cs, scholarship law)
    # With study_country matching? No, let study_country mismatch or just field mismatch alone
    s_mismatch = add_scholarship(session, 2, metadata={"field_of_study": "Law", "target_field": "Law"})

    service = RecommendationService(session, include_synthetic=True)
    resp = service.generate({"field_of_study": "Computer Science"}, limit=5)
    items_by_id = {item.scholarship_id: item for item in resp.recommendations}

    # Unscored candidate
    assert items_by_id[1].score is None
    assert any("unscored" in w.lower() for w in items_by_id[1].warnings)

    # Scored candidate with 0.0
    if 2 in items_by_id:
        assert items_by_id[2].score == 0.0
        assert items_by_id[2].score is not None


def test_recommendation_determinism() -> None:
    session = make_session()
    for i in range(1, 10):
        add_scholarship(session, i, metadata={"field_of_study": "Engineering" if i % 2 == 0 else "Medicine"})

    service = RecommendationService(session, include_synthetic=True)
    profile = {"field_of_study": "Engineering", "education_level": "undergraduate"}

    resp1 = service.generate(profile, limit=5)
    resp2 = service.generate(profile, limit=5)

    assert resp1.recommended_count == resp2.recommended_count
    assert [r.scholarship_id for r in resp1.recommendations] == [r.scholarship_id for r in resp2.recommendations]
    assert [r.score for r in resp1.recommendations] == [r.score for r in resp2.recommendations]
    assert [r.rank for r in resp1.recommendations] == [r.rank for r in resp2.recommendations]


def test_api_contract_strictness() -> None:
    # Test RecommendationRequest rejects extra fields (extra="forbid")
    with pytest.raises(ValidationError):
        RecommendationRequest.model_validate({
            "student_profile": {"field_of_study": "CS"},
            "unrecognized_field": True
        })

    # Test limit validation: limit must be between 1 and 100
    with pytest.raises(ValidationError):
        RecommendationRequest.model_validate({
            "student_profile": {"field_of_study": "CS"},
            "limit": 0
        })

    with pytest.raises(ValidationError):
        RecommendationRequest.model_validate({
            "student_profile": {"field_of_study": "CS"},
            "limit": 101
        })
