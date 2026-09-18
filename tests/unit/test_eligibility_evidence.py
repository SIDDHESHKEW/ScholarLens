from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import Scholarship, ScholarshipSource
from app.intelligence.eligibility.engine import evaluate_eligibility
from app.intelligence.eligibility.evidence.detector import EvidenceDetector
from app.intelligence.eligibility.evidence.models import (
    DataQualityStatus,
    EvidenceConfidence,
    EvidenceType,
)
from app.intelligence.eligibility.evidence.service import EligibilityEvidenceService
from app.intelligence.eligibility.result import EligibilityStatus
from app.matching.service import SoftMatchingService
from app.recommendations.service import RecommendationService


def make_session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return Session(engine)


def test_1_undergraduate_phd_positions_not_eligible() -> None:
    detector = EvidenceDetector()
    service = EligibilityEvidenceService(detector)

    scholarship = {
        "id": 101,
        "name": "PhD Positions in Computer Science",
        "description": "Positions for doctoral candidates in CS.",
        "requirements": [],
    }
    student = {"education_level": "undergraduate"}
    structured = evaluate_eligibility(student, scholarship["requirements"])
    assert structured.status == EligibilityStatus.ELIGIBLE

    hardened = service.harden_eligibility(structured, student, scholarship)
    assert hardened.status == EligibilityStatus.NOT_ELIGIBLE
    assert "doctoral" in hardened.explanation.lower()
    assert hardened.evidence_evaluation.has_contradiction is True
    assert hardened.evidence_evaluation.data_quality_status == DataQualityStatus.CONTRADICTORY


def test_2_undergraduate_postdoc_opportunity_not_eligible() -> None:
    detector = EvidenceDetector()
    service = EligibilityEvidenceService(detector)

    scholarship = {
        "id": 102,
        "name": "Postdoctoral Research Opportunity",
        "description": "Postdoc fellowship in robotics.",
        "requirements": [],
    }
    student = {"education_level": "undergraduate"}
    structured = evaluate_eligibility(student, scholarship["requirements"])
    hardened = service.harden_eligibility(structured, student, scholarship)
    assert hardened.status == EligibilityStatus.NOT_ELIGIBLE
    assert "postdoctoral" in hardened.explanation.lower()
    assert hardened.evidence_evaluation.has_contradiction is True


def test_3_postgraduate_undergraduate_scholarship_not_eligible() -> None:
    detector = EvidenceDetector()
    service = EligibilityEvidenceService(detector)

    scholarship = {
        "id": 103,
        "name": "Undergraduate Scholarship for Excellence",
        "description": "Open exclusively to undergraduate students in science.",
        "requirements": [],
    }
    student = {"education_level": "postgraduate"}
    structured = evaluate_eligibility(student, scholarship["requirements"])
    hardened = service.harden_eligibility(structured, student, scholarship)
    assert hardened.status == EligibilityStatus.NOT_ELIGIBLE
    assert "undergraduate" in hardened.explanation.lower()
    assert hardened.evidence_evaluation.has_contradiction is True


def test_4_undergraduate_engineering_scholarship_no_false_contradiction() -> None:
    detector = EvidenceDetector()
    service = EligibilityEvidenceService(detector)

    scholarship = {
        "id": 104,
        "name": "Engineering Scholarship",
        "description": "General funding for engineering studies.",
        "requirements": [],
    }
    student = {"education_level": "undergraduate"}
    structured = evaluate_eligibility(student, scholarship["requirements"])
    hardened = service.harden_eligibility(structured, student, scholarship)
    # Generic "Engineering Scholarship" must NOT be inferred as postgraduate/doctoral
    assert hardened.status == EligibilityStatus.ELIGIBLE
    assert hardened.evidence_evaluation.has_contradiction is False


