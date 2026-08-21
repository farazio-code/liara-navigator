from fastapi import APIRouter

from app.api.schemas import LivenessResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live", response_model=LivenessResponse)
async def liveness() -> LivenessResponse:
    return LivenessResponse()
