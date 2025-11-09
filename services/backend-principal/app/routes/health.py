from datetime import datetime

from fastapi import APIRouter

from ..schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="backend-principal",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat() + "Z",
        dependencies={"database": "ok", "ia_service": "ok"},
    )
