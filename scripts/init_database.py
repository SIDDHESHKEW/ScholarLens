"""Database initialization and canonical dataset ingestion script for ScholarMatch.

Creates all database tables and ingests the tracked scholarship dataset
(data/clean_scholarships.csv) into the SQLite database.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select
from app.db.base import Base, engine, initialize_database
from app.db.models import Scholarship, ScholarshipSource
from app.db.session import SessionLocal
from app.pipeline.acquisition.csv_adapter import ScholarshipCSVAdapter
from app.pipeline.ingestion.pipeline import ScholarshipIngestionPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def init_db(
    csv_path: Path = Path("data/clean_scholarships.csv"),
    reset: bool = False,
) -> dict:
    """Initialize database tables and ingest canonical scholarship CSV."""
    if reset:
        logger.info("Reset requested: dropping all existing tables...")
        Base.metadata.drop_all(bind=engine)

    logger.info("Initializing database schema...")
    initialize_database()

    if not csv_path.exists():
        raise FileNotFoundError(f"Canonical dataset not found at: {csv_path}")

    logger.info("Ingesting scholarship dataset from: %s", csv_path)
    adapter = ScholarshipCSVAdapter(csv_path)
    records, csv_report = adapter.read()
    logger.info("CSV parsed: %d records found (%d skipped)", csv_report.records_seen, csv_report.records_skipped)

    with SessionLocal() as session:
        pipeline = ScholarshipIngestionPipeline(session)
        report = pipeline.process(records)

    with SessionLocal() as session:
        total_scholarships = session.scalar(select(func.count(Scholarship.id))) or 0
        quality_counts = dict(
            session.execute(
                select(Scholarship.data_quality, func.count(Scholarship.id)).group_by(Scholarship.data_quality)
            ).all()
        )
        sources_count = session.scalar(select(func.count(ScholarshipSource.id))) or 0

    summary = {
        "status": "success",
        "csv_source": str(csv_path),
        "records_seen": csv_report.records_seen,
        "records_skipped": csv_report.records_skipped,
        "records_cleaned": report.records_cleaned,
        "records_normalized": report.records_normalized,
        "records_inserted": report.records_inserted,
        "records_updated": report.records_updated,
        "duplicates_detected": report.duplicates_detected,
        "total_scholarships_in_db": total_scholarships,
        "total_sources_tracked": sources_count,
        "data_quality_breakdown": quality_counts,
        "synthetic_records_created": 0,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize ScholarMatch SQLite database and ingest canonical dataset."
    )
    parser.add_argument(
        "--csv-path",
        type=Path,
        default=Path("data/clean_scholarships.csv"),
        help="Path to scholarship CSV dataset (default: data/clean_scholarships.csv)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate all database tables before ingestion",
    )
    args = parser.parse_args()

    try:
        summary = init_db(csv_path=args.csv_path, reset=args.reset)
        print("\n================ SCHOLARMATCH DATABASE INITIALIZATION ================")
        print(json.dumps(summary, indent=2))
        print("======================================================================\n")
    except Exception as exc:
        logger.error("Database initialization failed: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
