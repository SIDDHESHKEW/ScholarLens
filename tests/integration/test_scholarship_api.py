from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.dependencies import get_db
from app.main import app
from app.pipeline.ingestion.pipeline import ScholarshipIngestionPipeline, raw_record_from_mapping


def test_scholarship_api_reads_records_and_404s() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        ScholarshipIngestionPipeline(session).process(
            [
                raw_record_from_mapping(
                    {
                        "name": "SYNTHETIC TEST DATA - API Grant",
                        "provider": "Synthetic Provider",
                        "official_source_url": "https://example.org/api-grant",
                    },
                    source_name="Synthetic fixture",
                    source_type="dataset",
                )
            ]
        )

        def override_db():
            yield session

        app.dependency_overrides[get_db] = override_db
        try:
            with TestClient(app) as client:
                response = client.get("/api/v1/scholarships")
                detail = client.get("/api/v1/scholarships/1")
                missing = client.get("/api/v1/scholarships/999")
        finally:
            app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["name"].startswith("SYNTHETIC TEST DATA")
    assert detail.status_code == 200
    assert detail.json()["provenance"][0]["source_name"] == "Synthetic fixture"
    assert missing.status_code == 404