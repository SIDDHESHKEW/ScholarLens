from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import Scholarship, VerificationRecord
from app.recommendations.service import RecommendationService


def make_session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return Session(engine)


def add_scholarship(session: Session, scholarship_id: int, requirements=None, metadata=None) -> Scholarship:
    scholarship = Scholarship(
        id=scholarship_id,
        name=f"Synthetic Scholarship {scholarship_id}",
        provider="Synthetic Provider",
        requirements=requirements or [],
        legacy_metadata=metadata or {},
        data_quality="needs_review",
        fingerprint=f"recommendation-{scholarship_id}",
    )
    session.add(scholarship)
    session.commit()
    return scholarship


def test_eligible_is_recommended_with_deterministic_reasons_and_limit() -> None:
    session = make_session()
    add_scholarship(session, 1, metadata={"field_of_study": "computer_science"})
    add_scholarship(session, 2, metadata={"field_of_study": "medicine"})
    response = RecommendationService(session).generate(
        {"field_of_study": "computer_science"}, limit=1
    )
    assert response.recommended_count == 1
    assert response.recommendations[0].rank == 1
    assert response.recommendations[0].scholarship_id == 1
    assert response.recommendations[0].reasons
    assert response.recommendations[0].reasons == RecommendationService(session).generate(
        {"field_of_study": "computer_science"}, limit=1
    ).recommendations[0].reasons


def test_not_eligible_is_excluded_and_possible_can_be_disabled() -> None:
    session = make_session()
    add_scholarship(session, 1, [{"field": "age", "operator": "max", "value": 18, "requirement_type": "hard"}])
    add_scholarship(session, 2, [{"field": "academic_percentage", "operator": "min", "value": 80, "requirement_type": "hard"}])
    response = RecommendationService(session).generate(
        {"age": 20}, include_possibly_eligible=False
    )
    assert response.recommended_count == 0
    assert response.excluded.not_eligible_ids == [1]


def test_possible_eligibility_and_verification_warning_are_preserved() -> None:
    session = make_session()
    scholarship = add_scholarship(session, 1, metadata={"field_of_study": "computer_science"})
    session.add(
        VerificationRecord(
            scholarship_id=scholarship.id,
            verification_status="STALE",
            freshness_status="STALE",
            verifier_method="test",
            verified_at=datetime.now(timezone.utc),
        )
    )
    session.commit()
    response = RecommendationService(session).generate({"field_of_study": "computer_science"})
    item = response.recommendations[0]
    assert item.eligibility.outcome == "ELIGIBLE"
    assert item.verification.status == "STALE"
    assert item.verification.freshness == "STALE"
    assert item.warnings


def test_missing_optional_data_does_not_fabricate_values() -> None:
    session = make_session()
    add_scholarship(session, 1)
    response = RecommendationService(session).generate({})
    item = response.recommendations[0]
    assert item.application_url is None
    assert item.deadline is None
    assert item.verification.status == "UNVERIFIED"
    assert item.score is None


def test_scored_scholarship_ranks_above_unscored_and_preserves_null() -> None:
    session = make_session()
    # Unscored scholarship with lower ID (id=1)
    add_scholarship(session, 1, metadata={})
    # Scored scholarship with higher ID (id=2)
    add_scholarship(session, 2, metadata={"field_of_study": "computer_science"})

    response = RecommendationService(session).generate(
        {"field_of_study": "computer_science"}, limit=5
    )
    assert response.recommended_count == 2
    assert response.recommendations[0].rank == 1
    assert response.recommendations[0].scholarship_id == 2
    assert response.recommendations[0].score is not None
    assert response.recommendations[0].score > 0

    assert response.recommendations[1].rank == 2
    assert response.recommendations[1].scholarship_id == 1
    assert response.recommendations[1].score is None
    assert response.recommendations[1].score != 0
    assert any("unscored" in w.lower() for w in response.recommendations[1].warnings)


def test_unscored_does_not_outrank_possibly_eligible_scored() -> None:
    session = make_session()
    # Unscored but ELIGIBLE
    add_scholarship(session, 1, requirements=[], metadata={})
    # Scored but POSSIBLY_ELIGIBLE
    add_scholarship(
        session,
        2,
        requirements=[{"field": "academic_percentage", "operator": "min", "value": 75, "requirement_type": "hard"}],
        metadata={"field_of_study": "computer_science"},
    )
    # Student profile has field_of_study matching id 2, but missing academic_percentage (makes id 2 POSSIBLY_ELIGIBLE)
    response = RecommendationService(session).generate(
        {"field_of_study": "computer_science"}, limit=5, include_possibly_eligible=True
    )
    assert response.recommended_count == 2
    # Scored candidate must precede unscored candidate
    assert response.recommendations[0].scholarship_id == 2
    assert response.recommendations[0].score is not None
    assert response.recommendations[1].scholarship_id == 1
    assert response.recommendations[1].score is None


def test_synthetic_and_test_scholarships_excluded_from_production() -> None:
    from app.db.models import ScholarshipSource

    session = make_session()
    # Real candidate
    real = add_scholarship(session, 10, metadata={"source_dataset": "clean_scholarships.csv"})

    # Synthetic by name prefix
    syn1 = Scholarship(
        id=1,
        name="SYNTHETIC TEST DATA - Future Scholars Grant",
        provider="Example Foundation",
        requirements=[],
        legacy_metadata={},
        data_quality="needs_review",
        fingerprint="syn-1",
    )
    # Synthetic by source provenance
    syn2 = Scholarship(
        id=2,
        name="Rural STEM Award",
        provider="Example Foundation",
        requirements=[],
        legacy_metadata={},
        data_quality="needs_review",
        fingerprint="syn-2",
    )
    # Synthetic by metadata flag
    syn3 = Scholarship(
        id=3,
        name="Mock Fellowship",
        provider="Example Foundation",
        requirements=[],
        legacy_metadata={"is_synthetic": True},
        data_quality="needs_review",
        fingerprint="syn-3",
    )
    session.add_all([syn1, syn2, syn3])
    session.commit()

    session.add(
        ScholarshipSource(
            scholarship_id=syn2.id,
            source_name="Synthetic fixture",
            source_type="dataset",
            verification_status="unverified",
        )
    )
    session.commit()

    # Production recommendations exclude synthetic fixtures
    response = RecommendationService(session, include_synthetic=False).generate({})
    assert response.total_candidates == 1
    assert response.recommended_count == 1
    assert response.recommendations[0].scholarship_id == real.id

    # Test mode allows synthetic records to remain usable in tests
    response_with_synthetic = RecommendationService(session, include_synthetic=True).generate({})
    assert response_with_synthetic.total_candidates == 4