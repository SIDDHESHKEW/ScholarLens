from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import Scholarship
from app.intelligence.taxonomy import AcademicRelevanceTier, FieldClassification, classify_scholarship_field
from app.recommendations.quality import RecommendationQualityGate
from app.recommendations.service import RecommendationService


def make_session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return Session(engine)


def add_scholarship(
    session: Session,
    scholarship_id: int,
    name: str = "Test Scholarship",
    requirements=None,
    metadata=None,
    description: str = "Description",
) -> Scholarship:
    scholarship = Scholarship(
        id=scholarship_id,
        name=name,
        provider="Test Provider",
        description=description,
        requirements=requirements or [],
        legacy_metadata=metadata or {},
        data_quality="needs_review",
        fingerprint=f"test-quality-{scholarship_id}",
    )
    session.add(scholarship)
    session.commit()
    return scholarship


def test_classify_scholarship_field_identifies_broad_specific_unknown() -> None:
    assert classify_scholarship_field("Unrestricted") == FieldClassification.BROAD
    assert classify_scholarship_field("all") == FieldClassification.BROAD
    assert classify_scholarship_field("All disciplines") == FieldClassification.BROAD
    assert classify_scholarship_field("any field") == FieldClassification.BROAD
    assert classify_scholarship_field("All (Science, Commerce, Humanities...)") == FieldClassification.BROAD

    assert classify_scholarship_field("Computer Science") == FieldClassification.SPECIFIC
    assert classify_scholarship_field("Mechanical Engineering") == FieldClassification.SPECIFIC
    assert classify_scholarship_field("Finance and Economics") == FieldClassification.SPECIFIC
    assert classify_scholarship_field("Critical Languages") == FieldClassification.SPECIFIC

    assert classify_scholarship_field(None) == FieldClassification.UNKNOWN
    assert classify_scholarship_field("") == FieldClassification.UNKNOWN
    assert classify_scholarship_field("not specified") == FieldClassification.UNKNOWN


def test_specific_field_mismatch_blocks_recommendation() -> None:
    session = make_session()
    # Scholarship 1: Specific field mismatch (Finance and Economics)
    add_scholarship(session, 1, name="Finance Prize", metadata={"field_of_study": "Finance and Economics"})
    # Scholarship 2: Relevant discipline (Computer Science)
    add_scholarship(session, 2, name="CS Award", metadata={"field_of_study": "computer_science"})

    response = RecommendationService(session).generate(
        {"education_level": "undergraduate", "field_of_study": "computer_science"},
        limit=10,
    )
    recommended_ids = [r.scholarship_id for r in response.recommendations]
    assert 2 in recommended_ids
    assert 1 not in recommended_ids
    assert 1 in response.excluded.quality_blocked_ids
    assert response.excluded.quality_blocked_count == 1


def test_broad_unrestricted_field_is_not_blocked() -> None:
    session = make_session()
    # Scholarship 1: Unrestricted
    add_scholarship(session, 1, name="Global Scholars", metadata={"field_of_study": "Unrestricted"})
    # Scholarship 2: Specific field match (computer_science)
    add_scholarship(session, 2, name="CS Excellence", metadata={"field_of_study": "computer_science"})

    response = RecommendationService(session).generate(
        {"education_level": "undergraduate", "field_of_study": "computer_science"},
        limit=10,
    )
    recommended_ids = [r.scholarship_id for r in response.recommendations]
    assert 1 in recommended_ids
    assert 2 in recommended_ids
    assert response.excluded.quality_blocked_count == 0


def test_mba_scholarship_blocked_for_undergraduate_as_contradiction() -> None:
    session = make_session()
    add_scholarship(
        session,
        1,
        name="Global MBA Scholarship Program",
        description="Our new MBA scholarship for outstanding future business leaders.",
        metadata={"field_of_study": "Unrestricted"},
    )
    # Undergraduate profile
    response_ug = RecommendationService(session).generate(
        {"education_level": "undergraduate", "field_of_study": "computer_science"},
        limit=10,
    )
    assert 1 not in [r.scholarship_id for r in response_ug.recommendations]
    assert 1 in response_ug.excluded.not_eligible_ids

    # Postgraduate profile
    response_pg = RecommendationService(session).generate(
        {"education_level": "postgraduate", "field_of_study": "business"},
        limit=10,
    )
    assert 1 in [r.scholarship_id for r in response_pg.recommendations]


def test_minimal_profile_unspecified_field_remains_unknown_and_unblocked() -> None:
    session = make_session()
    add_scholarship(session, 1, name="Law Fellowship", metadata={"field_of_study": "Law & Legal Studies"})
    add_scholarship(session, 2, name="General Grant", metadata={"field_of_study": "Unrestricted"})

    # Student has no field_of_study specified
    response = RecommendationService(session).generate(
        {"age": 20, "education_level": "undergraduate"},
        limit=10,
    )
    recommended_ids = [r.scholarship_id for r in response.recommendations]
    assert 1 in recommended_ids
    assert 2 in recommended_ids
    assert response.excluded.quality_blocked_count == 0


def test_academic_relevance_tier_ordering_strong_over_broad_over_unknown() -> None:
    session = make_session()
    # Id 1: Broad/unrestricted
    add_scholarship(session, 1, name="Broad Award", metadata={"field_of_study": "Unrestricted"})
    # Id 2: Strong match
    add_scholarship(session, 2, name="Direct CS Award", metadata={"field_of_study": "computer_science"})
    # Id 3: Partial match (Engineering)
    add_scholarship(session, 3, name="Engineering Award", metadata={"field_of_study": "engineering"})
    # Id 4: Unknown field
    add_scholarship(session, 4, name="Unstated Award", metadata={})

    response = RecommendationService(session).generate(
        {"education_level": "undergraduate", "field_of_study": "computer_science"},
        limit=10,
    )
    ordered_ids = [r.scholarship_id for r in response.recommendations]
    # Strong (2) should precede Partial (3), Partial (3) should precede Broad (1), Broad (1) should precede Unknown (4)
    assert ordered_ids.index(2) < ordered_ids.index(3)
    assert ordered_ids.index(3) < ordered_ids.index(1)
    assert ordered_ids.index(1) < ordered_ids.index(4)
