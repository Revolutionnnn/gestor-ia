from fastapi import APIRouter

from ..config import SERVICE_NAME

router = APIRouter()


@router.get("", summary="Health check")
def health_check():
    return {"service": SERVICE_NAME, "status": "ok"}
