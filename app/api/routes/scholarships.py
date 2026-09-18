from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.db.models import ScholarshipSource
from app.repositories.scholarship_repository import ScholarshipRepository
from app.schemas.scholarship import ScholarshipRead, ScholarshipSourceRead

router = APIRouter(prefix="/scholarships", tags=["scholarships"])


def to_schema(scholarship: object, session: Session) -> ScholarshipRead:
    sources = session.scalars(
        select(ScholarshipSource)
        .where(ScholarshipSource.scholarship_id == scholarship.id)
        .order_by(ScholarshipSource.id)
    ).all()
    return ScholarshipRead(
        id=scholarship.id,
        name=scholarship.name,
        provider=scholarship.provider,
        description=scholarship.description,
        official_source_url=scholarship.official_source_url,
        application_url=scholarship.application_url,
        amount=scholarship.amount,
        currency=scholarship.currency,
        deadline=scholarship.deadline,
        status=scholarship.status,
        requirements=scholarship.requirements,
        eligibility_evidence=scholarship.eligibility_evidence,
        legacy_metadata=scholarship.legacy_metadata,
        source_record_id=scholarship.source_record_id,
        created_at=scholarship.created_at,
        updated_at=scholarship.updated_at,
        source_status=scholarship.source_status,
        status_derived=scholarship.status_derived,
        data_quality=scholarship.data_quality,
        quality_issues=scholarship.quality_issues or [],
        provenance=[ScholarshipSourceRead.model_validate(source) for source in sources],
    )


@router.get("", response_model=list[ScholarshipRead])
def list_scholarships(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ScholarshipRead]:
    repository = ScholarshipRepository(db)
    return [to_schema(item, db) for item in repository.list(skip=skip, limit=limit)]


@router.get("/{scholarship_id}", response_model=ScholarshipRead)
def get_scholarship(scholarship_id: int, db: Session = Depends(get_db)) -> ScholarshipRead:
    scholarship = ScholarshipRepository(db).get(scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    return to_schema(scholarship, db)