def test_5_undergraduate_no_education_info_no_invented_failure() -> None:
    detector = EvidenceDetector()
    service = EligibilityEvidenceService(detector)

    scholarship = {
        "id": 105,
        "name": "Community Leadership Award",
        "description": "Award for community service.",
        "requirements": [],
    }
    student = {"education_level": "undergraduate"}
    structured = evaluate_eligibility(student, scholarship["requirements"])
    hardened = service.harden_eligibility(structured, student, scholarship)
    assert hardened.status == EligibilityStatus.ELIGIBLE
    assert hardened.evidence_evaluation.has_contradiction is False
    assert hardened.evidence_evaluation.data_quality_status == DataQualityStatus.INSUFFICIENT


def test_6_undergraduate_multi_level_open_to_undergraduate_and_postgraduate() -> None:
    detector = EvidenceDetector()
    service = EligibilityEvidenceService(detector)

    scholarship = {
        "id": 106,
        "name": "Global Excellence Award",
        "description": "Scholarship open to undergraduate and postgraduate students in all fields.",
        "requirements": [],
    }
    student = {"education_level": "undergraduate"}
    structured = evaluate_eligibility(student, scholarship["requirements"])
    hardened = service.harden_eligibility(structured, student, scholarship)
    # Student is undergraduate, which is one of the allowed levels
    assert hardened.status == EligibilityStatus.ELIGIBLE
    assert hardened.evidence_evaluation.has_contradiction is False
    assert hardened.evidence_evaluation.data_quality_status == DataQualityStatus.SUFFICIENT


def test_7_postgraduate_multi_level_masters_and_phd() -> None:
    detector = EvidenceDetector()
    service = EligibilityEvidenceService(detector)

    scholarship = {
        "id": 107,
        "name": "Advanced Research Fellowship",
        "description": "Targeted at Master's and PhD students conducting scientific research.",
        "requirements": [],
    }
    student = {"education_level": "postgraduate"}
    structured = evaluate_eligibility(student, scholarship["requirements"])
    hardened = service.harden_eligibility(structured, student, scholarship)
    # Student is postgraduate (master's), which matches
    assert hardened.status == EligibilityStatus.ELIGIBLE
    assert hardened.evidence_evaluation.has_contradiction is False
    assert hardened.evidence_evaluation.data_quality_status == DataQualityStatus.SUFFICIENT


def test_8_incidental_mention_faculty_phd_not_classified_as_phd_only() -> None:
    detector = EvidenceDetector()
    service = EligibilityEvidenceService(detector)

    scholarship = {
        "id": 108,
        "name": "Undergraduate Summer Research Program",
        "description": "Applicants may work with faculty members who hold PhDs on exciting laboratory projects.",
        "requirements": [],
    }
    student = {"education_level": "undergraduate"}
    signals = detector.detect_evidence(scholarship)
    # The mention of "faculty members who hold PhDs" must not be extracted as a doctoral program signal
    doctoral_signals = [s for s in signals if s.detected_value == "doctoral"]
    assert len(doctoral_signals) == 0

    structured = evaluate_eligibility(student, scholarship["requirements"])
    hardened = service.harden_eligibility(structured, student, scholarship)
    assert hardened.status == EligibilityStatus.ELIGIBLE
    assert hardened.evidence_evaluation.has_contradiction is False


