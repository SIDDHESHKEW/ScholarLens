
from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.api import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="scholarmatch-api",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc),
    )