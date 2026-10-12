import asyncio
import logging

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.rate_limit import FixedWindowRateLimiter
from app.schemas.llm import QueryRequest, QueryResponse
from app.services.llm_service import llm_service

router = APIRouter()
logger = logging.getLogger(__name__)
rate_limiter = FixedWindowRateLimiter(settings.GENERATE_RATE_LIMIT_PER_MINUTE)


@router.post("/generate", response_model=QueryResponse)
async def generate_response(request: QueryRequest) -> QueryResponse:
    retry_after = await rate_limiter.check()
    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="Generation request limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )

    try:
        answer = await llm_service.generate_response(request.query)
        return QueryResponse(answer=answer)
    except asyncio.TimeoutError as error:
        logger.warning("LLM response generation timed out")
        raise HTTPException(
            status_code=504, detail="Response generation timed out"
        ) from error
    except Exception as e:
        logger.error(
            "LLM response generation failed",
            extra={"error_type": type(e).__name__},
        )
        raise HTTPException(
            status_code=500, detail="Unable to generate response"
        ) from e
