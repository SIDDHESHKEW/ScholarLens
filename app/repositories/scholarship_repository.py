from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Scholarship, ScholarshipSource


class ScholarshipRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self, skip: int = 0, limit: int = 100) -> Sequence[Scholarship]:
        return self.session.scalars(
            select(Scholarship).order_by(Scholarship.id).offset(skip).limit(limit)
        ).all()

    def list_candidates(self, include_synthetic: bool = False) -> Sequence[Scholarship]:
        if include_synthetic:
            return self.session.scalars(select(Scholarship).order_by(Scholarship.id)).all()

        synthetic_source_ids = select(ScholarshipSource.scholarship_id).where(
            func.lower(ScholarshipSource.source_name).like("%synthetic%")
            | func.lower(ScholarshipSource.source_name).like("%fixture%")
            | func.lower(ScholarshipSource.source_type).in_(["synthetic", "test", "fixture"])
        )
        query = select(Scholarship).where(
            ~Scholarship.id.in_(synthetic_source_ids),
            ~Scholarship.name.like("SYNTHETIC TEST DATA%"),
        ).order_by(Scholarship.id)
        candidates = self.session.scalars(query).all()
        return [
            s for s in candidates
            if not (
                s.legacy_metadata
                and (
                    s.legacy_metadata.get("is_test")
                    or s.legacy_metadata.get("is_synthetic")
                    or s.legacy_metadata.get("source_dataset") == "synthetic"
                )
            )
        ]

    def get(self, scholarship_id: int) -> Scholarship | None:
        return self.session.get(Scholarship, scholarship_id)

    def find_by_fingerprint(self, value: str) -> Scholarship | None:
        return self.session.scalar(select(Scholarship).where(Scholarship.fingerprint == value))

    def save(self, scholarship: Scholarship) -> Scholarship:
        self.session.add(scholarship)
        self.session.flush()
        return scholarship

    def add_source(self, source: ScholarshipSource) -> ScholarshipSource:
        self.session.add(source)
        self.session.flush()
        return source