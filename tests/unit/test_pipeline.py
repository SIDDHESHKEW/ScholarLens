from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import Scholarship, ScholarshipSource
from app.pipeline.ingestion.pipeline import ScholarshipIngestionPipeline, raw_record_from_mapping


def make_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_pipeline_upserts_and_preserves_provenance() -> None:
    session = make_session()
    payload = {
        "name": "SYNTHETIC TEST DATA - Grant",
        "provider": "Synthetic Provider",
        "official_source_url": "https://example.org/grant",
        "deadline": "2026-12-31",
        "requirements": [],
    }
    record = raw_record_from_mapping(
        payload, source_name="Synthetic fixture", source_type="dataset"
    )
    first = ScholarshipIngestionPipeline(session).process([record])
    second = ScholarshipIngestionPipeline(session).process([record])

    assert first.records_inserted == 1
    assert second.records_updated == 1
    assert session.query(Scholarship).count() == 1
    assert session.query(ScholarshipSource).count() == 2
    assert second.duplicates_detected == 1