from pydantic import BaseModel, Field

from app.config import settings


class QueryRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=settings.MAX_PROMPT_CHARACTERS,
    )


class QueryResponse(BaseModel):
    answer: str
