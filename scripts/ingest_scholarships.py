import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.base import initialize_database
from app.db.session import SessionLocal
from app.pipeline.ingestion.pipeline import ScholarshipIngestionPipeline, raw_record_from_mapping


def load_records(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as source_file:
        payload = json.load(source_file)
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise ValueError("source extract must be a JSON array of objects")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest a controlled scholarship JSON extract")
    parser.add_argument("path", type=Path)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-type", default="unknown")
    parser.add_argument("--source-url")
    arguments = parser.parse_args()

    initialize_database()
    records = [
        raw_record_from_mapping(
            payload,
            source_name=arguments.source_name,
            source_type=arguments.source_type,
            source_url=arguments.source_url,
        )
        for payload in load_records(arguments.path)
    ]
    with SessionLocal() as session:
        report = ScholarshipIngestionPipeline(session).process(records)
    print(json.dumps(report.__dict__, default=str, indent=2))


if __name__ == "__main__":
    main()