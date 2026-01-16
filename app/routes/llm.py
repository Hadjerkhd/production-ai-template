from fastapi import APIRouter, HTTPException

from app.schemas.llm import QueryRequest, QueryResponse
from app.services.llm_service import llm_service

router = APIRouter()


@router.post("/generate", response_model=QueryResponse)
async def generate_response(request: QueryRequest) -> QueryResponse:
    try:
        answer = await llm_service.generate_response(request.query)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
