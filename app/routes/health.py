from fastapi import APIRouter, HTTPException

from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/ready")
async def readiness() -> dict[str, str]:
    if not settings.VERTEX_AI_MODEL or not settings.VERTEX_AI_LOCATION:
        raise HTTPException(status_code=503, detail="Service is not configured")
    return {"status": "ready"}
