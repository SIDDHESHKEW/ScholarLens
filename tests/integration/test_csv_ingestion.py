from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import RawScholarshipRecord, Scholarship, ScholarshipSource
from app.pipeline.acquisition.csv_adapter import ScholarshipCSVAdapter
from app.pipeline.ingestion.pipeline import ScholarshipIngestionPipeline


def test_csv_ingestion_is_repeatable_and_preserves_provenance() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    records, _ = ScholarshipCSVAdapter("data/clean_scholarships.csv").read()
    with Session(engine) as session:
        first = ScholarshipIngestionPipeline(session).process(records[:3])
        second = ScholarshipIngestionPipeline(session).process(records[:3])
        assert first.records_inserted == 3
        assert second.records_updated == 3
        assert session.query(Scholarship).count() == 3
        assert session.query(ScholarshipSource).count() == 6
        assert session.query(RawScholarshipRecord).count() == 6
        scholarship = session.scalar(select(Scholarship).order_by(Scholarship.id))
        assert scholarship.source_record_id == "SCH_0001"
        assert scholarship.legacy_metadata["source_dataset"] == "clean_scholarships.csv"
        assert scholarship.eligibility_evidence["eligibility_criteria"]["parsing_status"] == "UNPARSED"