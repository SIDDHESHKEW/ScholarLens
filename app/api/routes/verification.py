from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.db.models import Scholarship, VerificationClaim, VerificationEvidence, VerificationRecord
from app.verification.schemas import VerificationClaimRead, VerificationEvidenceRead, VerificationRead

router = APIRouter(prefix="/scholarships", tags=["verification"])


def serialize(record: VerificationRecord, db: Session) -> VerificationRead:
    claims = db.scalars(select(VerificationClaim).where(VerificationClaim.verification_id == record.id)).all()
    evidence = db.scalars(select(VerificationEvidence).where(VerificationEvidence.verification_id == record.id)).all()
    return VerificationRead(
        id=record.id, scholarship_id=record.scholarship_id,
        verification_status=record.verification_status, freshness_status=record.freshness_status,
        verifier_method=record.verifier_method, verified_at=record.verified_at, notes=record.notes,
        claims=[VerificationClaimRead.model_validate(item) for item in claims],
        evidence=[VerificationEvidenceRead.model_validate(item) for item in evidence],
    )


@router.get("/verification/queue", response_model=list[int])
def verification_queue(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)) -> list[int]:
    records = db.scalars(select(Scholarship).where(Scholarship.data_quality == "needs_review").order_by(Scholarship.id).limit(limit)).all()
    return [record.id for record in records]


@router.get("/{scholarship_id}/verification", response_model=VerificationRead)
def latest_verification(scholarship_id: int, db: Session = Depends(get_db)) -> VerificationRead:
    record = db.scalar(select(VerificationRecord).where(VerificationRecord.scholarship_id == scholarship_id).order_by(VerificationRecord.verified_at.desc()))
    if record is None:
        raise HTTPException(status_code=404, detail="Verification has not been attempted")
    return serialize(record, db)


@router.get("/{scholarship_id}/verification/history", response_model=list[VerificationRead])
def verification_history(scholarship_id: int, db: Session = Depends(get_db)) -> list[VerificationRead]:
    records = db.scalars(select(VerificationRecord).where(VerificationRecord.scholarship_id == scholarship_id).order_by(VerificationRecord.verified_at.desc())).all()
    return [serialize(record, db) for record in records]

