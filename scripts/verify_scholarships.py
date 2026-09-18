import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from app.db.base import initialize_database
from app.db.models import Scholarship
from app.db.session import SessionLocal
from app.verification.service import ScholarshipVerificationService


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a bounded batch using stored scholarship URLs")
    parser.add_argument("--limit", type=int, default=3)
    arguments = parser.parse_args()
    if arguments.limit < 1 or arguments.limit > 50:
        parser.error("--limit must be between 1 and 50")
    initialize_database()
    report = {"attempted": 0, "statuses": {}, "errors": []}
    with SessionLocal() as session:
        scholarships = session.scalars(select(Scholarship).where(Scholarship.official_source_url.is_not(None)).order_by(Scholarship.id).limit(arguments.limit)).all()
        service = ScholarshipVerificationService(session)
        for scholarship in scholarships:
            try:
                record = service.verify(scholarship)
                report["attempted"] += 1
                report["statuses"][record.verification_status] = report["statuses"].get(record.verification_status, 0) + 1
            except Exception as error:
                report["errors"].append(f"{scholarship.id}: {error}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()