import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import initialize_database
from app.db.session import SessionLocal
from app.pipeline.acquisition.csv_adapter import ScholarshipCSVAdapter
from app.pipeline.ingestion.pipeline import ScholarshipIngestionPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a scholarship CSV through the Phase 2 pipeline")
    parser.add_argument("path", type=Path)
    arguments = parser.parse_args()

    initialize_database()
    records, csv_report = ScholarshipCSVAdapter(arguments.path).read()
    with SessionLocal() as session:
        report = ScholarshipIngestionPipeline(session).process(records)
    report.records_seen = csv_report.records_seen
    report.records_skipped = csv_report.records_skipped
    report.errors = csv_report.errors + report.errors
    print(json.dumps(asdict(report), indent=2, default=str))


if __name__ == "__main__":
    main()