def test_9_recommendation_integration_excludes_postdoc_and_phd_for_undergraduate() -> None:
    session = make_session()
    # Postdoc scholarship (structured requirements empty)
    s1 = Scholarship(
        id=1,
        name="Mechatronics Engineering in Korea Postdoc Opportunity",
        provider="Koreatech",
        requirements=[],
        legacy_metadata={"field_of_study": "engineering"},
        data_quality="complete",
        fingerprint="postdoc-rec-1",
    )
    # PhD scholarship (structured requirements empty)
    s2 = Scholarship(
        id=2,
        name="PhD Positions in Analog/RF/Microwave/Mixed-Signal IC Design",
        provider="University Lab",
        requirements=[],
        legacy_metadata={"field_of_study": "engineering"},
        data_quality="complete",
        fingerprint="phd-rec-2",
    )
    # Undergraduate engineering scholarship
    s3 = Scholarship(
        id=3,
        name="GyanDhan Engineering Scholarship",
        provider="GyanDhan",
        requirements=[],
        legacy_metadata={"field_of_study": "engineering"},
        data_quality="complete",
        fingerprint="ug-rec-3",
    )
    session.add_all([s1, s2, s3])
    session.commit()

    service = RecommendationService(session)
    response = service.generate(
        {"education_level": "undergraduate", "field_of_study": "computer_science"},
        limit=5,
        include_possibly_eligible=True,
    )

    # IDs 1 and 2 must be excluded as NOT_ELIGIBLE, and only ID 3 should be recommended
    recommended_ids = [r.scholarship_id for r in response.recommendations]
    assert 1 not in recommended_ids
    assert 2 not in recommended_ids
    assert 3 in recommended_ids
    assert response.excluded.not_eligible_count == 2
    assert set(response.excluded.not_eligible_ids) == {1, 2}


def test_10_provenance_preserves_source_field_and_excerpt() -> None:
    detector = EvidenceDetector()
    scholarship = {
        "id": 110,
        "name": "Quantum Materials Postdoc Fellowship",
        "description": "Fellowship for postdoctoral researchers in quantum physics.",
        "requirements": [],
    }
    signals = detector.detect_evidence(scholarship)
    assert len(signals) >= 1
    postdoc_signal = next(s for s in signals if s.detected_value == "postdoctoral")
    assert postdoc_signal.source_field in {"name", "description"}
    assert "postdoc" in postdoc_signal.text_excerpt.lower()
    assert postdoc_signal.confidence == EvidenceConfidence.HIGH


def test_11_original_scholarship_data_remains_unchanged() -> None:
    session = make_session()
    original_reqs = [{"field": "age", "operator": "min", "value": 18, "requirement_type": "hard"}]
    scholarship = Scholarship(
        id=111,
        name="PhD Fellowship in Renewable Energy",
        provider="Energy Institute",
        requirements=list(original_reqs),
        legacy_metadata={"raw_fields": {"education_level": "Any"}},
        data_quality="complete",
        fingerprint="audit-unchanged-111",
    )
    session.add(scholarship)
    session.commit()

    # Run matching and recommendations
    student = {"education_level": "undergraduate"}
    matcher = SoftMatchingService(session)
    result = matcher.evaluate(student, scholarship)
    assert result.hard_eligibility_status == "NOT_ELIGIBLE"

    # Verify scholarship in database is not mutated
    db_scholarship = session.get(Scholarship, 111)
    assert db_scholarship is not None
    assert db_scholarship.requirements == original_reqs
    assert db_scholarship.name == "PhD Fellowship in Renewable Energy"
    assert db_scholarship.legacy_metadata["raw_fields"]["education_level"] == "Any"


def test_12_synthetic_scholarships_remain_excluded_from_production() -> None:
    session = make_session()
    # Synthetic test fixture
    syn = Scholarship(
        id=1,
        name="SYNTHETIC TEST DATA - Future Scholars Grant",
        provider="Example Foundation",
        requirements=[],
        legacy_metadata={},
        data_quality="needs_review",
        fingerprint="syn-test-12",
    )
    # Real scholarship
    real = Scholarship(
        id=2,
        name="Undergraduate STEM Award",
        provider="Real Foundation",
        requirements=[],
        legacy_metadata={},
        data_quality="complete",
        fingerprint="real-test-12",
    )
    session.add_all([syn, real])
    session.add(
        ScholarshipSource(
            scholarship_id=syn.id,
            source_name="Synthetic fixture",
            source_type="dataset",
            verification_status="unverified",
        )
    )
    session.commit()

    service = RecommendationService(session, include_synthetic=False)
    response = service.generate({"education_level": "undergraduate"}, limit=5)
    rec_ids = [r.scholarship_id for r in response.recommendations]
    assert 1 not in rec_ids
    assert 2 in rec_ids
    assert response.total_candidates == 1
